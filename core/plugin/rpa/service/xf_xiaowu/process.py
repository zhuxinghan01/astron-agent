"""任务处理模块，包含任务创建和监控逻辑。"""

import asyncio
import os
import time
from typing import AsyncGenerator, Optional

import httpx
from fastapi import HTTPException
from loguru import logger

from api.schemas.execution_schema import RPAExecutionResponse
from consts import const
from errors.error_code import ErrorCode
from exceptions.config_exceptions import InvalidConfigException
from infra.xf_xiaowu.tasks import create_task, query_task_status


async def task_monitoring(
    sid: Optional[str],
    access_token: str,
    project_id: str,
    exec_position: Optional[str],
    params: Optional[dict],
) -> AsyncGenerator[str, None]:
    """
    监控任务状态。
    - 每 ping_interval 秒发送一次 "ping"。
    - 每 task_query_interval 秒查询一次任务状态。
    - 任务完成后，返回任务结果。
    - 若超时（timeout_sec 秒），返回 "超时"。
    :param task_query_interval: 任务查询间隔（秒），默认 10 秒。
    """
    logger.debug(
        f"Starting task monitoring for project_id: {project_id}, "
        f"exec_position: {exec_position}, params: {params}"
    )

    task_id = None
    try:
        task_id = await create_task(
            access_token=access_token,
            project_id=project_id,
            exec_position=exec_position,
            params=params,
        )  # 创建任务
    except (
        InvalidConfigException,
        HTTPException,
        httpx.HTTPStatusError,
        httpx.RequestError,
        AssertionError,
        KeyError,
        AttributeError,
    ) as e:
        logger.error(f"error: {e}")
        code = ErrorCode.CREATE_TASK_ERROR.code
        msg = f"{ErrorCode.CREATE_TASK_ERROR.message}, detail: {e}"
        error = RPAExecutionResponse(code=code, message=msg, sid=sid)
        yield error.model_dump_json()
        return

    start_time = time.time()
    while (time.time() - start_time) < int(os.getenv(const.RPA_TIMEOUT_KEY, "300")):
        await asyncio.sleep(int(os.getenv(const.RPA_TASK_QUERY_INTERVAL_KEY, "10")))
        result = await query_task_status(access_token, task_id)  # 查询任务
        if result:
            code, msg, data = result
            if code == ErrorCode.SUCCESS.code:
                success = RPAExecutionResponse(
                    code=code, message=msg, data=data, sid=sid
                )
                yield success.model_dump_json()
            elif code == ErrorCode.QUERY_TASK_ERROR.code:
                error = RPAExecutionResponse(code=code, message=msg, sid=sid)
                yield error.model_dump_json()
            return

    timeout = RPAExecutionResponse(
        code=ErrorCode.TIMEOUT_ERROR.code,
        message=ErrorCode.TIMEOUT_ERROR.message,
        sid=sid,
    )
    yield timeout.model_dump_json()
