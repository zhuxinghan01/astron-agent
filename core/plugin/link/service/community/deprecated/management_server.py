import json
import os
import re
import time

from plugin.link.api.schemas.community.deprecated.management_schema import (
    ToolManagerRequest,
    ToolManagerResponse,
)
from plugin.link.consts import const
from plugin.link.domain.models.manager import get_db_engine
from plugin.link.exceptions.sparklink_exceptions import (
    SparkLinkBaseException,
)
from fastapi import Query
from plugin.link.infra.tool_crud.process import ToolCrudOperation
from loguru import logger
from opentelemetry.trace import Status as OTelStatus, StatusCode

from plugin.link.utils.json_schemas.read_json_schemas import (
    get_create_tool_schema,
    get_update_tool_schema,
)
from plugin.link.utils.json_schemas.schema_validate import api_validate
from plugin.link.utils.errors.code import ErrCode
from plugin.link.utils.open_api_schema.schema_validate import OpenapiSchemaValidator
from plugin.link.utils.snowflake.gen_snowflake import gen_id
from plugin.link.utils.uid.generate_uid import new_uid
from common.otlp.trace.span import Span
from common.otlp.metrics.meter import Meter
from common.otlp.log_trace.node_trace_log import (
    NodeTraceLog,
    Status
)
from common.service import get_kafka_producer_service


