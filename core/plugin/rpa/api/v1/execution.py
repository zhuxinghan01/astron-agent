"""RPA 执行相关 API 路由."""

import json
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Header, HTTPException
from sse_starlette.sse import EventSourceResponse

from api.schemas.execution_schema import RPAExecutionRequest
from consts import const
from service.xf_xiaowu.process import task_monitoring

# RPA 执行路由
execution_router = APIRouter(tags=["rpa execution api"])


@execution_router.post("/exec")
async def exec_fun(
    Authorization: str = Header(   # pylint: disable=invalid-name
        ..., description="访问令牌"
    ),
    request: RPAExecutionRequest = Body(..., description="RPA 执行请求参数"),
) -> EventSourceResponse:
    """执行 RPA 任务并返回流式响应."""
    try:
        # 设置响应头
        headers = {
            "Content-Type": "text/event-stream; charset=utf-8",
            "Transfer-Encoding": "chunked",
            "Connection": "keep-alive",
            "Date": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
        }
        ping_interval = int(os.getenv(const.RPA_PING_INTERVAL_KEY, "3"))
        acctss_token = (
            Authorization[7:] if Authorization.startswith("Bearer ")
            else Authorization
        )
        return EventSourceResponse(
            task_monitoring(
                sid=request.sid,
                access_token=acctss_token,
                project_id=request.project_id,
                exec_position=request.exec_position,
                params=request.params,
            ),
            headers=headers,
            ping=ping_interval,
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid JSON format for 'params':" f" {e}"
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
