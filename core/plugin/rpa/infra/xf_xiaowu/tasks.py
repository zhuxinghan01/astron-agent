"""Module for creating and querying RPA tasks."""

import os
from typing import Optional, Tuple

import httpx
from fastapi import HTTPException
from loguru import logger

from consts import const
from errors.error_code import ErrorCode
from exceptions.config_exceptions import InvalidConfigException
from utils.urls.utl_util import is_valid_url


# 创建任务
async def create_task(
    access_token: str,
    project_id: str,
    exec_position: Optional[str],
    params: Optional[dict],
) -> str:
    """
    创建任务。
    - 返回任务 ID。
    """
    task_create_url = os.getenv(const.RPA_TASK_CREATE_URL_KEY, None)
    if not is_valid_url(task_create_url):
        logger.error(f"无效的任务创建 URL: {task_create_url}")
        raise InvalidConfigException(f"无效的任务创建 URL: {task_create_url}")

    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    body = {"project_id": project_id, "exec_position": exec_position, "params": params}
    async with httpx.AsyncClient() as client:
        try:
            assert task_create_url is not None
            response = await client.post(task_create_url, headers=header, json=body)
            response.raise_for_status()

            response_data = response.json()
            print(f"create task response_data:\n {response_data}\n\n")

            code = response_data.get("code", "-1")
            msg = response_data.get("msg", None)
            data = response_data.get("data", None)

            if code != "0000" or not data:
                logger.error(f"创建任务失败: {msg}")
                raise HTTPException(status_code=500, detail=f"创建任务失败: {msg}")

            task_id = data.get("executionId", None)
            if not task_id:
                logger.error("创建任务失败: 未返回任务ID")
                raise HTTPException(
                    status_code=500,
                    detail=f"创建任务失败: 未返回任务ID: {response_data}",
                )

            return task_id
        except httpx.HTTPStatusError as e:
            logger.error(f"创建任务失败: {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"创建任务失败: {e.response.text}",
            ) from e
        except httpx.RequestError as e:
            logger.error(f"创建任务失败: {e}")
            raise HTTPException(status_code=500, detail=f"创建任务失败: {e}") from e


# 查询任务状态
async def query_task_status(
    access_token: str, task_id: str
) -> Tuple[int, str, dict] | None:
    """
    查询任务状态。
    - 若任务完成，返回任务结果。
    - 若任务未完成，返回 None。
    """
    task_query_url = os.getenv(const.RPA_TASK_QUERY_URL_KEY, None)
    if not is_valid_url(task_query_url):
        logger.error(f"无效的任务查询 URL: {task_query_url}")
        raise InvalidConfigException(f"无效的任务查询 URL: {task_query_url}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url=f"{task_query_url}/{task_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()

            response_data = response.json()
            print(f"query task response_data:\n {response_data}\n\n")

            code = response_data.get("code", "-1")
            msg = response_data.get("msg", None)
            data = response_data.get("data", None)
            if code != "0000" or not data:
                logger.error(f"查询任务状态失败: {msg}")
                raise HTTPException(
                    status_code=500, detail=f"查询任务状态失败: {code}:{msg}"
                )

            execution = data.get("execution", {})
            if not execution:
                logger.error("查询任务状态失败: 未返回任务信息")
                raise HTTPException(
                    status_code=500, detail="查询任务状态失败: 未返回任务信息"
                )

            status = execution.get("status", "")
            if status in ["COMPLETED"]:
                result = execution.get("result", {})
                data = result.get("data", {})
                return ErrorCode.SUCCESS.code, ErrorCode.SUCCESS.message, data

            if status in ["FAILED"]:
                msg = execution.get("error", "")
                return (
                    ErrorCode.QUERY_TASK_ERROR.code,
                    f"{ErrorCode.QUERY_TASK_ERROR.message}: {msg}",
                    {},
                )
            if status in ["PENDING"]:
                return None

            raise HTTPException(status_code=500, detail=f"未知的任务状态: {status}")

        except httpx.RequestError as e:
            logger.error(f"查询任务状态失败: {e}")
            raise HTTPException(status_code=500, detail=f"查询任务状态失败: {e}") from e
