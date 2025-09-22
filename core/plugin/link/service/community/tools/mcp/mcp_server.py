"""MCP (Model Context Protocol) server integration module.

This module provides FastAPI endpoints and utilities for interacting with MCP servers.
It handles tool listing, tool execution, and server management operations with proper
error handling, observability tracing, and security validations.
"""

import os
from typing import Tuple
from consts import const

from fastapi import Body
from loguru import logger
from mcp import ClientSession
from mcp.client.sse import sse_client
from opentelemetry.trace import Status, StatusCode
from xingchen_utils.otlp.trace.span import Span
from xingchen_utils.otlp.metric.meter import Meter
from xingchen_utils.otlp.node_trace.node_trace import NodeTrace
from xingchen_utils.otlp.node_trace.node import TraceStatus

from api.schemas.community.tools.mcp.mcp_tools_schema import (
    MCPToolListRequest,
    MCPToolListResponse,
    MCPItemInfo,
    MCPInfo,
    MCPToolListData,
    MCPCallToolRequest,
    MCPCallToolResponse,
    MCPCallToolData,
    MCPTextResponse,
    MCPImageResponse,
)
from domain.models.manager import get_db_engine
from infra.tool_crud.process import ToolCrudOperation
from utils.errors.code import ErrCode
from utils.sid.sid_generator2 import new_sid
from utils.security.access_interceptor import is_in_blacklist, is_local_url


