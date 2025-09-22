"""测试任务处理模块。"""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException

from api.schemas.execution_dto import RPAExecutionResponse
from errors.error_code import ErrorCode
from exceptions.config_exceptions import InvalidConfigException
from service.xf_xiaowu.process import task_monitoring


class TestTaskMonitoring:
    """task_monitoring 函数的测试用例。"""

    @pytest.mark.asyncio
    @patch("service.xf_xiaowu.process.create_task")
    @patch("service.xf_xiaowu.process.query_task_status")
    @patch.dict(
        os.environ, {"RPA_TIMEOUT_KEY": "300", "RPA_TASK_QUERY_INTERVAL_KEY": "1"}
    )
    async def test_task_monitoring_success(
        self, mock_query_task: MagicMock, mock_create_task: MagicMock
    ) -> None:
        """测试任务监控成功完成的情况。"""
        # 模拟创建任务成功
        mock_create_task.return_value = "test_task_id_123"

        # 模拟查询任务状态返回成功
        mock_query_task.return_value = (
            ErrorCode.SUCCESS.code,
            "Task completed successfully",
            {"result": "finished", "output": "test_output"},
        )

        # 收集生成器输出
        results = []
        async for result in task_monitoring(
            sid="test_sid",
            access_token="test_token",
            project_id="test_project",
            exec_position="EXECUTOR",
            params={"key": "value"},
        ):
            results.append(result)

        # 验证结果
        assert len(results) == 1
        response = RPAExecutionResponse.model_validate_json(results[0])
        assert response.code == ErrorCode.SUCCESS.code
        assert response.message == "Task completed successfully"
        assert response.sid == "test_sid"
        assert response.data == {"result": "finished", "output": "test_output"}

        # 验证调用
        mock_create_task.assert_called_once_with(
            access_token="test_token",
            project_id="test_project",
            exec_position="EXECUTOR",
            params={"key": "value"},
        )
        mock_query_task.assert_called_with("test_token", "test_task_id_123")

    @pytest.mark.asyncio
    @patch("service.xf_xiaowu.process.create_task")
    @patch.dict(
        os.environ, {"RPA_TIMEOUT_KEY": "300", "RPA_TASK_QUERY_INTERVAL_KEY": "1"}
    )
    async def test_task_monitoring_create_task_error(
        self, mock_create_task: MagicMock
    ) -> None:
        """测试创建任务失败的情况。"""
        # 模拟创建任务失败
        mock_create_task.side_effect = HTTPException(
            status_code=400, detail="Bad request"
        )

        # 收集生成器输出
        results = []
        async for result in task_monitoring(
            sid="test_sid",
            access_token="test_token",
            project_id="test_project",
            exec_position="EXECUTOR",
            params={"key": "value"},
        ):
            results.append(result)

        # 验证结果
        assert len(results) == 1
        response = RPAExecutionResponse.model_validate_json(results[0])
        assert response.code == ErrorCode.CREATE_TASK_ERROR.code
        assert ErrorCode.CREATE_TASK_ERROR.message in response.message
        assert response.sid == "test_sid"

    @pytest.mark.asyncio
    @patch("service.xf_xiaowu.process.create_task")
    @patch.dict(
        os.environ, {"RPA_TIMEOUT_KEY": "300", "RPA_TASK_QUERY_INTERVAL_KEY": "1"}
    )
    async def test_task_monitoring_invalid_config_error(
        self, mock_create_task: MagicMock
    ) -> None:
        """测试配置无效错误的情况。"""
        # 模拟配置错误
        mock_create_task.side_effect = InvalidConfigException("Invalid configuration")

        # 收集生成器输出
        results = []
        async for result in task_monitoring(
            sid="test_sid",
            access_token="test_token",
            project_id="test_project",
            exec_position="EXECUTOR",
            params={"key": "value"},
        ):
            results.append(result)

        # 验证结果
        assert len(results) == 1
        response = RPAExecutionResponse.model_validate_json(results[0])
        assert response.code == ErrorCode.CREATE_TASK_ERROR.code
        assert "Invalid configuration" in response.message

    @pytest.mark.asyncio
    @patch("service.xf_xiaowu.process.create_task")
    @patch("service.xf_xiaowu.process.query_task_status")
    @patch.dict(
        os.environ, {"RPA_TIMEOUT_KEY": "2", "RPA_TASK_QUERY_INTERVAL_KEY": "1"}
    )
    async def test_task_monitoring_timeout(
        self, mock_query_task: MagicMock, mock_create_task: MagicMock
    ) -> None:
        """测试任务监控超时的情况。"""
        # 模拟创建任务成功
        mock_create_task.return_value = "test_task_id_123"

        # 模拟查询任务状态一直返回 None（未完成）
        mock_query_task.return_value = None

        # 收集生成器输出
        results = []
        async for result in task_monitoring(
            sid="test_sid",
            access_token="test_token",
            project_id="test_project",
            exec_position="EXECUTOR",
            params={"key": "value"},
        ):
            results.append(result)

        # 验证结果
        assert len(results) == 1
        response = RPAExecutionResponse.model_validate_json(results[0])
        assert response.code == ErrorCode.TIMEOUT_ERROR.code
        assert response.message == ErrorCode.TIMEOUT_ERROR.message
        assert response.sid == "test_sid"

    @pytest.mark.asyncio
    @patch("service.xf_xiaowu.process.create_task")
    @patch("service.xf_xiaowu.process.query_task_status")
    @patch.dict(
        os.environ, {"RPA_TIMEOUT_KEY": "300", "RPA_TASK_QUERY_INTERVAL_KEY": "1"}
    )
    async def test_task_monitoring_query_error(
        self, mock_query_task: MagicMock, mock_create_task: MagicMock
    ) -> None:
        """测试查询任务状态错误的情况。"""
        # 模拟创建任务成功
        mock_create_task.return_value = "test_task_id_123"

        # 模拟查询任务状态返回错误
        mock_query_task.return_value = (
            ErrorCode.QUERY_TASK_ERROR.code,
            "Query task failed",
            None,
        )

        # 收集生成器输出
        results = []
        async for result in task_monitoring(
            sid="test_sid",
            access_token="test_token",
            project_id="test_project",
            exec_position="EXECUTOR",
            params={"key": "value"},
        ):
            results.append(result)

        # 验证结果
        assert len(results) == 1
        response = RPAExecutionResponse.model_validate_json(results[0])
        assert response.code == ErrorCode.QUERY_TASK_ERROR.code
        assert response.message == "Query task failed"
        assert response.sid == "test_sid"

    @pytest.mark.asyncio
    @patch("service.xf_xiaowu.process.create_task")
    @patch.dict(
        os.environ, {"RPA_TIMEOUT_KEY": "300", "RPA_TASK_QUERY_INTERVAL_KEY": "1"}
    )
    async def test_task_monitoring_httpx_error(
        self, mock_create_task: MagicMock
    ) -> None:
        """测试 httpx 相关错误的情况。"""
        # 模拟 httpx 错误
        mock_create_task.side_effect = httpx.HTTPStatusError(
            "Bad request", request=MagicMock(), response=MagicMock()
        )

        # 收集生成器输出
        results = []
        async for result in task_monitoring(
            sid="test_sid",
            access_token="test_token",
            project_id="test_project",
            exec_position="EXECUTOR",
            params={"key": "value"},
        ):
            results.append(result)

        # 验证结果
        assert len(results) == 1
        response = RPAExecutionResponse.model_validate_json(results[0])
        assert response.code == ErrorCode.CREATE_TASK_ERROR.code

    @pytest.mark.asyncio
    @patch("service.xf_xiaowu.process.create_task")
    @patch.dict(
        os.environ, {"RPA_TIMEOUT_KEY": "300", "RPA_TASK_QUERY_INTERVAL_KEY": "1"}
    )
    async def test_task_monitoring_request_error(
        self, mock_create_task: MagicMock
    ) -> None:
        """测试网络请求错误的情况。"""
        # 模拟网络请求错误
        mock_create_task.side_effect = httpx.RequestError("Network error")

        # 收集生成器输出
        results = []
        async for result in task_monitoring(
            sid="test_sid",
            access_token="test_token",
            project_id="test_project",
            exec_position="EXECUTOR",
            params={"key": "value"},
        ):
            results.append(result)

        # 验证结果
        assert len(results) == 1
        response = RPAExecutionResponse.model_validate_json(results[0])
        assert response.code == ErrorCode.CREATE_TASK_ERROR.code

    @pytest.mark.asyncio
    @patch("service.xf_xiaowu.process.create_task")
    @patch("service.xf_xiaowu.process.query_task_status")
    @patch.dict(
        os.environ, {"RPA_TIMEOUT_KEY": "300", "RPA_TASK_QUERY_INTERVAL_KEY": "1"}
    )
    async def test_task_monitoring_with_none_params(
        self, mock_query_task: MagicMock, mock_create_task: MagicMock
    ) -> None:
        """测试 params 为 None 的情况。"""
        # 模拟创建任务成功
        mock_create_task.return_value = "test_task_id_123"

        # 模拟查询任务状态返回成功
        mock_query_task.return_value = (
            ErrorCode.SUCCESS.code,
            "Task completed successfully",
            {"result": "finished"},
        )

        # 收集生成器输出
        results = []
        async for result in task_monitoring(
            sid=None,  # sid 也可以是 None
            access_token="test_token",
            project_id="test_project",
            exec_position=None,
            params=None,
        ):
            results.append(result)

        # 验证结果
        assert len(results) == 1
        response = RPAExecutionResponse.model_validate_json(results[0])
        assert response.code == ErrorCode.SUCCESS.code
        assert response.sid is None or response.sid == ""

        # 验证调用参数
        mock_create_task.assert_called_once_with(
            access_token="test_token",
            project_id="test_project",
            exec_position=None,
            params=None,
        )
