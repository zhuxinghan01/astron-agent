"""HTTP execution server for community tools.

This module provides HTTP execution capabilities for community tools, including
HTTP request execution, tool debugging, and OpenAPI schema validation.
It handles authentication, parameter validation, and response processing.
"""

import os
import json
import base64

from api.schemas.community.tools.http.execution_schema import (
    HttpRunRequest,
    HttpRunResponse,
    HttpRunResponseHeader,
    ToolDebugRequest,
    ToolDebugResponseHeader,
    ToolDebugResponse,
)
from consts import const
from domain.models.manager import get_db_engine, get_redis_engine
from exceptions.sparklink_exceptions import SparkLinkBaseException
from infra.tool_crud.process import ToolCrudOperation
from infra.tool_exector.process import HttpRun
from opentelemetry.trace import Status, StatusCode
from loguru import logger
from utils.uid.generate_uid import new_uid
from utils.errors.code import ErrCode
from utils.open_api_schema.schema_parser import OpenapiSchemaParser
from utils.json_schemas.read_json_schemas import (
    get_http_run_schema,
    get_tool_debug_schema,
)
from utils.json_schemas.schema_validate import api_validate
from xingchen_utils.otlp.trace.span import Span
from xingchen_utils.otlp.node_trace.node_trace import NodeTrace
from xingchen_utils.otlp.node_trace.node import TraceStatus
from xingchen_utils.otlp.metric.meter import Meter

default_value = {
    " 'string'": "",
    " 'number'": 0,
    " 'object'": {},
    " 'array'": [],
    " 'boolean'": False,
    " 'integer'": 0,
}


