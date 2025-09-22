"""测试 RPA 任务管理模块。"""

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException

from errors.error_code import ErrorCode
from exceptions.config_exceptions import InvalidConfigException
from infra.xf_xiaowu.tatks import create_task, query_task_status


class TestCreateTask:
    """create_task 函数的测试用例。"""

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RPA_TASK_CREATE_URL": "https://api.example.com/create"})
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    async def test_create_task_success(self, mock_client_class: Any) -> None:
        """测试成功创建任务。"""
        # 模拟 HTTP 客户端响应
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {"executionId": "task_123456"},
        }
        mock_response.raise_for_status.return_value = None
        mock_client.post.return_value = mock_response

        # 调用函数
        result = await create_task(
            access_token="test_token",
            project_id="project_123",
            exec_position="EXECUTOR",
            params={"key": "value"},
        )

        # 验证结果
        assert result == "task_123456"

        # 验证 HTTP 请求参数
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://api.example.com/create"
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_token"
        assert call_args[1]["json"]["project_id"] == "project_123"

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RPA_TASK_CREATE_URL": "invalid_url"})
    async def test_create_task_invalid_url(self) -> None:
        """测试无效的创建任务 URL。"""
        with pytest.raises(InvalidConfigException) as exc_info:
            await create_task(
                access_token="test_token",
                project_id="project_123",
                exec_position="EXECUTOR",
                params={"key": "value"},
            )

        assert "无效的任务创建 URL" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch.dict(os.environ, {}, clear=True)
    async def test_create_task_missing_url_env(self) -> None:
        """测试缺少任务创建 URL 环境变量。"""
        with pytest.raises(InvalidConfigException) as exc_info:
            await create_task(
                access_token="test_token",
                project_id="project_123",
                exec_position="EXECUTOR",
                params={"key": "value"},
            )

        assert "无效的任务创建 URL" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RPA_TASK_CREATE_URL": "https://api.example.com/create"})
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    async def test_create_task_api_error_response(self, mock_client_class: Any) -> None:
        """测试 API 返回错误响应。"""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "5000",
            "msg": "Internal server error",
            "data": None,
        }
        mock_response.raise_for_status.return_value = None
        mock_client.post.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            await create_task(
                access_token="test_token",
                project_id="project_123",
                exec_position="EXECUTOR",
                params={"key": "value"},
            )

        assert exc_info.value.status_code == 500
        assert "创建任务失败" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RPA_TASK_CREATE_URL": "https://api.example.com/create"})
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    async def test_create_task_missing_execution_id(
        self, mock_client_class: Any
    ) -> None:
        """测试响应中缺少 executionId。"""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {"other_field": "value"},  # 缺少 executionId
        }
        mock_response.raise_for_status.return_value = None
        mock_client.post.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            await create_task(
                access_token="test_token",
                project_id="project_123",
                exec_position="EXECUTOR",
                params={"key": "value"},
            )

        assert exc_info.value.status_code == 500
        assert "未返回任务ID" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RPA_TASK_CREATE_URL": "https://api.example.com/create"})
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    async def test_create_task_http_status_error(self, mock_client_class: Any) -> None:
        """测试 HTTP 状态错误。"""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # 模拟 HTTP 状态错误
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        http_error = httpx.HTTPStatusError(
            "400", request=MagicMock(), response=mock_response
        )
        mock_client.post.side_effect = http_error

        with pytest.raises(HTTPException) as exc_info:
            await create_task(
                access_token="test_token",
                project_id="project_123",
                exec_position="EXECUTOR",
                params={"key": "value"},
            )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RPA_TASK_CREATE_URL": "https://api.example.com/create"})
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    async def test_create_task_request_error(self, mock_client_class: Any) -> None:
        """测试网络请求错误。"""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # 模拟网络请求错误
        mock_client.post.side_effect = httpx.RequestError("Network error")

        with pytest.raises(HTTPException) as exc_info:
            await create_task(
                access_token="test_token",
                project_id="project_123",
                exec_position="EXECUTOR",
                params={"key": "value"},
            )

        assert exc_info.value.status_code == 500
        assert "Network error" in exc_info.value.detail