async def tool_list(list_info: MCPToolListRequest = Body()) -> MCPToolListResponse:
    """
    Get the list of tools.
    """
    session_id = new_sid()
    mcp_server_ids = list_info.mcp_server_ids
    mcp_server_urls = list_info.mcp_server_urls

    span = Span(
        app_id="appid_mcp",
        uid="mcp_uid",
    )

    if session_id:
        span.sid = session_id

    with span.start(func_name="tool_list") as span_context:
        logger.info(
            {"mcp api, tool_list router usr_input": list_info.model_dump_json()}
        )
        span_context.add_info_events({"usr_input": list_info.model_dump_json()})
        span_context.set_attributes(attributes={"tool_id": "tool_list"})
        node_trace = NodeTrace(
            flow_id="",
            sid=span_context.sid,
            app_id=span_context.app_id,
            uid=span_context.uid,
            bot_id="/mcp/tool_list",
            chat_id=span_context.sid,
            sub="spark-link",
            caller="mcp_caller",
            log_caller="",
            question=list_info.model_dump_json(),
        )
        node_trace.record_start()
        m = Meter(app_id=span_context.app_id, func="tool_list")

        items = []
        # Process IDs
        if mcp_server_ids:
            for mcp_server_id in mcp_server_ids:
                # url = getFromDB(tool_id)
                err, url = get_mcp_server_url(
                    mcp_server_id=mcp_server_id, span=span_context
                )
                if err is not ErrCode.SUCCESSES:
                    items.append(
                        MCPItemInfo(
                            server_id=mcp_server_id,
                            server_status=err.code,
                            server_message=err.msg,
                            tools=[],
                        )
                    )
                    continue

                if is_local_url(url):
                    err = ErrCode.MCP_SERVER_LOCAL_URL_ERR
                    items.append(
                        MCPItemInfo(
                            server_id=mcp_server_id,
                            server_status=err.code,
                            server_message=err.msg,
                            tools=[],
                        )
                    )
                    continue

                try:
                    async with sse_client(url=url) as (read, write):
                        try:
                            async with ClientSession(
                                read, write, logging_callback=None
                            ) as session:
                                try:
                                    await session.initialize()
                                except Exception:
                                    err = ErrCode.MCP_SERVER_INITIAL_ERR
                                    items.append(
                                        MCPItemInfo(
                                            server_id=mcp_server_id,
                                            server_status=err.code,
                                            server_message=err.msg,
                                            tools=[],
                                        )
                                    )
                                    continue

                                try:
                                    tools_result = await session.list_tools()
                                    tools_dict = tools_result.model_dump()["tools"]
                                    tools = []
                                    for tool in tools_dict:
                                        tool_info = MCPInfo(
                                            name=tool["name"],
                                            description=tool["description"],
                                            inputSchema=tool["inputSchema"],
                                        )
                                        tools.append(tool_info)

                                    success = ErrCode.SUCCESSES
                                    items.append(
                                        MCPItemInfo(
                                            server_id=mcp_server_id,
                                            server_url=None,
                                            server_status=success.code,
                                            server_message=success.msg,
                                            tools=tools,
                                        )
                                    )
                                except Exception:
                                    err = ErrCode.MCP_SERVER_TOOL_LIST_ERR
                                    items.append(
                                        MCPItemInfo(
                                            server_id=mcp_server_id,
                                            server_status=err.code,
                                            server_message=err.msg,
                                            tools=[],
                                        )
                                    )
                                    continue
                        except Exception:
                            err = ErrCode.MCP_SERVER_SESSION_ERR
                            items.append(
                                MCPItemInfo(
                                    server_id=mcp_server_id,
                                    server_status=err.code,
                                    server_message=err.msg,
                                    tools=[],
                                )
                            )
                            continue
                except Exception:
                    err = ErrCode.MCP_SERVER_CONNECT_ERR
                    items.append(
                        MCPItemInfo(
                            server_id=mcp_server_id,
                            server_status=err.code,
                            server_message=err.msg,
                            tools=[],
                        )
                    )
                    continue

        # Process URLs
        if mcp_server_urls:
            for url in mcp_server_urls:
                if is_local_url(url):
                    err = ErrCode.MCP_SERVER_LOCAL_URL_ERR
                    items.append(
                        MCPItemInfo(
                            server_url=str(url),
                            server_status=err.code,
                            server_message=err.msg,
                            tools=[],
                        )
                    )
                    continue

                if is_in_blacklist(url=url):
                    err = ErrCode.MCP_SERVER_BLACKLIST_URL_ERR
                    items.append(
                        MCPItemInfo(
                            server_url=str(url),
                            server_status=err.code,
                            server_message=err.msg,
                            tools=[],
                        )
                    )
                    continue

                try:
                    async with sse_client(url=url) as (read, write):
                        try:
                            async with ClientSession(
                                read, write, logging_callback=None
                            ) as session:
                                try:
                                    await session.initialize()
                                except Exception:
                                    err = ErrCode.MCP_SERVER_INITIAL_ERR
                                    items.append(
                                        MCPItemInfo(
                                            server_url=url,
                                            server_status=err.code,
                                            server_message=err.msg,
                                            tools=[],
                                        )
                                    )
                                    continue

                                try:
                                    tools_result = await session.list_tools()
                                    tools_dict = tools_result.model_dump()["tools"]
                                    tools = []
                                    for tool in tools_dict:
                                        tool_info = MCPInfo(
                                            name=tool.get("name", "No name available"),
                                            description=tool.get(
                                                "description",
                                                "No description available",
                                            ),
                                            inputSchema=tool.get("inputSchema"),
                                        )
                                        tools.append(tool_info)
                                    success = ErrCode.SUCCESSES
                                    items.append(
                                        MCPItemInfo(
                                            server_url=url,
                                            server_status=success.code,
                                            server_message=success.msg,
                                            tools=tools,
                                        )
                                    )
                                except Exception:
                                    err = ErrCode.MCP_SERVER_TOOL_LIST_ERR
                                    items.append(
                                        MCPItemInfo(
                                            server_url=url,
                                            server_status=err.code,
                                            server_message=err.msg,
                                            tools=[],
                                        )
                                    )
                                    continue
                        except Exception:
                            err = ErrCode.MCP_SERVER_SESSION_ERR
                            items.append(
                                MCPItemInfo(
                                    server_url=url,
                                    server_status=err.code,
                                    server_message=err.msg,
                                    tools=[],
                                )
                            )
                            continue
                except Exception:
                    err = ErrCode.MCP_SERVER_CONNECT_ERR
                    items.append(
                        MCPItemInfo(
                            server_url=url,
                            server_status=err.code,
                            server_message=err.msg,
                            tools=[],
                        )
                    )
                    continue

        success = ErrCode.SUCCESSES
        result = MCPToolListResponse(
            code=success.code,
            message=success.msg,
            sid=session_id,
            data=MCPToolListData(servers=items),
        )
        if os.getenv(const.enable_otlp_key, "false").lower() == "true":
            m.in_success_count()
            node_trace.answer = result.model_dump_json()
            node_trace.flow_id = "tool_list"
            node_trace.log_caller = "mcp_type"
            node_trace.upload(
                status=TraceStatus(code=success.code, message=success.msg),
                log_caller="mcp_type",
                span=span_context,
            )
        return result