async def http_run(run_params: HttpRunRequest) -> HttpRunResponse:
    """
    http run with version
    """
    # NOTE: This function contains similar parameter extraction and span initialization
    # patterns as the management servers but in an HTTP execution context.
    # The duplication ensures consistent request handling patterns across all
    # service layers.
    run_params_list = run_params.model_dump(exclude_none=True)
    # Standard parameter extraction pattern - duplicated across service layers
    # for consistency in request handling across different service contexts
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
    span = Span(
        app_id=app_id,
        uid=uid,
    )
    sid = run_params_list.get("header", {}).get("sid")
    if sid:
        span.sid = sid

    with span.start(func_name="http_run") as span_context:
        logger.info(
            {
                "exec api, http_run router usr_input": json.dumps(
                    run_params_list, ensure_ascii=False
                )
            }
        )
        span_context.add_info_events(
            {"usr_input": json.dumps(run_params_list, ensure_ascii=False)}
        )
        span_context.set_attributes(
            attributes={
                "tool_id": run_params_list.get("parameter", {}).get("tool_id", {})
            }
        )
        node_trace = NodeTrace(
            flow_id="",
            sid=span_context.sid,
            app_id=span_context.app_id,
            uid=span_context.uid,
            bot_id="/tools/http_run",
            chat_id=span_context.sid,
            sub="spark-link",
            caller=caller,
            log_caller="",
            question=json.dumps(run_params_list, ensure_ascii=False),
        )
        node_trace.record_start()
        m = Meter(app_id=span_context.app_id, func="http_run")
        # Parameter validation
        validate_err = api_validate(get_http_run_schema(), run_params_list)
        if validate_err:
            # Standard error handling pattern - this telemetry and response structure
            # is duplicated across service functions to ensure consistent error
            # reporting and observability, adapted for HTTP execution context
            # with different response types
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(ErrCode.JSON_PROTOCOL_PARSER_ERR.code)
                node_trace.answer = validate_err
                node_trace.upload(
                    status=TraceStatus(
                        code=ErrCode.JSON_PROTOCOL_PARSER_ERR.code, message=validate_err
                    ),
                    log_caller="",
                    span=span_context,
                )
            return HttpRunResponse(
                header=HttpRunResponseHeader(
                    code=ErrCode.JSON_PROTOCOL_PARSER_ERR.code,
                    message=validate_err,
                    sid=span_context.sid,
                ),
                payload={},
            )

        tool_id = run_params_list["parameter"]["tool_id"]
        operation_id = run_params_list["parameter"]["operation_id"]
        version = run_params_list["parameter"].get("version", None)

        if version is None or version == "":
            version = const.DEF_VER

        tool_id_info = [
            {
                "app_id": run_params_list["header"]["app_id"],
                "tool_id": tool_id,
                "version": version,
                "is_deleted": const.DEF_DEL,
            }
        ]
        crud_inst = ToolCrudOperation(get_db_engine())
        try:
            query_results = crud_inst.get_tools(tool_id_info, span=span_context)
        except SparkLinkBaseException as err:
            span_context.add_error_event(err.message)
            span_context.set_status(Status(StatusCode.ERROR))
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(err.code)
                node_trace.answer = err.message
                node_trace.flow_id = tool_id
                node_trace.upload(
                    status=TraceStatus(code=err.code, message=err.message),
                    log_caller="",
                    span=span_context,
                )
            return HttpRunResponse(
                header=HttpRunResponseHeader(
                    code=err.code, message=err.message, sid=span_context.sid
                ),
                payload={},
            )
        if not query_results:
            message = f"{tool_id} does not exist"
            span_context.add_error_event(message)
            span_context.set_status(Status(StatusCode.ERROR))
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(ErrCode.TOOL_NOT_EXIST_ERR.code)
                node_trace.answer = message
                node_trace.flow_id = tool_id
                node_trace.upload(
                    status=TraceStatus(
                        code=ErrCode.TOOL_NOT_EXIST_ERR.code, message=message
                    ),
                    log_caller="",
                    span=span_context,
                )
            return HttpRunResponse(
                header=HttpRunResponseHeader(
                    code=ErrCode.TOOL_NOT_EXIST_ERR.code,
                    message=message,
                    sid=span_context.sid,
                ),
                payload={},
            )
        parser_result = {}
        for query_result in query_results:
            result_dict = query_result.dict()
            open_api_schema = json.loads(result_dict.get("open_api_schema"))
            tool_type = (
                os.getenv(const.OFFICIAL_TOOL_KEY)
                if open_api_schema.get("info").get("x-is-official")
                else os.getenv(const.THIRD_TOOL_KEY)
            )
            parser = OpenapiSchemaParser(open_api_schema, span=span_context)
            parser_result.update({result_dict["tool_id"]: parser.schema_parser()})
        tool_id_schema = parser_result[tool_id]
        operation_id_schema = tool_id_schema.get(operation_id, "")
        if not operation_id_schema:
            message = f"operation_id: {operation_id} does not exist"
            span_context.add_error_event(message)
            span_context.set_status(Status(StatusCode.ERROR))
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(ErrCode.OPERATION_ID_NOT_EXIST_ERR.code)
                node_trace.answer = message
                node_trace.flow_id = tool_id
                node_trace.log_caller = tool_type
                node_trace.upload(
                    status=TraceStatus(
                        code=ErrCode.OPERATION_ID_NOT_EXIST_ERR.code, message=message
                    ),
                    log_caller=tool_type,
                    span=span_context,
                )
            return HttpRunResponse(
                header=HttpRunResponseHeader(
                    code=ErrCode.OPERATION_ID_NOT_EXIST_ERR.code,
                    message=message,
                    sid=span_context.sid,
                ),
                payload={},
            )
        try:
            message = run_params_list["payload"]["message"]
            message_header = (
                json.loads(base64.b64decode(message.get("header")).decode("utf-8"))
                if message.get("header")
                else {}
            )
            message_query = (
                json.loads(base64.b64decode(message.get("query")).decode("utf-8"))
                if message.get("query")
                else {}
            )

            # Get authentication information from Redis
            if operation_id_schema["security"]:
                """
                api_key_info = {
                    "api_key": {
                        "type": "apiKey",
                        "name": "api_key",
                        "in": "header"
                    }
                }
                """
                security_type = operation_id_schema["security_type"]
                if security_type not in operation_id_schema["security"]:
                    span_context.add_error_event(
                        f"{ErrCode.OPENAPI_AUTH_TYPE_ERR.msg}"
                    )
                    span_context.set_status(Status(StatusCode.ERROR))
                    if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                        m.in_error_count(ErrCode.OPENAPI_AUTH_TYPE_ERR.code)
                        node_trace.answer = (
                            f"{ErrCode.OPENAPI_AUTH_TYPE_ERR.msg}"
                        )
                        node_trace.flow_id = tool_id
                        node_trace.log_caller = tool_type
                        node_trace.upload(
                            status=TraceStatus(
                                code=ErrCode.OPENAPI_AUTH_TYPE_ERR.code,
                                message=f"{ErrCode.OPENAPI_AUTH_TYPE_ERR.msg}",
                            ),
                            log_caller=tool_type,
                            span=span_context,
                        )
                    return HttpRunResponse(
                        header=HttpRunResponseHeader(
                            code=ErrCode.OPENAPI_AUTH_TYPE_ERR.code,
                            message=f"{ErrCode.OPENAPI_AUTH_TYPE_ERR.msg}",
                            sid=span_context.sid,
                        ),
                        payload={},
                    )
                api_key_info = operation_id_schema["security"].get(security_type)
                redis_engine = get_redis_engine()
                api_key_dict = None
                redis_cache = redis_engine.get(f"spark_bot:tool_config:{tool_id}")
                if redis_cache is None:
                    raise Exception("security: get redis_cache is none!")
                auth_info = redis_cache.get("authentication", {})
                if auth_info is None:
                    raise Exception("security: redis_cache get authentication is none!")

                if api_key_info.get("type") == "apiKey":
                    api_key_dict = auth_info.get("apiKey")
                if api_key_info.get("in") == "header":
                    message_header.update(api_key_dict)
                elif api_key_info.get("in") == "query":
                    message_query.update(api_key_dict)

            http_inst = HttpRun(
                server=operation_id_schema["server_url"],
                method=operation_id_schema["method"],
                path=(
                    json.loads(base64.b64decode(message.get("path")).decode("utf-8"))
                    if message.get("path")
                    else {}
                ),
                query=message_query,
                header=message_header,
                body=(
                    json.loads(base64.b64decode(message.get("body")).decode("utf-8"))
                    if message.get("body")
                    else {}
                ),
                open_api_schema=open_api_schema,
            )
            result = await http_inst.do_call(span_context)
            result_json = None
            try:
                result_json = json.loads(result)
            except Exception:
                result_json = result
            # Perform response data schema validation
            response_schema = get_response_schema(open_api_schema)
            import jsonschema

            errs = list(
                jsonschema.Draft7Validator(response_schema).iter_errors(result_json)
            )
            er_msgs = []
            for err in errs:
                err_msg: str = err.message
                if err_msg.startswith("None is not of type"):
                    key_type = err_msg.split("None is not of type")[1]
                    key_type = key_type.strip("")
                    path = err.json_path
                    path_list = path.split(".")[1:]
                    path_list_len = len(path_list)
                    i = 0
                    root = result_json
                    while True:
                        if i >= path_list_len - 1:
                            break
                        path_ = path_list[i]
                        if "[" in path_ and "]" in path_:
                            array_name, array_index = process_array(path_)
                            root = root.get(array_name)
                            root = root[array_index]
                        else:
                            root = root.get(path_)
                        i += 1
                    path_end = path_list[-1]
                    if "[" in path_end and "]" in path_end:
                        array_name, array_index = process_array(path_end)
                        if key_type in default_value:
                            root[array_name][array_index] = default_value.get(key_type)
                        else:
                            er_msgs.append(
                                f"参数路径: {err.json_path}, 错误信息: {err.message}"
                            )
                    else:
                        if key_type in default_value:
                            root[path_end] = default_value.get(key_type)
                        else:
                            er_msgs.append(
                                f"参数路径: {err.json_path}, 错误信息: {err.message}"
                            )
                else:
                    er_msgs.append(
                        f"参数路径: {err.json_path}, 错误信息: {err.message}"
                    )
            if er_msgs:
                msg = ";".join(er_msgs)
                span_context.add_error_event(
                    f"错误码：{ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.code}, "
                    f"错误信息：{ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.msg}, "
                    f"详细信息：{msg}"
                )
                span_context.set_status(Status(StatusCode.ERROR))
                if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                    m.in_error_count(ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.code)
                    node_trace.answer = (
                        f"错误信息：{ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.msg}, "
                        f"详细信息：{msg}"
                    )
                    node_trace.flow_id = tool_id
                    node_trace.log_caller = tool_type
                    node_trace.upload(
                        status=TraceStatus(
                            code=ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.code,
                            message=(
                                f"错误信息：{ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.msg}, "
                                f"详细信息：{msg}"
                            ),
                        ),
                        log_caller=tool_type,
                        span=span_context,
                    )
                return HttpRunResponse(
                    header=HttpRunResponseHeader(
                        code=ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.code,
                        message=(
                            f"错误信息：{ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.msg}, "
                            f"详细信息：{msg}"
                        ),
                        sid=span_context.sid,
                    ),
                    payload={},
                )
            span_context.add_info_events({"before result": result})
            result = json.dumps(result_json, ensure_ascii=False)
            span_context.add_info_events({"after result": result})
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_success_count()
                node_trace.answer = result
                node_trace.flow_id = tool_id
                node_trace.log_caller = tool_type
                node_trace.upload(
                    status=TraceStatus(
                        code=ErrCode.SUCCESSES.code, message=ErrCode.SUCCESSES.msg
                    ),
                    log_caller=tool_type,
                    span=span_context,
                )
            return HttpRunResponse(
                header=HttpRunResponseHeader(
                    code=ErrCode.SUCCESSES.code,
                    message=ErrCode.SUCCESSES.msg,
                    sid=span_context.sid,
                ),
                payload={
                    "text": {
                        "text": result,
                    }
                },
            )
        except SparkLinkBaseException as err:
            span_context.add_error_event(err.message)
            span_context.set_status(Status(StatusCode.ERROR))
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(err.code)
                node_trace.answer = err.message
                node_trace.flow_id = tool_id
                node_trace.log_caller = tool_type
                node_trace.upload(
                    status=TraceStatus(code=err.code, message=err.message),
                    log_caller=tool_type,
                    span=span_context,
                )
            return HttpRunResponse(
                header=HttpRunResponseHeader(
                    code=err.code, message=err.message, sid=span_context.sid
                ),
                payload={},
            )
        except Exception as err:
            span_context.add_error_event(f"{ErrCode.COMMON_ERR.msg}: {err}")
            span_context.set_status(Status(StatusCode.ERROR))
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(ErrCode.COMMON_ERR.code)
                node_trace.answer = f"{ErrCode.COMMON_ERR.msg}: {err}"
                node_trace.flow_id = tool_id
                node_trace.log_caller = tool_type
                node_trace.upload(
                    status=TraceStatus(
                        code=ErrCode.COMMON_ERR.code,
                        message=f"{ErrCode.COMMON_ERR.msg}: {err}",
                    ),
                    log_caller=tool_type,
                    span=span_context,
                )
            return HttpRunResponse(
                header=HttpRunResponseHeader(
                    code=ErrCode.COMMON_ERR.code,
                    message=f"{ErrCode.COMMON_ERR.msg}: {err}",
                    sid=span_context.sid,
                ),
                payload={},
            )