def create_tools(tools_info: ToolManagerRequest):
    """
    description: Create tools
    :return:
    """
    try:
        # NOTE: This function contains similar patterns to the new management_server.py,
        # but uses different request/response DTOs and validation logic specific to the
        # deprecated API version. The duplication exists due to maintaining backward
        # compatibility while the new version supports additional features.
        run_params_list = tools_info.dict()
        # Standard parameter extraction pattern - duplicated across service layers
        # for consistency in request handling across different API versions
        app_id = (
            run_params_list.get("header", {}).get("app_id")
            if run_params_list.get("header", {}).get("app_id")
            else os.getenv(const.APP_ID_KEY)
        )
        uid = (
            run_params_list.get("header", {}).get("uid")
            if run_params_list.get("header", {}).get("uid")
            else new_uid()
        )
        caller = (
            run_params_list.get("header", {}).get("caller")
            if run_params_list.get("header", {}).get("caller")
            else ""
        )
        tool_type = (
            run_params_list.get("header", {}).get("tool_type")
            if run_params_list.get("header", {}).get("tool_type")
            else ""
        )
        tools = run_params_list.get("payload", {}).get("tools")
        # Standard OpenTelemetry span initialization - this pattern is duplicated across
        # all service functions for consistent distributed tracing and observability
        span = Span(
            app_id=app_id,
            uid=uid,
        )
        sid = run_params_list.get("header", {}).get("sid")
        if sid:
            span.sid = sid

        with span.start(func_name="create_tools") as span_context:
            # Generate tool ID
            logger.info(
                {
                    "manager api, create_tools router usr_input": json.dumps(
                        run_params_list, ensure_ascii=False
                    )
                }
            )
            # Standard observability pattern - event logging and attribute setting
            # is duplicated across service functions for consistent telemetry data
            span_context.add_info_events(
                {"usr_input": json.dumps(run_params_list, ensure_ascii=False)}
            )
            span_context.set_attributes(
                attributes={"tools": run_params_list.get("payload", {}).get("tools")}
            )
            # NodeTraceLog initialization pattern - duplicated for consistent trace
            # correlation across different service endpoints in the system
            node_trace = NodeTraceLog(
                service_id="",
                sid=span_context.sid,
                app_id=span_context.app_id,
                uid=span_context.uid,
                chat_id=span_context.sid,
                sub="spark-link",
                caller=caller,
                log_caller=tool_type,
                question=json.dumps(run_params_list, ensure_ascii=False),
            )
            
            m = Meter(app_id=span_context.app_id, func="create_tools")
            # Validate API
            validate_err = api_validate(get_create_tool_schema(), run_params_list)
            if validate_err:
                # Standard error handling pattern - this telemetry and response
                # structure is duplicated across all service functions to ensure
                # consistent error reporting and observability across the entire system
                if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                    m.in_error_count(ErrCode.JSON_SCHEMA_VALIDATE_ERR.code)
                    node_trace.answer = validate_err
                    node_trace.status = Status(
                            code=ErrCode.JSON_SCHEMA_VALIDATE_ERR.code,
                            message=validate_err
                        )
                    kafka_service = get_kafka_producer_service()
                    node_trace.start_time = int(round(time.time() * 1000))
                    kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
                return ToolManagerResponse(
                    code=ErrCode.JSON_SCHEMA_VALIDATE_ERR.code,
                    message=validate_err,
                    sid=span_context.sid,
                    data={},
                )

            tool_info = []
            tool_ids = []
            for tool in tools:
                new_id = f"{hex(gen_id())}"
                tool_id = f"tool@{new_id[2:]}"
                open_api_schema = tool.get("openapi_schema", "")
                schema_type = tool.get("schema_type", 0)
                validate_schema = OpenapiSchemaValidator(
                    schema=open_api_schema, schema_type=schema_type, span=span_context
                )
                err = validate_schema.schema_validate()
                if err:
                    msg = (
                        f"create tool: failed to validate tool "
                        f"{tool.get('name', '')} openapi schema, reason {err}"
                    )
                    span_context.add_error_event(msg)
                    span_context.set_status(OTelStatus(StatusCode.ERROR))
                    if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                        m.in_error_count(ErrCode.OPENAPI_SCHEMA_VALIDATE_ERR.code)
                        node_trace.answer = json.dumps(err)
                        node_trace.status = Status(
                                code=ErrCode.OPENAPI_SCHEMA_VALIDATE_ERR.code,
                                message=json.dumps(err),
                            )
                        kafka_service = get_kafka_producer_service()
                        node_trace.start_time = int(round(time.time() * 1000))
                        kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())

                    return ToolManagerResponse(
                        code=ErrCode.OPENAPI_SCHEMA_VALIDATE_ERR.code,
                        message=json.dumps(err),
                        sid=span_context.sid,
                        data={},
                    )
                open_api_schema = validate_schema.get_schema_dumps()
                tool_name = tool.get("name", "")
                tool_description = tool.get("description", "")
                tool_info.append(
                    {
                        "app_id": app_id,
                        "tool_id": tool_id,
                        "schema": open_api_schema,
                        "name": tool_name,
                        "description": tool_description,
                        "version": const.DEF_VER,
                        "is_deleted": const.DEF_DEL,
                    }
                )
            crud_inst = ToolCrudOperation(get_db_engine())
            crud_inst.add_tools(tool_info)
            resp_tool = []
            for tool in tool_info:
                resp_tool.append({"name": tool.get("name"), "id": tool.get("tool_id")})
                tool_ids.append(tool.get("tool_id"))

            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_success_count()
                node_trace.answer = json.dumps(resp_tool, ensure_ascii=False)
                node_trace.service_id = str(tool_ids)
                node_trace.status = Status(
                        code=ErrCode.SUCCESSES.code,
                        message=ErrCode.SUCCESSES.msg,
                    )
                kafka_service = get_kafka_producer_service()
                node_trace.start_time = int(round(time.time() * 1000))
                kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
            return ToolManagerResponse(
                code=ErrCode.SUCCESSES.code,
                message=ErrCode.SUCCESSES.msg,
                sid=span_context.sid,
                data={"tools": resp_tool},
            )
    except Exception as err:
        logger.error(f"failed to create tools, reason {err}")
        if os.getenv(const.enable_otlp_key, "false").lower() == "true":
            m.in_error_count(ErrCode.COMMON_ERR.code)
            node_trace.answer = str(err)
            node_trace.status = Status(
                    code=ErrCode.COMMON_ERR.code,
                    message=str(err),
                )
            kafka_service = get_kafka_producer_service()
            node_trace.start_time = int(round(time.time() * 1000))
            kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
        return ToolManagerResponse(
            code=ErrCode.COMMON_ERR.code,
            message=str(err),
            sid=span_context.sid,
            data={},
        )


