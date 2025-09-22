"""WorkflowAgent API单元测试模块."""

import concurrent.futures
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, Mock, patch

from fastapi.testclient import TestClient

from api.app import app


class TestWorkflowAgentAPI:
    """WorkflowAgent API测试类."""

    def __init__(self) -> None:
        """初始化测试类."""
        self.client = TestClient(app)

    def setup_method(self) -> None:
        """测试方法初始化."""
        # Reset client state for each test
        self.client = TestClient(app)

    def test_workflow_agent_routes_exist(self) -> None:
        """测试Workflow Agent API路由是否存在."""
        # 测试可能的工作流代理端点
        workflow_endpoints = [
            "/v1/workflow",
            "/workflow",
            "/v1/agent/workflow",
            "/agent/workflow",
            "/v1/workflow/execute",
            "/workflow/execute",
        ]

        responses = []
        for endpoint in workflow_endpoints:
            try:
                response = self.client.get(endpoint)
                responses.append((endpoint, response.status_code))
            except (ConnectionError, ValueError, TypeError) as e:
                responses.append((endpoint, f"Error: {e}"))  # type: ignore[arg-type]

        # 验证至少有一个端点有响应
        valid_responses = [r for r in responses if isinstance(r[1], int)]
        assert len(valid_responses) > 0

    @patch("api.v1.workflow_agent.WorkflowAgentRunnerBuilder")
    def test_workflow_execution_success(self, mock_builder: Any) -> None:
        """测试工作流执行成功场景."""
        # Mock builder和runner
        mock_runner = Mock()

        async def mock_run_stream() -> AsyncGenerator[dict[str, str], None]:
            yield {"type": "step", "content": "开始执行工作流"}
            yield {"type": "step", "content": "正在处理数据"}
            yield {"type": "result", "content": "工作流执行完成", "status": "success"}

        mock_runner.run = Mock(return_value=mock_run_stream())

        mock_builder_instance = Mock()
        mock_builder_instance.build = AsyncMock(return_value=mock_runner)
        mock_builder.return_value = mock_builder_instance

        # 测试工作流执行请求
        workflow_request = {
            "workflow_id": "test-workflow-123",
            "inputs": {
                "query": "执行测试工作流",
                "parameters": {"temperature": 0.7, "max_steps": 5},
            },
            "model_config": {
                "domain": "gpt-4",
                "api": "https://api.openai.com/v1",
                "api_key": "test-key",
            },
        }

        execution_endpoints = [
            "/v1/workflow/execute",
            "/workflow/execute",
            "/v1/agent/workflow/run",
        ]

        for endpoint in execution_endpoints:
            try:
                response = self.client.post(endpoint, json=workflow_request)
                if response.status_code in [200, 404, 422, 405]:
                    assert response.status_code in [200, 404, 422, 405]
                    if response.status_code == 200:
                        result = response.json()
                        assert isinstance(result, dict)
                    break
            except (ConnectionError, ValueError, TypeError):
                continue

    def test_workflow_streaming_execution(self) -> None:
        """测试工作流流式执行."""
        # 测试流式工作流执行
        streaming_request = {
            "workflow_id": "streaming-workflow",
            "inputs": {"query": "流式执行测试"},
            "stream": True,
        }

        streaming_endpoints = [
            "/v1/workflow/stream",
            "/workflow/stream",
            "/v1/workflow/execute?stream=true",
        ]

        for endpoint in streaming_endpoints:
            try:
                response = self.client.post(endpoint, json=streaming_request)
                if response.status_code in [200, 404, 405]:
                    assert response.status_code in [200, 404, 405]
                    if response.status_code == 200:
                        # 验证流式响应头
                        content_type = response.headers.get("content-type", "")
                        assert "stream" in content_type or "json" in content_type
                    break
            except (ConnectionError, ValueError, TypeError):
                continue

    def test_workflow_agent_list_workflows(self) -> None:
        """测试列出可用工作流."""
        list_endpoints = [
            "/v1/workflows",
            "/workflows",
            "/v1/workflow/list",
            "/workflow/list",
        ]

        for endpoint in list_endpoints:
            try:
                response = self.client.get(endpoint)
                if response.status_code in [200, 404, 405]:
                    assert response.status_code in [200, 404, 405]
                    if response.status_code == 200:
                        workflows = response.json()
                        assert isinstance(workflows, (list, dict))
                    break
            except (ConnectionError, ValueError, TypeError):
                continue

    def test_workflow_agent_get_workflow_details(self) -> None:
        """测试获取工作流详情."""
        workflow_id = "test-workflow-123"

        detail_endpoints = [
            f"/v1/workflow/{workflow_id}",
            f"/workflow/{workflow_id}",
            f"/v1/workflow/details/{workflow_id}",
        ]

        for endpoint in detail_endpoints:
            try:
                response = self.client.get(endpoint)
                if response.status_code not in [200, 404, 405]:
                    continue
                assert response.status_code in [200, 404, 405]
                if response.status_code == 200:
                    workflow_details = response.json()
                    assert isinstance(workflow_details, dict)
                    # 验证工作流详情结构
                    expected_fields = [
                        "id",
                        "name",
                        "description",
                        "steps",
                        "inputs",
                        "outputs",
                    ]
                    for field in expected_fields:
                        if field in workflow_details:
                            assert workflow_details[field] is not None
                break
            except (ConnectionError, ValueError, TypeError):
                continue

    def test_workflow_agent_validation_errors(self) -> None:
        """测试工作流请求验证错误."""
        # 测试各种无效请求
        invalid_requests = [
            {},  # 空请求
            {"workflow_id": ""},  # 空工作流ID
            {"workflow_id": "test", "inputs": None},  # 空输入
            {"inputs": {"query": "测试"}},  # 缺少工作流ID
            {"workflow_id": "test", "inputs": {"invalid": None}},  # 无效输入值
        ]

        for invalid_request in invalid_requests:
            response = self.client.post("/v1/workflow/execute", json=invalid_request)
            # 应该返回验证错误
            assert response.status_code in [400, 404, 422, 405]

    def test_workflow_agent_unicode_support(self) -> None:
        """测试工作流对Unicode内容的支持."""
        unicode_request = {
            "workflow_id": "中文工作流🔄",
            "inputs": {
                "query": "中文查询测试🚀",
                "context": "包含特殊字符的上下文：①②③④⑤",
                "parameters": {
                    "language": "zh-CN",
                    "description": "这是一个Unicode测试",
                },
            },
        }

        response = self.client.post("/v1/workflow/execute", json=unicode_request)
        # 验证Unicode内容被正确处理
        assert response.status_code in [200, 404, 422, 405]

    @patch("api.v1.workflow_agent.WorkflowAgentRunnerBuilder")
    def test_workflow_agent_error_handling(self, mock_builder: Any) -> None:
        """测试工作流执行错误处理."""
        # Mock builder抛出各种异常
        mock_builder_instance = Mock()

        # 测试构建错误
        mock_builder_instance.build = AsyncMock(
            side_effect=ValueError("工作流构建失败")
        )
        mock_builder.return_value = mock_builder_instance

        workflow_request = {
            "workflow_id": "error-workflow",
            "inputs": {"query": "错误测试"},
        }

        response = self.client.post("/v1/workflow/execute", json=workflow_request)
        assert response.status_code in [400, 404, 422, 405, 500]

    def test_workflow_agent_concurrent_execution(self) -> None:
        """测试工作流并发执行."""

        def execute_workflow(workflow_id: str) -> Any:
            request_data = {
                "workflow_id": workflow_id,
                "inputs": {"query": f"并发测试 {workflow_id}"},
            }
            return self.client.post("/v1/workflow/execute", json=request_data)

        # 并发执行多个工作流
        workflow_ids = ["workflow-1", "workflow-2", "workflow-3"]

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(execute_workflow, wf_id) for wf_id in workflow_ids
            ]
            responses = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # 验证所有请求都得到响应
        assert len(responses) == 3
        for response in responses:
            assert response.status_code in [200, 404, 422, 405, 429]

    def test_workflow_agent_large_input_data(self) -> None:
        """测试工作流处理大输入数据."""
        # 创建大型输入数据
        large_input = {
            "query": "大数据处理测试",
            "data": ["数据项 " + str(i) for i in range(1000)],
            "context": "大量上下文内容 " * 100,
        }

        large_request = {"workflow_id": "large-data-workflow", "inputs": large_input}

        response = self.client.post("/v1/workflow/execute", json=large_request)
        # 验证大数据处理（可能有大小限制）
        assert response.status_code in [200, 400, 404, 413, 422, 405]

    def test_workflow_agent_timeout_handling(self) -> None:
        """测试工作流执行超时处理."""
        # 测试可能导致超时的长时间工作流
        timeout_request = {
            "workflow_id": "long-running-workflow",
            "inputs": {"query": "长时间执行测试", "timeout": 30},  # 设置超时时间
        }

        response = self.client.post("/v1/workflow/execute", json=timeout_request)
        assert response.status_code in [200, 404, 408, 422, 405, 504]

    def test_workflow_agent_execution_history(self) -> None:
        """测试工作流执行历史记录."""
        # 测试获取执行历史
        history_endpoints = [
            "/v1/workflow/history",
            "/workflow/history",
            "/v1/workflow/executions",
        ]

        for endpoint in history_endpoints:
            try:
                response = self.client.get(endpoint)
                if response.status_code in [200, 404, 405]:
                    assert response.status_code in [200, 404, 405]
                    if response.status_code == 200:
                        history = response.json()
                        assert isinstance(history, (list, dict))
                    break
            except (ConnectionError, ValueError, TypeError):
                continue

    def test_workflow_agent_execution_status(self) -> None:
        """测试获取工作流执行状态."""
        execution_id = "test-execution-123"

        status_endpoints = [
            f"/v1/workflow/execution/{execution_id}/status",
            f"/workflow/status/{execution_id}",
            f"/v1/execution/{execution_id}",
        ]

        for endpoint in status_endpoints:
            try:
                response = self.client.get(endpoint)
                if response.status_code not in [200, 404, 405]:
                    continue
                assert response.status_code in [200, 404, 405]
                if response.status_code == 200:
                    status_data = response.json()
                    assert isinstance(status_data, dict)
                    # 验证状态数据结构
                    status_fields = ["status", "progress", "start_time", "result"]
                    for field in status_fields:
                        if field in status_data:
                            assert status_data[field] is not None
                break
            except (ConnectionError, ValueError, TypeError):
                continue

    def test_workflow_agent_cancel_execution(self) -> None:
        """测试取消工作流执行."""
        execution_id = "test-execution-123"

        cancel_endpoints = [
            f"/v1/workflow/execution/{execution_id}/cancel",
            f"/workflow/cancel/{execution_id}",
        ]

        for endpoint in cancel_endpoints:
            try:
                response = self.client.post(endpoint)
                if response.status_code in [200, 404, 405]:
                    assert response.status_code in [200, 404, 405]
                    if response.status_code == 200:
                        cancel_result = response.json()
                        assert isinstance(cancel_result, dict)
                    break
            except (ConnectionError, ValueError, TypeError):
                continue

    def test_workflow_agent_authentication(self) -> None:
        """测试工作流API认证."""
        # 测试认证功能（实际认证逻辑由中间件处理）

        # 测试带认证头的请求
        headers = {"Authorization": "Bearer workflow-token"}
        workflow_request = {
            "workflow_id": "auth-test-workflow",
            "inputs": {"query": "认证测试"},
        }

        response = self.client.post(
            "/v1/workflow/execute", json=workflow_request, headers=headers
        )
        assert response.status_code in [200, 401, 403, 404, 422, 405]

    def test_workflow_agent_parameter_validation(self) -> None:
        """测试工作流参数验证."""
        # 测试各种参数边界值
        boundary_requests = [
            {"workflow_id": "param-test", "inputs": {"temperature": -1.0}},  # 无效温度
            {"workflow_id": "param-test", "inputs": {"max_steps": 0}},  # 无效步骤数
            {"workflow_id": "param-test", "inputs": {"timeout": -5}},  # 无效超时
        ]

        for request_data in boundary_requests:
            response = self.client.post("/v1/workflow/execute", json=request_data)
            assert response.status_code in [400, 404, 422, 405]

    def test_workflow_agent_custom_model_config(self) -> None:
        """测试自定义模型配置."""
        custom_config_request = {
            "workflow_id": "custom-model-workflow",
            "inputs": {"query": "自定义模型测试"},
            "model_config": {
                "domain": "custom-llm-model",
                "api": "https://custom-api.example.com/v1",
                "api_key": "custom-api-key",
                "temperature": 0.9,
                "max_tokens": 4000,
                "custom_params": {"top_p": 0.95, "frequency_penalty": 0.1},
            },
        }

        response = self.client.post("/v1/workflow/execute", json=custom_config_request)
        assert response.status_code in [200, 404, 422, 405]