async def call_tool(call_info: MCPCallToolRequest = Body()) -> MCPCallToolResponse:
    """
    Call a tool.
    """
    session_id = new_sid()
    mcp_server_id = call_info.mcp_server_id
    tool_name = call_info.tool_name
    tool_args = call_info.tool_args

    span = Span(
        app_id="appid_mcp",
        uid="mcp_uid",
    )

    if session_id:
        span.sid = session_id

    with span.start(func_name="call_tool") as span_context:
        logger.info(
            {"mcp api, call_tool router usr_input": call_info.model_dump_json()}
        )
        span_context.add_info_events({"usr_input": call_info.model_dump_json()})
        span_context.set_attributes(attributes={"tool_id": mcp_server_id})
        node_trace = NodeTrace(
            flow_id="",
            sid=span_context.sid,
            app_id=span_context.app_id,
            uid=span_context.uid,
            bot_id="/mcp/call_tool",
            chat_id=span_context.sid,
            sub="spark-link",
            caller="mcp_caller",
            log_caller="",
            question=call_info.model_dump_json(),
        )
        node_trace.record_start()
        m = Meter(app_id=span_context.app_id, func="call_tool")

        url = call_info.mcp_server_url

        if url and is_in_blacklist(url=url):
            err = ErrCode.MCP_SERVER_BLACKLIST_URL_ERR
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(err.code)
            return MCPCallToolResponse(
                code=err.code,
                message=err.msg,
                sid=session_id,
                data=MCPCallToolData(isError=None, content=None),
            )

        if not url:
            # url = getFromDB(tool_id)
            err, url = get_mcp_server_url(
                mcp_server_id=mcp_server_id, span=span_context
            )
            node_trace.answer = err.msg
            node_trace.upload(
                status=TraceStatus(code=err.code, message=err.msg),
                log_caller="",
                span=span_context,
            )
            if err is not ErrCode.SUCCESSES:
                if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                    m.in_error_count(err.code)
                return MCPCallToolResponse(
                    code=err.code,
                    message=err.msg,
                    sid=session_id,
                    data=MCPCallToolData(isError=None, content=None),
                )

        if is_local_url(url):
            err = ErrCode.MCP_SERVER_LOCAL_URL_ERR
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(err.code)
            return MCPCallToolResponse(
                code=err.code,
                message=err.msg,
                sid=session_id,
                data=MCPCallToolData(isError=None, content=None),
            )

        is_error = True
        content = []
        try:
            async with sse_client(url=url) as (read, write):
                try:
                    async with ClientSession(
                        read, write, logging_callback=None
                    ) as session:
                        try:
                            await session.initialize()
                        except Exception:
                            err = ErrCode.MCP_SERVER_INITIAL_ERR
                            span_context.add_error_event(err.msg)
                            span_context.set_status(Status(StatusCode.ERROR))
                            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                                m.in_error_count(err.code)
                                node_trace.answer = err.msg
                                node_trace.flow_id = mcp_server_id
                                node_trace.upload(
                                    status=TraceStatus(code=err.code, message=err.msg),
                                    log_caller="",
                                    span=span_context,
                                )
                            return MCPCallToolResponse(
                                code=err.code,
                                message=err.msg,
                                sid=session_id,
                                data=MCPCallToolData(isError=None, content=None),
                            )
                        try:
                            call_result = await session.call_tool(
                                tool_name, arguments=tool_args
                            )
                            call_dict = call_result.model_dump()
                            is_error = call_dict["isError"]
                            for data in call_dict["content"]:
                                if data["type"] == "text":
                                    text = MCPTextResponse(text=data["text"])
                                    content.append(text)
                                elif data["type"] == "image":
                                    image = MCPImageResponse(
                                        data=data["data"], mineType=data["mineType"]
                                    )
                                    content.append(image)
                        except Exception:
                            err = ErrCode.MCP_SERVER_CALL_TOOL_ERR
                            span_context.add_error_event(err.msg)
                            span_context.set_status(Status(StatusCode.ERROR))
                            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                                m.in_error_count(err.code)
                                node_trace.answer = err.msg
                                node_trace.flow_id = mcp_server_id
                                node_trace.upload(
                                    status=TraceStatus(code=err.code, message=err.msg),
                                    log_caller="",
                                    span=span_context,
                                )
                            return MCPCallToolResponse(
                                code=err.code,
                                message=err.msg,
                                sid=session_id,
                                data=MCPCallToolData(isError=None, content=None),
                            )
                except Exception:
                    err = ErrCode.MCP_SERVER_SESSION_ERR
                    span_context.add_error_event(err.msg)
                    span_context.set_status(Status(StatusCode.ERROR))
                    if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                        m.in_error_count(err.code)
                        node_trace.answer = err.msg
                        node_trace.flow_id = mcp_server_id
                        node_trace.upload(
                            status=TraceStatus(code=err.code, message=err.msg),
                            log_caller="",
                            span=span_context,
                        )
                    return MCPCallToolResponse(
                        code=err.code,
                        message=err.msg,
                        sid=session_id,
                        data=MCPCallToolData(isError=None, content=None),
                    )
        except Exception:
            err = ErrCode.MCP_SERVER_CONNECT_ERR
            span_context.add_error_event(err.msg)
            span_context.set_status(Status(StatusCode.ERROR))
            if os.getenv(const.enable_otlp_key, "false").lower() == "true":
                m.in_error_count(err.code)
                node_trace.answer = err.msg
                node_trace.flow_id = mcp_server_id
                node_trace.upload(
                    status=TraceStatus(code=err.code, message=err.msg),
                    log_caller="",
                    span=span_context,
                )
            return MCPCallToolResponse(
                code=err.code,
                message=err.msg,
                sid=session_id,
                data=MCPCallToolData(isError=None, content=None),
            )

        success = ErrCode.SUCCESSES
        result = MCPCallToolResponse(
            code=success.code,
            message=success.msg,
            sid=session_id,
            data=MCPCallToolData(isError=is_error, content=content),
        )
        if os.getenv(const.enable_otlp_key, "false").lower() == "true":
            m.in_success_count()
            node_trace.answer = result.model_dump_json()
            node_trace.flow_id = mcp_server_id
            node_trace.log_caller = "mcp_type"
            node_trace.upload(
                status=TraceStatus(code=success.code, message=success.msg),
                log_caller="mcp_type",
                span=span_context,
            )
        return result