class TestQueryTaskStatus:
    """query_task_status 函数的测试用例。"""

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RPA_TASK_QUERY_URL": "https://api.example.com/query"})
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    async def test_query_task_status_completed(self, mock_client_class: Any) -> None:
        """测试查询已完成的任务状态。"""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {
                "execution": {
                    "status": "COMPLETED",
                    "result": {"data": {"output": "task completed successfully"}},
                }
            },
        }
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response

        result = await query_task_status("test_token", "task_123")

        assert result is not None
        code, message, data = result
        assert code == ErrorCode.SUCCESS.code
        assert message == ErrorCode.SUCCESS.message
        assert data == {"output": "task completed successfully"}

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RPA_TASK_QUERY_URL": "https://api.example.com/query"})
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    async def test_query_task_status_failed(self, mock_client_class: Any) -> None:
        """测试查询失败的任务状态。"""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {
                "execution": {"status": "FAILED", "error": "Task execution failed"}
            },
        }
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response

        result = await query_task_status("test_token", "task_123")

        assert result is not None
        code, message, data = result
        assert code == ErrorCode.QUERY_TASK_ERROR.code
        assert "Task execution failed" in message
        assert data == {}

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RPA_TASK_QUERY_URL": "https://api.example.com/query"})
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    async def test_query_task_status_pending(self, mock_client_class: Any) -> None:
        """测试查询待处理的任务状态。"""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {"execution": {"status": "PENDING"}},
        }
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response

        result = await query_task_status("test_token", "task_123")

        assert result is None

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RPA_TASK_QUERY_URL": "invalid_url"})
    async def test_query_task_status_invalid_url(self) -> None:
        """测试无效的查询任务 URL。"""
        with pytest.raises(InvalidConfigException) as exc_info:
            await query_task_status("test_token", "task_123")

        assert "无效的任务查询 URL" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RPA_TASK_QUERY_URL": "https://api.example.com/query"})
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    async def test_query_task_status_api_error(self, mock_client_class: Any) -> None:
        """测试 API 返回错误响应。"""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "5000",
            "msg": "Internal server error",
            "data": None,
        }
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            await query_task_status("test_token", "task_123")

        assert exc_info.value.status_code == 500
        assert "查询任务状态失败" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RPA_TASK_QUERY_URL": "https://api.example.com/query"})
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    async def test_query_task_status_unknown_status(
        self, mock_client_class: Any
    ) -> None:
        """测试未知的任务状态。"""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {"execution": {"status": "UNKNOWN_STATUS"}},
        }
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            await query_task_status("test_token", "task_123")

        assert exc_info.value.status_code == 500
        assert "未知的任务状态" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RPA_TASK_QUERY_URL": "https://api.example.com/query"})
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    async def test_query_task_status_missing_execution(
        self, mock_client_class: Any
    ) -> None:
        """测试响应中缺少 execution 信息。"""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {},  # 缺少 execution 字段
        }
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            await query_task_status("test_token", "task_123")

        assert exc_info.value.status_code == 500
        assert "未返回任务信息" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RPA_TASK_QUERY_URL": "https://api.example.com/query"})
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    async def test_query_task_status_request_error(
        self, mock_client_class: Any
    ) -> None:
        """测试网络请求错误。"""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # 模拟网络请求错误
        mock_client.get.side_effect = httpx.RequestError("Network error")

        with pytest.raises(HTTPException) as exc_info:
            await query_task_status("test_token", "task_123")

        assert exc_info.value.status_code == 500
        assert "Network error" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RPA_TASK_QUERY_URL": "https://api.example.com/query"})
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    async def test_query_task_status_url_construction(
        self, mock_client_class: Any
    ) -> None:
        """测试查询 URL 的构造。"""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {"execution": {"status": "PENDING"}},
        }
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response

        await query_task_status("test_token", "task_123")

        # 验证请求 URL 和头部
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["url"] == "https://api.example.com/query/task_123"
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_token"