async def tool_debug(tool_debug_params: ToolDebugRequest) -> ToolDebugResponse:
    """
    Tool debugging interface
    """
    run_params_list = tool_debug_params.dict()
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
    tool_id = (
        run_params_list.get("header", {}).get("tool_id")
        if run_params_list.get("header", {}).get("tool_id")
        else ""
    )
    span = Span(
        app_id=app_id,
        uid=uid,
    )
    sid = run_params_list.get("header", {}).get("sid")
    if sid:
        span.sid = sid

    with span.start(func_name="tool_debug") as span_context:
        m = Meter(app_id=span_context.app_id, func="tool_debug")
        try:
            openapi_schema = json.loads(tool_debug_params.openapi_schema)
            logger.info(
                {
                    "exec api, tool_debug router usr_input": json.dumps(
                        run_params_list, ensure_ascii=False
                    )
                }
            )
            span_context.add_info_events(
                {"usr_input": json.dumps(run_params_list, ensure_ascii=False)}
            )
            span_context.set_attributes(
                attributes={"server": run_params_list.get("server", {})}
            )
            tool_type = (
                os.getenv(const.OFFICIAL_TOOL_KEY)
                if openapi_schema.get("info").get("x-is-official")
                else os.getenv(const.THIRD_TOOL_KEY)
            )
            node_trace = NodeTrace(
                flow_id=tool_id,
                sid=span_context.sid,
                app_id=span_context.app_id,
                uid=span_context.uid,
                bot_id="/tools/tool_debug",
                chat_id=span_context.sid,
                sub="spark-link",
                caller=caller,
                log_caller="",
                question=json.dumps(run_params_list, ensure_ascii=False),
            )
            node_trace.record_start()
            # Parameter validation
            validate_err = api_validate(get_tool_debug_schema(), run_params_list)
            if validate_err:
                span_context.add_error_event(
                    f"Error code: {ErrCode.JSON_PROTOCOL_PARSER_ERR.code}, error message: {validate_err}"
                )
                if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                    m.in_error_count(ErrCode.JSON_PROTOCOL_PARSER_ERR.code)
                    node_trace.answer = validate_err
                    node_trace.flow_id = tool_id
                    node_trace.log_caller = tool_type
                    node_trace.upload(
                        status=TraceStatus(
                            code=ErrCode.JSON_PROTOCOL_PARSER_ERR.code,
                            message=validate_err,
                        ),
                        log_caller=tool_type,
                        span=span_context,
                    )
                return HttpRunResponse(
                    header=HttpRunResponseHeader(
                        code=ErrCode.JSON_PROTOCOL_PARSER_ERR.code,
                        message=validate_err,
                        sid=span_context.sid,
                    ),
                    payload={},
                )

            http_inst = HttpRun(
                server=tool_debug_params.server,
                method=tool_debug_params.method,
                path=tool_debug_params.path if tool_debug_params.path else {},
                query=tool_debug_params.query if tool_debug_params.query else {},
                header=tool_debug_params.header if tool_debug_params.header else {},
                body=tool_debug_params.body if tool_debug_params.body else {},
                open_api_schema=openapi_schema,
            )
            result = await http_inst.do_call(span_context)
            result_json = None
            try:
                result_json = json.loads(result)
            except Exception:
                result_json = result
            # Perform response data schema validation
            response_schema = get_response_schema(openapi_schema)
            import jsonschema

            errs = list(
                jsonschema.Draft7Validator(response_schema).iter_errors(result_json)
            )
            er_msgs = []
            for err in errs:
                err_msg: str = err.message
                if err_msg.startswith("None is not of type"):
                    key_type = err_msg.split("None is not of type")[1]
                    key_type = key_type.strip("")
                    path = err.json_path
                    path_list = path.split(".")[1:]
                    path_list_len = len(path_list)
                    i = 0
                    root = result_json
                    while True:
                        if i >= path_list_len - 1:
                            break
                        path_ = path_list[i]
                        if "[" in path_ and "]" in path_:
                            array_name, array_index = process_array(path_)
                            root = root.get(array_name)
                            root = root[array_index]
                        else:
                            root = root.get(path_)
                        i += 1
                    path_end = path_list[-1]
                    if "[" in path_end and "]" in path_end:
                        array_name, array_index = process_array(path_end)
                        if key_type in default_value:
                            root[array_name][array_index] = default_value.get(key_type)
                        else:
                            er_msgs.append(
                                f"参数路径: {err.json_path}, 错误信息: {err.message}"
                            )
                    else:
                        if key_type in default_value:
                            root[path_end] = default_value.get(key_type)
                        else:
                            er_msgs.append(
                                f"参数路径: {err.json_path}, 错误信息: {err.message}"
                            )
                else:
                    er_msgs.append(
                        f"参数路径: {err.json_path}, 错误信息: {err.message}"
                    )
            if er_msgs:
                msg = ";".join(er_msgs)
                span_context.add_error_event(
                    f"错误码：{ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.code}, "
                    f"错误信息：{ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.msg}, "
                    f"详细信息：{msg}"
                )
                span_context.set_status(Status(StatusCode.ERROR))
                if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                    m.in_error_count(ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.code)
                    node_trace.answer = (
                        f"错误信息：{ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.msg}, "
                        f"详细信息：{msg}"
                    )
                    node_trace.flow_id = tool_id
                    node_trace.log_caller = tool_type
                    node_trace.upload(
                        status=TraceStatus(
                            code=ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.code,
                            message=(
                                f"错误信息：{ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.msg}, "
                                f"详细信息：{msg}"
                            ),
                        ),
                        log_caller=tool_type,
                        span=span_context,
                    )
                return HttpRunResponse(
                    header=HttpRunResponseHeader(
                        code=ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.code,
                        message=(
                            f"错误信息：{ErrCode.RESPONSE_SCHEMA_VALIDATE_ERR.msg}, "
                            f"详细信息：{msg}"
                        ),
                        sid=span_context.sid,
                    ),
                    payload={},
                )
            span_context.add_info_events({"before result": result})
            result = json.dumps(result_json, ensure_ascii=False)
            span_context.add_info_events({"after result": result})
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_success_count()
                node_trace.answer = result
                node_trace.flow_id = tool_id
                node_trace.log_caller = tool_type
                node_trace.upload(
                    status=TraceStatus(
                        code=ErrCode.SUCCESSES.code, message=ErrCode.SUCCESSES.msg
                    ),
                    log_caller=tool_type,
                    span=span_context,
                )
            return ToolDebugResponse(
                header=ToolDebugResponseHeader(
                    code=ErrCode.SUCCESSES.code,
                    message=ErrCode.SUCCESSES.msg,
                    sid=span_context.sid,
                ),
                payload={
                    "text": {
                        "text": result,
                    }
                },
            )
        except SparkLinkBaseException as err:
            span_context.add_error_event(err.message)
            span_context.set_status(Status(StatusCode.ERROR))
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(err.code)
                node_trace.answer = err.message
                node_trace.flow_id = tool_id
                node_trace.log_caller = tool_type
                node_trace.upload(
                    status=TraceStatus(code=err.code, message=err.message),
                    log_caller=tool_type,
                    span=span_context,
                )
            return HttpRunResponse(
                header=HttpRunResponseHeader(
                    code=err.code, message=err.message, sid=span_context.sid
                ),
                payload={},
            )
        except Exception as err:
            span_context.add_error_event(f"{ErrCode.COMMON_ERR.msg}: {err}")
            span_context.set_status(Status(StatusCode.ERROR))
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(ErrCode.COMMON_ERR.code)
                node_trace.answer = f"{ErrCode.COMMON_ERR.msg}: {err}"
                node_trace.flow_id = tool_id
                node_trace.log_caller = tool_type
                node_trace.upload(
                    status=TraceStatus(
                        code=ErrCode.COMMON_ERR.code,
                        message=f"{ErrCode.COMMON_ERR.msg}: {err}",
                    ),
                    log_caller=tool_type,
                    span=span_context,
                )
            return HttpRunResponse(
                header=HttpRunResponseHeader(
                    code=ErrCode.COMMON_ERR.code,
                    message=f"{ErrCode.COMMON_ERR.msg}: {err}",
                    sid=span_context.sid,
                ),
                payload={},
            )


def process_array(name):
    """Process array notation in parameter names.

    Extracts the array name and index from bracket notation (e.g., 'items[0]').

    Args:
        name (str): Parameter name with array notation (e.g., 'items[0]')

    Returns:
        tuple: A tuple containing (array_name, array_index)
    """
    bracket_left_index = name.find("[")
    bracket_right_index = name.find("]")
    array_name = name[0:bracket_left_index]
    array_index = int(name[bracket_left_index + 1: bracket_right_index])
    return array_name, array_index


def get_response_schema(openapi_schema: dict) -> dict:
    """
    Get response schema from tool's OpenAPI schema
    """
    if openapi_schema is None:
        return {}
    paths = openapi_schema.get("paths", {})
    response_schema = {}
    for _, method_dict in paths.items():
        for _, method in method_dict.items():
            response_schema = (
                method.get("responses", {})
                .get("200", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema", {})
            )
    return response_schema