def get_mcp_server_url(mcp_server_id: str, span: Span) -> Tuple[ErrCode, str]:
    """Retrieve MCP server URL from database by server ID.

    Args:
        mcp_server_id: Unique identifier for the MCP server
        span: OpenTelemetry span for tracing

    Returns:
        Tuple containing error code and server URL string
    """
    if not mcp_server_id:
        return (ErrCode.MCP_SERVER_ID_EMPTY_ERR, "")

    tool_id_info = [{"app_id": "1232223", "tool_id": mcp_server_id}]
    try:
        crud_inst = ToolCrudOperation(get_db_engine())
        query_results = crud_inst.get_tools(tool_id_info, span=span)
    except Exception:
        return (ErrCode.MCP_CRUD_OPERATION_FAILED_ERR, "")

    if not query_results:
        return (ErrCode.MCP_SERVER_NOT_FOUND_ERR, "")

    mcp_server = ""
    for query_result in query_results:
        result_dict = query_result.dict()
        if result_dict.get("tool_id", "") != mcp_server_id:
            continue

        # Database extension mcp_server_url stores MCP URL data
        mcp_server = result_dict.get("mcp_server_url", "")
        break

    if not mcp_server:
        return (ErrCode.MCP_SERVER_URL_EMPTY_ERR, mcp_server)

    return (ErrCode.SUCCESSES, mcp_server)