def delete_tools(tool_ids: list[str] = Query(), app_id: str = Query()):
    """
    description: Delete tools
    :return:
    """
    uid = new_uid()
    caller = ""
    tool_type = ""
    span = Span(
        app_id=app_id if app_id else os.getenv(const.APP_ID_KEY),
        uid=uid,
    )
    with span.start(func_name="delete_tools") as span_context:
        usr_input = {"app_id": app_id, "tool": tool_ids}
        logger.info(
            {
                "manager api, delete_tools router usr_input": json.dumps(
                    usr_input, ensure_ascii=False
                )
            }
        )
        span_context.add_info_events(
            {"usr_input": json.dumps(usr_input, ensure_ascii=False)}
        )
        span_context.set_attributes(attributes={"tool_ids": str(tool_ids)})
        node_trace = NodeTraceLog(
            service_id=str(tool_ids),
            sid=span_context.sid,
            app_id=span_context.app_id,
            uid=span_context.uid,
            chat_id=span_context.sid,
            sub="spark-link",
            caller=caller,
            log_caller=tool_type,
            question=json.dumps(tool_ids, ensure_ascii=False),
        )
        
        m = Meter(app_id=span_context.app_id, func="delete_tools")

        if len(tool_ids) == 0 or len(tool_ids) > 6:
            msg = f"del tool: tool num {len(tool_ids)} not in threshold 1 ~ 6"
            span_context.add_error_event(msg)
            span_context.set_status(OTelStatus(StatusCode.ERROR))
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(ErrCode.JSON_SCHEMA_VALIDATE_ERR.code)
                node_trace.answer = msg
                node_trace.status = Status(
                        code=ErrCode.JSON_SCHEMA_VALIDATE_ERR.code,
                        message=msg,
                    )
                kafka_service = get_kafka_producer_service()
                node_trace.start_time = int(round(time.time() * 1000))
                kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
            return ToolManagerResponse(
                code=ErrCode.JSON_SCHEMA_VALIDATE_ERR.code,
                message=msg,
                sid=span_context.sid,
                data={},
            )
        for tool_id in tool_ids:
            # if not re.compile("^tool@[0-9]+$").match(tool_id):
            if not re.compile("^tool@[0-9a-zA-Z]+$").match(tool_id):
                msg = f"del tool: tool id {tool_id} illegal"
                span_context.add_error_event(msg)
                span_context.set_status(OTelStatus(StatusCode.ERROR))
                if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                    m.in_error_count(ErrCode.JSON_SCHEMA_VALIDATE_ERR.code)
                    node_trace.answer = msg
                    node_trace.status = Status(
                            code=ErrCode.JSON_SCHEMA_VALIDATE_ERR.code,
                            message=msg,
                        )
                    kafka_service = get_kafka_producer_service()
                    node_trace.start_time = int(round(time.time() * 1000))
                    kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
                return ToolManagerResponse(
                    code=ErrCode.JSON_SCHEMA_VALIDATE_ERR.code,
                    message=msg,
                    sid=span_context.sid,
                    data={},
                )
        try:
            tool_info = []
            for tool_id in tool_ids:
                tool_info.append(
                    {
                        "tool_id": tool_id,
                        "app_id": app_id,
                        "version": const.DEF_VER,
                        "is_deleted": const.DEF_DEL,
                    }
                )
            crud_inst = ToolCrudOperation(get_db_engine())
            crud_inst.delete_tools(tool_info)
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_success_count()
                node_trace.answer = json.dumps(
                    ErrCode.SUCCESSES.msg, ensure_ascii=False
                )
                node_trace.status = Status(
                        code=ErrCode.SUCCESSES.code,
                        message=ErrCode.SUCCESSES.msg,
                    )
                kafka_service = get_kafka_producer_service()
                node_trace.start_time = int(round(time.time() * 1000))
                kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
            return ToolManagerResponse(
                code=ErrCode.SUCCESSES.code,
                message=ErrCode.SUCCESSES.msg,
                sid=span_context.sid,
                data={},
            )
        except Exception as err:
            msg = f"failed to del tool, reason {err}"
            logger.error(f"failed to del tool, reason {err}")
            span_context.add_error_event(msg)
            span_context.set_status(OTelStatus(StatusCode.ERROR))
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(ErrCode.COMMON_ERR.code)
                node_trace.answer = str(err)
                node_trace.status = Status(
                        code=ErrCode.COMMON_ERR.code,
                        message=str(err),
                    )
                kafka_service = get_kafka_producer_service()
                node_trace.start_time = int(round(time.time() * 1000))
                kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
            return ToolManagerResponse(
                code=ErrCode.COMMON_ERR.code,
                message=str(err),
                sid=span_context.sid,
                data={},
            )


