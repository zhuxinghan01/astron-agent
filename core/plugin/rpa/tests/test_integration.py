"""集成测试模块。

测试各个模块之间的集成和端到端功能。
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from api.app import xingchen_rap_server_app


class TestRPAIntegration:
    """RPA 系统集成测试。"""

    @pytest.fixture
    def integration_client(self) -> TestClient:
        """创建集成测试客户端。"""
        app = xingchen_rap_server_app()
        return TestClient(app)

    @pytest.mark.integration
    @patch.dict(
        os.environ,
        {
            "RPA_TASK_CREATE_URL": "https://api.example.com/create",
            "RPA_TASK_QUERY_URL": "https://api.example.com/query",
            "RPA_TIMEOUT": "300",
            "RPA_TASK_QUERY_INTERVAL": "1",
        },
    )
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    def test_complete_rpa_execution_flow_success(
        self, mock_client_class: MagicMock, integration_client: TestClient
    ) -> None:
        """测试完整的 RPA 执行流程 - 成功场景。"""
        # 模拟 HTTP 客户端
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # 模拟创建任务响应
        create_response = MagicMock()
        create_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {"executionId": "integration_task_123"},
        }
        create_response.raise_for_status.return_value = None

        # 模拟查询任务响应 - 完成状态
        query_response = MagicMock()
        query_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {
                "execution": {
                    "status": "COMPLETED",
                    "result": {
                        "data": {
                            "output": "Integration test completed successfully",
                            "execution_time": "30.5s",
                        }
                    },
                }
            },
        }
        query_response.raise_for_status.return_value = None

        # 设置 mock 响应序列
        mock_client.post.return_value = create_response
        mock_client.get.return_value = query_response

        # 执行集成测试请求
        request_data = {
            "project_id": "integration_project_123",
            "exec_position": "EXECUTOR",
            "params": {"test_param": "integration_value", "mode": "test"},
            "sid": "integration_session_456",
        }

        response = integration_client.post(
            "/rpa/v1/exec",
            headers={"Authorization": "Bearer integration_test_token"},
            json=request_data,
        )

        # 验证响应
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

        # 验证创建任务调用
        mock_client.post.assert_called_once()
        create_call = mock_client.post.call_args
        assert "https://api.example.com/create" in create_call[0]
        assert (
            create_call[1]["headers"]["Authorization"]
            == "Bearer integration_test_token"
        )

        request_body = create_call[1]["json"]
        assert request_body["project_id"] == "integration_project_123"
        assert request_body["exec_position"] == "EXECUTOR"
        assert request_body["params"]["test_param"] == "integration_value"

        # 验证查询任务调用
        mock_client.get.assert_called()
        query_call = mock_client.get.call_args
        assert (
            query_call[1]["url"] == "https://api.example.com/query/integration_task_123"
        )

    @pytest.mark.integration
    @patch.dict(
        os.environ,
        {
            "RPA_TASK_CREATE_URL": "https://api.example.com/create",
            "RPA_TASK_QUERY_URL": "https://api.example.com/query",
            "RPA_TIMEOUT": "2",
            "RPA_TASK_QUERY_INTERVAL": "1",
        },
    )
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    def test_complete_rpa_execution_flow_timeout(
        self, mock_client_class: MagicMock, integration_client: TestClient
    ) -> None:
        """测试完整的 RPA 执行流程 - 超时场景。"""
        # 模拟 HTTP 客户端
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # 模拟创建任务响应
        create_response = MagicMock()
        create_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {"executionId": "timeout_task_123"},
        }
        create_response.raise_for_status.return_value = None

        # 模拟查询任务响应 - 一直处于待处理状态
        query_response = MagicMock()
        query_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {"execution": {"status": "PENDING"}},
        }
        query_response.raise_for_status.return_value = None

        mock_client.post.return_value = create_response
        mock_client.get.return_value = query_response

        # 执行请求
        request_data = {
            "project_id": "timeout_project_123",
            "sid": "timeout_session_456",
        }

        response = integration_client.post(
            "/rpa/v1/exec",
            headers={"Authorization": "Bearer timeout_test_token"},
            json=request_data,
        )

        # 验证响应（超时应该返回事件流）
        assert response.status_code == 200

    @pytest.mark.integration
    @patch.dict(
        os.environ,
        {
            "RPA_TASK_CREATE_URL": "invalid_url",
        },
    )
    def test_integration_invalid_configuration(
        self, integration_client: TestClient
    ) -> None:
        """测试集成场景下的无效配置。"""
        request_data = {
            "project_id": "config_error_project",
            "sid": "config_error_session",
        }

        response = integration_client.post(
            "/rpa/v1/exec",
            headers={"Authorization": "Bearer config_error_token"},
            json=request_data,
        )

        # 应该返回事件流，但内容包含配置错误
        assert response.status_code == 200

    @pytest.mark.integration
    @patch.dict(
        os.environ,
        {
            "RPA_TASK_CREATE_URL": "https://api.example.com/create",
            "RPA_TASK_QUERY_URL": "https://api.example.com/query",
            "RPA_TIMEOUT": "300",
            "RPA_TASK_QUERY_INTERVAL": "1",
        },
    )
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    def test_integration_task_failure_flow(
        self, mock_client_class: MagicMock, integration_client: TestClient
    ) -> None:
        """测试任务失败的集成流程。"""
        # 模拟 HTTP 客户端
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # 模拟创建任务响应
        create_response = MagicMock()
        create_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {"executionId": "failure_task_123"},
        }
        create_response.raise_for_status.return_value = None

        # 模拟查询任务响应 - 失败状态
        query_response = MagicMock()
        query_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {
                "execution": {
                    "status": "FAILED",
                    "error": "Task execution failed due to network error",
                }
            },
        }
        query_response.raise_for_status.return_value = None

        mock_client.post.return_value = create_response
        mock_client.get.return_value = query_response

        # 执行请求
        request_data = {
            "project_id": "failure_project_123",
            "sid": "failure_session_456",
        }

        response = integration_client.post(
            "/rpa/v1/exec",
            headers={"Authorization": "Bearer failure_test_token"},
            json=request_data,
        )

        # 验证响应
        assert response.status_code == 200

    @pytest.mark.integration
    def test_integration_invalid_request_format(
        self, integration_client: TestClient
    ) -> None:
        """测试无效请求格式的集成场景。"""
        # 缺少必需的 project_id
        invalid_request = {"exec_position": "EXECUTOR", "params": {"key": "value"}}

        response = integration_client.post(
            "/rpa/v1/exec",
            headers={"Authorization": "Bearer test_token"},
            json=invalid_request,
        )

        # 应该返回验证错误
        assert response.status_code == 422

    @pytest.mark.integration
    def test_integration_missing_authorization_header(
        self, integration_client: TestClient
    ) -> None:
        """测试缺少授权头的集成场景。"""
        request_data = {"project_id": "unauthorized_project"}

        response = integration_client.post(
            "/rpa/v1/exec",
            json=request_data,
            # 缺少 Authorization 头
        )

        # 应该返回验证错误
        assert response.status_code == 422

    @pytest.mark.integration
    @patch.dict(
        os.environ,
        {
            "RPA_TASK_CREATE_URL": "https://api.example.com/create",
            "RPA_TIMEOUT": "300",
            "RPA_TASK_QUERY_INTERVAL": "1",
        },
    )
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    def test_integration_network_error_handling(
        self, mock_client_class: MagicMock, integration_client: TestClient
    ) -> None:
        """测试网络错误处理的集成场景。"""
        # 模拟 HTTP 客户端
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # 模拟网络错误
        mock_client.post.side_effect = httpx.RequestError("Network connection failed")

        request_data = {
            "project_id": "network_error_project",
            "sid": "network_error_session",
        }

        response = integration_client.post(
            "/rpa/v1/exec",
            headers={"Authorization": "Bearer network_error_token"},
            json=request_data,
        )

        # 应该返回事件流，内容包含网络错误
        assert response.status_code == 200

    @pytest.mark.integration
    def test_integration_app_creation(self) -> None:
        """测试应用创建的集成。"""
        app = xingchen_rap_server_app()

        # 验证应用创建成功
        assert app is not None

        # 验证路由注册
        routes = app.routes
        assert any(
            "/rpa/v1/exec" in getattr(route, "path", str(route)) for route in routes
        )

    @pytest.mark.integration
    @patch.dict(
        os.environ,
        {
            "RPA_TASK_CREATE_URL": "https://api.example.com/create",
            "RPA_TASK_QUERY_URL": "https://api.example.com/query",
            "RPA_TIMEOUT": "300",
            "RPA_TASK_QUERY_INTERVAL": "1",
            "RPA_PING_INTERVAL": "30",
        },
    )
    @patch("infra.xf_xiaowu.tatks.httpx.AsyncClient")
    def test_integration_response_headers_and_streaming(
        self, mock_client_class: MagicMock, integration_client: TestClient
    ) -> None:
        """测试响应头和流式传输的集成。"""
        # 模拟 HTTP 客户端
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # 模拟创建任务响应
        create_response = MagicMock()
        create_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {"executionId": "stream_task_123"},
        }
        create_response.raise_for_status.return_value = None
        mock_client.post.return_value = create_response

        # 模拟查询任务响应
        query_response = MagicMock()
        query_response.json.return_value = {
            "code": "0000",
            "msg": "Success",
            "data": {
                "execution": {
                    "status": "COMPLETED",
                    "result": {"data": {"result": "streaming test"}},
                }
            },
        }
        query_response.raise_for_status.return_value = None
        mock_client.get.return_value = query_response

        request_data = {"project_id": "streaming_project", "sid": "streaming_session"}

        response = integration_client.post(
            "/rpa/v1/exec",
            headers={"Authorization": "Bearer streaming_token"},
            json=request_data,
        )

        # 验证流式响应头
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

    @pytest.mark.integration
    def test_integration_bearer_token_formats(
        self, integration_client: TestClient
    ) -> None:
        """测试不同 Bearer token 格式的集成。"""
        request_data = {"project_id": "token_test_project"}

        # 测试标准 Bearer 格式
        response1 = integration_client.post(
            "/rpa/v1/exec",
            headers={"Authorization": "Bearer standard_token"},
            json=request_data,
        )
        assert response1.status_code == 200

        # 测试无 Bearer 前缀格式
        response2 = integration_client.post(
            "/rpa/v1/exec", headers={"Authorization": "plain_token"}, json=request_data
        )
        assert response2.status_code == 200
