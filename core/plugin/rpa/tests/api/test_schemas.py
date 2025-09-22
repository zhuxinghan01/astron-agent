"""测试 API schemas（DTO）模块。"""

import pytest
from pydantic import ValidationError

from api.schemas.execution_dto import RPAExecutionRequest, RPAExecutionResponse


class TestRPAExecutionRequest:
    """RPAExecutionRequest DTO 的测试用例。"""

    def test_valid_request_with_all_fields(self) -> None:
        """测试包含所有字段的有效请求。"""
        request_data = {
            "sid": "test_session_123",
            "project_id": "test_project_456",
            "exec_position": "EXECUTOR",
            "params": {"key1": "value1", "key2": "value2"},
        }
        request = RPAExecutionRequest(**request_data)  # type: ignore[arg-type]

        assert request.sid == "test_session_123"
        assert request.project_id == "test_project_456"
        assert request.exec_position == "EXECUTOR"
        assert request.params == {"key1": "value1", "key2": "value2"}

    def test_valid_request_minimal_fields(self) -> None:
        """测试只包含必需字段的有效请求。"""
        request_data = {"project_id": "test_project_456"}
        request = RPAExecutionRequest(**request_data)  # type: ignore[arg-type]

        assert request.sid == ""
        assert request.project_id == "test_project_456"
        assert request.exec_position == "EXECUTOR"
        assert request.params is None

    def test_invalid_request_missing_project_id(self) -> None:
        """测试缺少必需字段 project_id 的无效请求。"""
        request_data = {"sid": "test_session_123"}

        with pytest.raises(ValidationError) as exc_info:
            RPAExecutionRequest(**request_data)  # type: ignore[arg-type]

        assert "project_id" in str(exc_info.value)

    def test_request_with_empty_params(self) -> None:
        """测试 params 为空字典的请求。"""
        request_data = {"project_id": "test_project_456", "params": {}}
        request = RPAExecutionRequest(**request_data)  # type: ignore[arg-type]
        assert request.params == {}

    def test_request_with_none_params(self) -> None:
        """测试 params 为 None 的请求。"""
        request_data = {"project_id": "test_project_456", "params": None}
        request = RPAExecutionRequest(**request_data)  # type: ignore[arg-type]
        assert request.params is None


class TestRPAExecutionResponse:
    """RPAExecutionResponse DTO 的测试用例。"""

    def test_valid_response_with_all_fields(self) -> None:
        """测试包含所有字段的有效响应。"""
        response_data = {
            "code": 200,
            "message": "Success",
            "sid": "test_session_123",
            "data": {"result": "completed", "task_id": "task_456"},
        }
        response = RPAExecutionResponse(**response_data)  # type: ignore[arg-type]

        assert response.code == 200
        assert response.message == "Success"
        assert response.sid == "test_session_123"
        assert response.data == {"result": "completed", "task_id": "task_456"}

    def test_valid_response_minimal_fields(self) -> None:
        """测试只包含必需字段的有效响应。"""
        response_data = {"code": 500, "message": "Internal Server Error"}
        response = RPAExecutionResponse(**response_data)  # type: ignore[arg-type]

        assert response.code == 500
        assert response.message == "Internal Server Error"
        assert response.sid == ""
        assert response.data is None

    def test_invalid_response_missing_code(self) -> None:
        """测试缺少必需字段 code 的无效响应。"""
        response_data = {"message": "Success"}

        with pytest.raises(ValidationError) as exc_info:
            RPAExecutionResponse(**response_data)  # type: ignore[arg-type]

        assert "code" in str(exc_info.value)

    def test_invalid_response_missing_message(self) -> None:
        """测试缺少必需字段 message 的无效响应。"""
        response_data = {"code": 200}

        with pytest.raises(ValidationError) as exc_info:
            RPAExecutionResponse(**response_data)  # type: ignore[arg-type]

        assert "message" in str(exc_info.value)

    def test_response_model_dump_json(self) -> None:
        """测试响应对象转换为 JSON 字符串。"""
        response_data = {
            "code": 200,
            "message": "Success",
            "sid": "test_session_123",
            "data": {"result": "completed"},
        }
        response = RPAExecutionResponse(**response_data)  # type: ignore[arg-type]
        json_str = response.model_dump_json()

        assert isinstance(json_str, str)
        assert "200" in json_str
        assert "Success" in json_str
        assert "test_session_123" in json_str