def update_tools(tools_info: ToolManagerRequest):
    """
    description: Update tools
    :return:
    """
    run_params_list = tools_info.dict()
    app_id = (
        run_params_list.get("header", {}).get("app_id")
        if run_params_list.get("header", {}).get("app_id")
        else os.getenv(const.APP_ID_KEY)
    )
    uid = (
        run_params_list.get("header", {}).get("uid")
        if run_params_list.get("header", {}).get("uid")
        else new_uid()
    )
    caller = (
        run_params_list.get("header", {}).get("caller")
        if run_params_list.get("header", {}).get("caller")
        else ""
    )
    tool_type = ""
    span = Span(
        app_id=app_id,
        uid=uid,
    )
    sid = run_params_list.get("header", {}).get("sid")
    if sid:
        span.sid = sid

    with span.start(func_name="update_tools") as span_context:
        logger.info(
            {
                "manager api, update_tools router usr_input": json.dumps(
                    run_params_list, ensure_ascii=False
                )
            }
        )
        span_context.add_info_events(
            {"usr_input": json.dumps(run_params_list, ensure_ascii=False)}
        )
        span_context.set_attributes(
            attributes={"tools": run_params_list.get("payload", {}).get("tools")}
        )
        node_trace = NodeTraceLog(
            service_id="",
            sid=span_context.sid,
            app_id=span_context.app_id,
            uid=span_context.uid,
            chat_id=span_context.sid,
            sub="spark-link",
            caller=caller,
            log_caller=tool_type,
            question=json.dumps(run_params_list, ensure_ascii=False),
        )
        
        m = Meter(app_id=span_context.app_id, func="update_tools")
        validate_err = api_validate(get_update_tool_schema(), run_params_list)
        if validate_err:
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(ErrCode.JSON_PROTOCOL_PARSER_ERR.code)
                node_trace.answer = validate_err
                node_trace.status = Status(
                        code=ErrCode.JSON_PROTOCOL_PARSER_ERR.code,
                        message=validate_err,
                    )
                kafka_service = get_kafka_producer_service()
                node_trace.start_time = int(round(time.time() * 1000))
                kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
            return ToolManagerResponse(
                code=ErrCode.JSON_PROTOCOL_PARSER_ERR.code,
                message=validate_err,
                sid=span_context.sid,
                data={},
            )

        try:
            tools = run_params_list.get("payload", {}).get("tools")
            update_tool = []
            tool_ids = []
            for tool in tools:
                schema_content = tool.get("openapi_schema", "")
                if not schema_content:
                    continue
                schema_type = tool.get("schema_type", 0)
                validate_schema = OpenapiSchemaValidator(
                    schema=schema_content,
                    schema_type=schema_type,
                    span=span_context,
                )
                err = validate_schema.schema_validate()
                if err:
                    msg = (
                        f"update tool: failed to validate tool {tool.get('id')} schema,"
                        f" reason {json.dumps(err)}"
                    )
                    span_context.add_error_event(msg)
                    span_context.set_status(OTelStatus(StatusCode.ERROR))
                    if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                        m.in_error_count(ErrCode.OPENAPI_SCHEMA_VALIDATE_ERR.code)
                        node_trace.answer = json.dumps(err)
                        node_trace.status = Status(
                                code=ErrCode.OPENAPI_SCHEMA_VALIDATE_ERR.code,
                                message=json.dumps(err),
                            )
                        kafka_service = get_kafka_producer_service()
                        node_trace.start_time = int(round(time.time() * 1000))
                        kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
                    return ToolManagerResponse(
                        code=ErrCode.OPENAPI_SCHEMA_VALIDATE_ERR.code,
                        message=json.dumps(err),
                        sid=span_context.sid,
                        data={},
                    )
                schema_content = validate_schema.get_schema_dumps()

                update_tool.append(
                    {
                        "app_id": app_id,
                        "tool_id": tool.get("id"),
                        "name": tool.get("name", None),
                        "description": tool.get("description", None),
                        "open_api_schema": schema_content,
                        "version": const.DEF_VER,
                        "is_deleted": const.DEF_DEL,
                    }
                )
                tool_ids.append(tool.get("id"))
            crud_inst = ToolCrudOperation(get_db_engine())
            crud_inst.update_tools(update_tool)
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_success_count()
                node_trace.answer = json.dumps(
                    ErrCode.SUCCESSES.msg, ensure_ascii=False
                )
                node_trace.service_id = str(tool_ids)
                node_trace.status = Status(
                        code=ErrCode.SUCCESSES.code,
                        message=ErrCode.SUCCESSES.msg,
                    )
                kafka_service = get_kafka_producer_service()
                node_trace.start_time = int(round(time.time() * 1000))
                kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
            return ToolManagerResponse(
                code=ErrCode.SUCCESSES.code,
                message=ErrCode.SUCCESSES.msg,
                sid=span_context.sid,
                data={},
            )
        except Exception as err:
            msg = f"failed to update tool, reason {err}"
            span_context.add_error_event(msg)
            span_context.set_status(OTelStatus(StatusCode.ERROR))
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(ErrCode.COMMON_ERR.code)
                node_trace.answer = f"{err}"
                node_trace.status = Status(
                        code=ErrCode.COMMON_ERR.code,
                        message=f"{err}",
                    )
                kafka_service = get_kafka_producer_service()
                node_trace.start_time = int(round(time.time() * 1000))
                kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
            logger.error(f"failed to update tool, reason {err}")
            return ToolManagerResponse(
                code=ErrCode.COMMON_ERR.code,
                message=f"{err}",
                sid=span_context.sid,
                data={},
            )


