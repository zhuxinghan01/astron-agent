"""基础LLM模型单元测试模块."""

import asyncio
from typing import Any, AsyncIterator, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from domain.models.base import BaseLLMModel


class TestBaseLLMModel:
    """BaseLLMModel测试类."""

    def setup_method(self) -> None:
        """测试方法初始化."""
        # 创建mock AsyncOpenAI客户端
        self.mock_llm = AsyncMock()  # pylint: disable=attribute-defined-outside-init
        self.model_name = "test_model"  # pylint: disable=attribute-defined-outside-init

        # 使用model_construct绕过Pydantic验证
        self.model = BaseLLMModel.model_construct(  # pylint: disable=attribute-defined-outside-init
            name=self.model_name, llm=self.mock_llm
        )

    def test_model_initialization(self) -> None:
        """测试模型初始化."""
        assert self.model.name == self.model_name
        assert self.model.llm == self.mock_llm

    def test_model_config(self) -> None:
        """测试模型配置."""
        # 验证配置允许任意类型
        # 验证模型配置存在
        assert hasattr(BaseLLMModel, "model_config")

    @pytest.mark.asyncio
    async def test_create_completion_success(self) -> None:
        """测试成功创建completion."""
        test_messages = [{"role": "user", "content": "test message"}]
        test_stream = True
        expected_response = Mock()

        # Mock OpenAI客户端调用
        self.mock_llm.chat.completions.create = AsyncMock(
            return_value=expected_response
        )

        with patch("domain.models.base.agent_config") as mock_config:
            mock_config.default_llm_timeout = 60
            mock_config.default_llm_max_token = 10000

            result = await self.model.create_completion(test_messages, test_stream)

            # 验证结果
            assert result == expected_response

            # 验证调用参数
            self.mock_llm.chat.completions.create.assert_called_once_with(
                messages=test_messages,
                stream=test_stream,
                model=self.model_name,
                timeout=60,
                max_tokens=10000,
            )

    @pytest.mark.asyncio
    @patch("domain.models.base.BaseLLMModel.create_completion", new_callable=AsyncMock)
    async def test_stream_success_without_span(self, mock_create: AsyncMock) -> None:
        """测试无span的流式处理成功."""
        test_messages = [{"role": "user", "content": "test message"}]
        test_stream = True

        # Mock chunk数据
        mock_chunk1 = Mock()
        mock_chunk1.model_dump.return_value = {"code": 0, "content": "chunk1"}
        mock_chunk1.model_dump_json.return_value = '{"content": "chunk1"}'

        mock_chunk2 = Mock()
        mock_chunk2.model_dump.return_value = {"code": 0, "content": "chunk2"}
        mock_chunk2.model_dump_json.return_value = '{"content": "chunk2"}'

        # Mock异步迭代器
        async def mock_response_iterator() -> AsyncIterator[Mock]:
            yield mock_chunk1
            yield mock_chunk2

        mock_response = AsyncMock()
        mock_response.__aiter__ = AsyncMock(return_value=mock_response_iterator())

        mock_create.return_value = mock_response_iterator()

        # 收集流式结果
        results = []
        async for chunk in self.model.stream(test_messages, test_stream, None):
            results.append(chunk)

        # 验证结果
        assert len(results) == 2
        assert results[0] == mock_chunk1
        assert results[1] == mock_chunk2

    @pytest.mark.asyncio
    @patch("domain.models.base.BaseLLMModel.create_completion", new_callable=AsyncMock)
    async def test_stream_success_with_span(self, mock_create: AsyncMock) -> None:
        """测试带span的流式处理成功."""
        test_messages = [
            {"role": "user", "content": "test user message"},
            {"role": "assistant", "content": "test assistant message"},
        ]
        test_stream = True

        # Mock span
        mock_span = Mock()
        mock_span.add_info_events = Mock()

        # Mock chunk数据
        mock_chunk = Mock()
        mock_chunk.model_dump.return_value = {"code": 0, "content": "chunk"}
        mock_chunk.model_dump_json.return_value = '{"content": "chunk"}'

        async def mock_response_iterator() -> AsyncIterator[Mock]:
            yield mock_chunk

        mock_create.return_value = mock_response_iterator()

        # 执行流式处理
        results = []
        async for chunk in self.model.stream(test_messages, test_stream, mock_span):
            results.append(chunk)

        # 验证span调用
        assert (
            mock_span.add_info_events.call_count >= 4
        )  # messages + model + stream + chunk

        # 验证具体的span调用
        calls = mock_span.add_info_events.call_args_list
        message_calls = [
            call for call in calls if "user" in str(call) or "assistant" in str(call)
        ]
        assert len(message_calls) >= 2

    @pytest.mark.asyncio
    @patch("domain.models.base.llm_plugin_error")
    @patch("domain.models.base.BaseLLMModel.create_completion", new_callable=AsyncMock)
    async def test_stream_error_chunk_handling(
        self, mock_create: AsyncMock, mock_error_handler: Mock
    ) -> None:
        """测试错误chunk处理."""
        test_messages = [{"role": "user", "content": "test message"}]
        test_stream = True

        # Mock错误chunk
        mock_error_chunk = Mock()
        mock_error_chunk.model_dump.return_value = {
            "code": 500,
            "message": "Internal server error",
        }

        async def mock_response_iterator() -> AsyncIterator[Mock]:
            yield mock_error_chunk

        mock_create.return_value = mock_response_iterator()

        # 执行并验证错误处理
        results = []
        async for chunk in self.model.stream(test_messages, test_stream, None):
            results.append(chunk)

            # 验证错误处理器被调用
            mock_error_handler.assert_called_once_with(500, "Internal server error")

    @pytest.mark.asyncio
    @patch("domain.models.base.BaseLLMModel.create_completion", new_callable=AsyncMock)
    async def test_stream_api_timeout_error(self, mock_create: AsyncMock) -> None:
        """测试API超时错误处理."""
        test_messages = [{"role": "user", "content": "test message"}]
        test_stream = True

        # pylint: disable=import-outside-toplevel
        from openai import APITimeoutError

        # pylint: disable=import-outside-toplevel
        from exceptions.plugin_exc import PluginExc

        # 创建一个mock请求对象
        mock_request = Mock()
        mock_create.side_effect = APITimeoutError(mock_request)

        # 验证异常处理
        with pytest.raises(PluginExc, match="请求服务超时"):
            results = []
            async for chunk in self.model.stream(test_messages, test_stream, None):
                results.append(chunk)

    @pytest.mark.asyncio
    @patch("domain.models.base.llm_plugin_error")
    @patch("domain.models.base.BaseLLMModel.create_completion", new_callable=AsyncMock)
    async def test_stream_api_error_handling(
        self, mock_create: AsyncMock, mock_error_handler: Mock
    ) -> None:
        """测试API错误处理."""
        test_messages = [{"role": "user", "content": "test message"}]
        test_stream = True
        mock_span = Mock()
        mock_span.add_info_events = Mock()

        # pylint: disable=import-outside-toplevel
        from openai import APIError

        # Mock API错误
        api_error = APIError(
            message="API Error", request=Mock(), body={"error": "Bad request"}
        )
        api_error.code = "400"

        mock_create.side_effect = api_error

        # 执行并验证错误处理
        results = []
        async for chunk in self.model.stream(test_messages, test_stream, mock_span):
            results.append(chunk)

        # 验证span记录错误信息
        assert mock_span.add_info_events.call_count >= 4

        # 验证错误处理器被调用
        mock_error_handler.assert_called_once_with("400", "API Error")

    @pytest.mark.asyncio
    @patch("domain.models.base.llm_plugin_error")
    @patch("domain.models.base.BaseLLMModel.create_completion", new_callable=AsyncMock)
    async def test_stream_value_error_handling(
        self, mock_create: AsyncMock, mock_error_handler: Mock
    ) -> None:
        """测试值错误处理."""
        test_messages = [{"role": "user", "content": "test message"}]
        test_stream = True
        mock_span = Mock()
        mock_span.add_info_events = Mock()

        mock_create.side_effect = ValueError("Invalid value")

        # 执行并验证错误处理
        results = []
        async for chunk in self.model.stream(test_messages, test_stream, mock_span):
            results.append(chunk)

        # 验证span记录错误信息
        assert mock_span.add_info_events.call_count >= 3

        # 验证错误处理器被调用
        mock_error_handler.assert_called_once_with("-1", "Invalid value")

    @pytest.mark.asyncio
    @patch("domain.models.base.BaseLLMModel.create_completion", new_callable=AsyncMock)
    async def test_stream_concurrent_access(self, mock_create: AsyncMock) -> None:
        """测试并发访问流式处理."""
        test_messages = [{"role": "user", "content": "test message"}]

        # Mock chunk数据
        mock_chunk = Mock()
        mock_chunk.model_dump.return_value = {"code": 0, "content": "chunk"}
        mock_chunk.model_dump_json.return_value = '{"content": "chunk"}'

        def mock_response_iterator_factory() -> AsyncIterator[Mock]:
            async def mock_response_iterator() -> AsyncIterator[Mock]:
                await asyncio.sleep(0.01)  # 模拟延迟
                yield mock_chunk

            return mock_response_iterator()

        mock_create.side_effect = (
            lambda *_args, **_kwargs: mock_response_iterator_factory()
        )

        # 创建并发任务
        tasks = []
        for _ in range(3):
            task = asyncio.create_task(
                self._collect_stream_results(test_messages, True)
            )
            tasks.append(task)

        # 等待所有任务完成
        results = await asyncio.gather(*tasks)

        # 验证所有任务都成功
        for result_list in results:
            assert len(result_list) == 1
            assert result_list[0] == mock_chunk

    async def _collect_stream_results(
        self, messages: List[Dict[str, Any]], stream: bool
    ) -> List[Any]:
        """辅助方法：收集流式结果."""
        results = []
        async for chunk in self.model.stream(messages, stream, None):
            results.append(chunk)
        return results

    @pytest.mark.asyncio
    @patch("domain.models.base.BaseLLMModel.create_completion", new_callable=AsyncMock)
    async def test_unicode_message_handling(self, mock_create: AsyncMock) -> None:
        """测试Unicode消息处理."""
        unicode_messages = [
            {"role": "user", "content": "测试中文消息🚀"},
            {"role": "assistant", "content": "中文回复✅"},
        ]
        test_stream = True
        mock_span = Mock()
        mock_span.add_info_events = Mock()

        # Mock chunk数据
        mock_chunk = Mock()
        mock_chunk.model_dump.return_value = {"code": 0, "content": "中文响应"}
        mock_chunk.model_dump_json.return_value = '{"content": "中文响应"}'

        async def mock_response_iterator() -> AsyncIterator[Mock]:
            yield mock_chunk

        mock_create.return_value = mock_response_iterator()

        # 执行流式处理
        results = []
        async for chunk in self.model.stream(unicode_messages, test_stream, mock_span):
            results.append(chunk)

        # 验证Unicode内容正确处理
        assert len(results) == 1
        assert results[0] == mock_chunk

        # 验证span记录了Unicode内容
        calls = mock_span.add_info_events.call_args_list
        unicode_calls = [
            call for call in calls if any("测试中文" in str(arg) for arg in call.args)
        ]
        assert len(unicode_calls) > 0

    @pytest.mark.asyncio
    @patch("domain.models.base.BaseLLMModel.create_completion", new_callable=AsyncMock)
    async def test_empty_messages_handling(self, mock_create: AsyncMock) -> None:
        """测试空消息列表处理."""
        empty_messages: List[Dict[str, Any]] = []
        test_stream = True

        async def mock_empty_response() -> AsyncIterator[Any]:
            # 空的异步生成器，用于模拟无响应情况
            return
            yield  # pylint: disable=unreachable

        mock_create.return_value = mock_empty_response()

        # 执行流式处理
        results = []
        async for chunk in self.model.stream(empty_messages, test_stream, None):
            results.append(chunk)

        # 验证空消息处理
        assert len(results) == 0

    def test_model_attribute_access(self) -> None:
        """测试模型属性访问."""
        # 测试名称访问
        assert self.model.name == self.model_name

        # 测试LLM客户端访问
        assert self.model.llm == self.mock_llm

        # 测试属性设置
        new_name = "new_model_name"
        self.model.name = new_name
        assert self.model.name == new_name
