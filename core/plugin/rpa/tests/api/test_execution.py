"""测试 RPA 执行 API 路由。"""

import json
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from api.schemas.execution_dto import RPAExecutionRequest, RPAExecutionResponse


class TestExecutionAPI:
    """RPA 执行 API 的测试用例。"""

    def test_exec_endpoint_exists(self, client: TestClient) -> None:
        """测试 /rpa/v1/exec 端点存在。"""
        response = client.post(
            "/rpa/v1/exec",
            headers={"Authorization": "Bearer test_token"},
            json={"project_id": "test_project"},
        )
        # 不期望 404 错误，任何其他错误都表明端点存在
        assert response.status_code != 404

    @patch("api.v1.execution.task_monitoring")
    def test_exec_valid_request(
        self, mock_task_monitoring: MagicMock, client: TestClient
    ) -> None:
        """测试有效的执行请求。"""

        # 模拟异步生成器
        async def mock_generator() -> AsyncGenerator[str, None]:
            yield '{"code": 200, "message": "Success"}'

        mock_task_monitoring.return_value = mock_generator()

        request_data = {
            "project_id": "test_project_123",
            "exec_position": "EXECUTOR",
            "params": {"key": "value"},
            "sid": "test_session",
        }

        response = client.post(
            "/rpa/v1/exec",
            headers={"Authorization": "Bearer test_token_123"},
            json=request_data,
        )

        # 验证调用参数
        mock_task_monitoring.assert_called_once()
        call_args = mock_task_monitoring.call_args
        assert call_args.kwargs["sid"] == "test_session"
        assert call_args.kwargs["access_token"] == "test_token_123"
        assert call_args.kwargs["project_id"] == "test_project_123"
        assert call_args.kwargs["exec_position"] == "EXECUTOR"
        assert call_args.kwargs["params"] == {"key": "value"}

    @patch("api.v1.execution.task_monitoring")
    def test_exec_bearer_token_parsing(
        self, mock_task_monitoring: MagicMock, client: TestClient
    ) -> None:
        """测试 Bearer token 解析。"""

        async def mock_generator() -> AsyncGenerator[str, None]:
            yield '{"code": 200, "message": "Success"}'

        mock_task_monitoring.return_value = mock_generator()

        request_data = {"project_id": "test_project_123"}

        # 测试带 Bearer 前缀的 token
        response = client.post(
            "/rpa/v1/exec",
            headers={"Authorization": "Bearer my_secret_token"},
            json=request_data,
        )

        call_args = mock_task_monitoring.call_args
        assert call_args.kwargs["access_token"] == "my_secret_token"

    @patch("api.v1.execution.task_monitoring")
    def test_exec_plain_token(
        self, mock_task_monitoring: MagicMock, client: TestClient
    ) -> None:
        """测试不带 Bearer 前缀的 token。"""

        async def mock_generator() -> AsyncGenerator[str, None]:
            yield '{"code": 200, "message": "Success"}'

        mock_task_monitoring.return_value = mock_generator()

        request_data = {"project_id": "test_project_123"}

        # 测试不带 Bearer 前缀的 token
        response = client.post(
            "/rpa/v1/exec", headers={"Authorization": "plain_token"}, json=request_data
        )

        call_args = mock_task_monitoring.call_args
        assert call_args.kwargs["access_token"] == "plain_token"

    def test_exec_missing_authorization_header(self, client: TestClient) -> None:
        """测试缺少 Authorization 头的请求。"""
        request_data = {"project_id": "test_project_123"}

        response = client.post("/rpa/v1/exec", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_exec_invalid_request_body(self, client: TestClient) -> None:
        """测试无效的请求体。"""
        # 缺少必需的 project_id
        response = client.post(
            "/rpa/v1/exec",
            headers={"Authorization": "Bearer test_token"},
            json={"sid": "test_session"},
        )
        assert response.status_code == 422

    @patch("api.v1.execution.task_monitoring")
    def test_exec_minimal_request(
        self, mock_task_monitoring: MagicMock, client: TestClient
    ) -> None:
        """测试最小化的有效请求。"""

        async def mock_generator() -> AsyncGenerator[str, None]:
            yield '{"code": 200, "message": "Success"}'

        mock_task_monitoring.return_value = mock_generator()

        request_data = {"project_id": "test_project_123"}

        response = client.post(
            "/rpa/v1/exec",
            headers={"Authorization": "Bearer test_token"},
            json=request_data,
        )

        call_args = mock_task_monitoring.call_args
        assert call_args.kwargs["project_id"] == "test_project_123"
        assert call_args.kwargs["sid"] == ""  # 默认值
        assert call_args.kwargs["exec_position"] == "EXECUTOR"  # 默认值
        assert call_args.kwargs["params"] is None  # 默认值

    @patch("api.v1.execution.task_monitoring")
    @patch("api.v1.execution.os.getenv")
    def test_exec_response_headers_and_ping(
        self,
        mock_getenv: MagicMock,
        mock_task_monitoring: MagicMock,
        client: TestClient,
    ) -> None:
        """测试响应头和 ping 间隔设置。"""
        mock_getenv.return_value = "30"  # RPA_PING_INTERVAL_KEY

        async def mock_generator() -> AsyncGenerator[str, None]:
            yield '{"code": 200, "message": "Success"}'

        mock_task_monitoring.return_value = mock_generator()

        request_data = {"project_id": "test_project_123"}

        with patch("api.v1.execution.EventSourceResponse") as mock_sse:
            response = client.post(
                "/rpa/v1/exec",
                headers={"Authorization": "Bearer test_token"},
                json=request_data,
            )

            # 验证 EventSourceResponse 被正确调用
            mock_sse.assert_called_once()
            call_args = mock_sse.call_args

            # 验证 headers 包含必要的字段
            headers = call_args.kwargs["headers"]
            assert "Content-Type" in headers
            assert headers["Content-Type"] == "text/event-stream; charset=utf-8"
            assert headers["Cache-Control"] == "no-cache, no-transform"
            assert headers["Connection"] == "keep-alive"

            # 验证 ping 间隔
            assert call_args.kwargs["ping"] == 30

    @patch("api.v1.execution.task_monitoring")
    def test_exec_exception_handling(
        self, mock_task_monitoring: MagicMock, client: TestClient
    ) -> None:
        """测试异常处理。"""
        # 模拟 task_monitoring 抛出异常
        mock_task_monitoring.side_effect = ValueError("Test error")

        request_data = {"project_id": "test_project_123"}

        response = client.post(
            "/rpa/v1/exec",
            headers={"Authorization": "Bearer test_token"},
            json=request_data,
        )

        assert response.status_code == 500
        assert "Test error" in response.json()["detail"]