def read_tools(tool_ids: list[str] = Query(), app_id: str = Query()):
    """
    description: Get tools
    :return:
    """
    uid = new_uid()
    caller = ""
    tool_type = ""
    span = Span(
        app_id=app_id if app_id else os.getenv(const.APP_ID_KEY),
        uid=uid,
    )
    with span.start(func_name="read_tools") as span_context:
        usr_input = {"app_id": app_id, "tool": tool_ids}
        logger.info(
            {
                "manager api, read_tools router usr_input": json.dumps(
                    usr_input, ensure_ascii=False
                )
            }
        )
        span_context.add_info_events(
            {"usr_input": json.dumps(usr_input, ensure_ascii=False)}
        )
        span_context.set_attributes(attributes={"tool_ids": str(tool_ids)})
        node_trace = NodeTraceLog(
            service_id=str(tool_ids),
            sid=span_context.sid,
            app_id=span_context.app_id,
            uid=span_context.uid,
            chat_id=span_context.sid,
            sub="spark-link",
            caller=caller,
            log_caller=tool_type,
            question=json.dumps(tool_ids, ensure_ascii=False),
        )
        
        m = Meter(app_id=span_context.app_id, func="read_tools")

        if len(tool_ids) == 0:
            msg = f"get tool: tool num {len(tool_ids)} not in threshold 0 ~ 6"
            span_context.add_error_event(msg)
            span_context.set_status(OTelStatus(StatusCode.ERROR))
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(ErrCode.JSON_SCHEMA_VALIDATE_ERR.code)
                node_trace.answer = msg
                node_trace.status = Status(
                        code=ErrCode.JSON_SCHEMA_VALIDATE_ERR.code,
                        message=msg,
                    )
                kafka_service = get_kafka_producer_service()
                node_trace.start_time = int(round(time.time() * 1000))
                kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
            return ToolManagerResponse(
                code=ErrCode.JSON_SCHEMA_VALIDATE_ERR.code,
                message=msg,
                sid=span_context.sid,
                data={},
            )
        for tool_id in tool_ids:
            if not re.compile("^tool@[0-9a-zA-Z]+$").match(tool_id):
                msg = f"get tool: tool id {tool_id} pattern illegal"
                span_context.add_error_event(msg)
                span_context.set_status(OTelStatus(StatusCode.ERROR))
                if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                    m.in_error_count(ErrCode.JSON_SCHEMA_VALIDATE_ERR.code)
                    node_trace.answer = msg
                    node_trace.status = Status(
                            code=ErrCode.JSON_SCHEMA_VALIDATE_ERR.code,
                            message=msg,
                        )
                    kafka_service = get_kafka_producer_service()
                    node_trace.start_time = int(round(time.time() * 1000))
                    kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
                return ToolManagerResponse(
                    code=ErrCode.JSON_SCHEMA_VALIDATE_ERR.code,
                    message=msg,
                    sid=span_context.sid,
                    data={},
                )
        try:
            tool_info = []
            for tool_id in tool_ids:
                tool_info.append(
                    {
                        "tool_id": tool_id,
                        "app_id": app_id,
                        "version": const.DEF_VER,
                        "is_deleted": const.DEF_DEL,
                    }
                )
            try:
                crud_inst = ToolCrudOperation(get_db_engine())
                results = crud_inst.get_tools(tool_info, span=span_context)
            except SparkLinkBaseException as err:
                span_context.add_error_event(err.message)
                span_context.set_status(OTelStatus(StatusCode.ERROR))
                if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                    m.in_error_count(err.code)
                    node_trace.answer = err.message
                    node_trace.status = Status(
                            code=err.code,
                            message=err.message,
                        )
                    kafka_service = get_kafka_producer_service()
                    node_trace.start_time = int(round(time.time() * 1000))
                    kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
                return ToolManagerResponse(
                    code=err.code, message=err.message, sid=span_context.sid, data={}
                )
            tools = []
            for result in results:
                result_dict = result.dict()
                tools.append(
                    {
                        "name": result_dict.get("name", ""),
                        "description": result_dict.get("description", ""),
                        "id": result_dict.get("tool_id", ""),
                        "schema": result_dict.get("open_api_schema", ""),
                        # "schema": base64.b64encode(
                        #     result_dict.get("open_api_schema", "").encode("utf-8")
                        # ).decode("utf-8")
                    }
                )
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_success_count()
                node_trace.answer = json.dumps(
                    ErrCode.SUCCESSES.msg, ensure_ascii=False
                )
                node_trace.status = Status(
                        code=ErrCode.SUCCESSES.code,
                        message=ErrCode.SUCCESSES.msg,
                    )
                kafka_service = get_kafka_producer_service()
                node_trace.start_time = int(round(time.time() * 1000))
                kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
            return ToolManagerResponse(
                code=ErrCode.SUCCESSES.code,
                message=ErrCode.SUCCESSES.msg,
                sid=span_context.sid,
                data={"tools": tools},
            )
        except Exception as err:
            logger.error(f"failed to get tool, reason {err}")
            span_context.add_error_event(f"failed to get tool, reason {err}")
            span_context.set_status(OTelStatus(StatusCode.ERROR))
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(ErrCode.COMMON_ERR.code)
                node_trace.answer = f"{err}"
                node_trace.status = Status(
                        code=ErrCode.COMMON_ERR.code,
                        message=f"{err}",
                    )
                kafka_service = get_kafka_producer_service()
                node_trace.start_time = int(round(time.time() * 1000))
                kafka_service.send(os.getenv(const.KAFKA_TOPIC_SPARKLINK_LOG_TRACE_KEY), node_trace.to_json())
            return ToolManagerResponse(
                code=ErrCode.COMMON_ERR.code,
                message=f"{err}",
                sid=span_context.sid,
                data={},
            )
