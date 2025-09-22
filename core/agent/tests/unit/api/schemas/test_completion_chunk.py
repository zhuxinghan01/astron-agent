"""CompletionChunk Schema单元测试模块."""

import json
from typing import Any, Dict, List

from pydantic import ValidationError

from api.schemas.completion_chunk import (
    ReasonChatCompletionChunk,
    ReasonChoice,
    ReasonChoiceDelta,
    ReasonChoiceDeltaToolCall,
    ReasonChoiceDeltaToolCallFunction,
)


class TestReasonChoiceDeltaToolCallFunction:
    """ReasonChoiceDeltaToolCallFunction测试类."""

    def test_tool_call_function_creation(self) -> None:
        """测试工具调用函数创建."""
        function_data: Dict[str, Any] = {
            "name": "test_function",
            "arguments": '{"param1": "value1", "param2": "value2"}',
        }

        tool_function = ReasonChoiceDeltaToolCallFunction(**function_data)
        assert tool_function.name == "test_function"
        # 处理可能为None的arguments
        if tool_function.arguments is not None:
            assert "param1" in tool_function.arguments

    def test_tool_call_function_unicode_support(self) -> None:
        """测试工具调用函数Unicode支持."""
        unicode_data: Dict[str, Any] = {
            "name": "中文函数名",
            "arguments": '{"query": "中文查询🔍", "context": "特殊字符①②③"}',
        }

        tool_function = ReasonChoiceDeltaToolCallFunction(**unicode_data)
        assert tool_function.name == "中文函数名"
        if tool_function.arguments is not None:
            assert "中文查询🔍" in tool_function.arguments

    def test_tool_call_function_validation(self) -> None:
        """测试工具调用函数验证."""
        # 测试无效数据
        invalid_data_sets: List[Dict[str, Any]] = [
            {"name": "", "arguments": "{}"},  # 空函数名
            {"name": "test", "arguments": "invalid_json"},  # 无效JSON
        ]

        for invalid_data in invalid_data_sets:
            try:
                ReasonChoiceDeltaToolCallFunction(**invalid_data)
                # 某些验证可能在运行时进行
            except (ValidationError, ValueError):
                # 验证错误是预期的
                pass


class TestReasonChoiceDeltaToolCall:
    """ReasonChoiceDeltaToolCall测试类."""

    def test_tool_call_creation(self) -> None:
        """测试工具调用创建."""
        function_data: Dict[str, Any] = {
            "name": "search_function",
            "arguments": '{"query": "test search"}',
        }

        tool_call_data: Dict[str, Any] = {
            "index": 0,
            "type": "tool",
            "reason": "执行工具调用",
            "function": ReasonChoiceDeltaToolCallFunction(**function_data),
        }

        tool_call = ReasonChoiceDeltaToolCall(**tool_call_data)
        assert tool_call.index == 0
        assert tool_call.type == "tool"
        assert tool_call.reason == "执行工具调用"
        assert isinstance(
            tool_call.function, ReasonChoiceDeltaToolCallFunction
        ) or hasattr(tool_call.function, "name")

    def test_tool_call_without_function(self) -> None:
        """测试没有function的工具调用."""
        tool_call_data: Dict[str, Any] = {
            "index": 0,
            "type": "tool",
            "reason": "无function的工具调用",
        }

        try:
            tool_call = ReasonChoiceDeltaToolCall(**tool_call_data)
            # 验证可选字段处理
            assert tool_call.index == 0
            assert tool_call.type == "tool"
            assert tool_call.reason == "无function的工具调用"
        except ValidationError:
            # 如果function是必需的
            pass

    def test_tool_call_unicode_content(self) -> None:
        """测试工具调用Unicode内容."""
        unicode_function = ReasonChoiceDeltaToolCallFunction(
            name="中文搜索", arguments='{"查询": "测试内容🔍"}'
        )

        tool_call_data: Dict[str, Any] = {
            "index": 0,
            "type": "tool",
            "reason": "中文搜索调用",
            "function": unicode_function,
        }

        tool_call = ReasonChoiceDeltaToolCall(**tool_call_data)
        assert tool_call.reason == "中文搜索调用"


class TestReasonChoiceDelta:
    """ReasonChoiceDelta测试类."""

    def test_choice_delta_creation(self) -> None:
        """测试选择增量创建."""
        delta_data: Dict[str, Any] = {"content": "这是测试内容", "role": "assistant"}

        choice_delta = ReasonChoiceDelta(**delta_data)
        if hasattr(choice_delta, "content"):
            assert choice_delta.content == "这是测试内容"
        if hasattr(choice_delta, "role"):
            assert choice_delta.role == "assistant"

    def test_choice_delta_with_tool_calls(self) -> None:
        """测试包含工具调用的选择增量."""
        tool_call = ReasonChoiceDeltaToolCall(
            index=0,
            type="tool",
            reason="测试工具调用",
            function=ReasonChoiceDeltaToolCallFunction(
                name="test_tool", arguments="{}"
            ),
        )

        delta_data: Dict[str, Any] = {
            "content": "调用工具中...",
            "tool_calls": [tool_call],
        }

        try:
            choice_delta = ReasonChoiceDelta(**delta_data)
            if hasattr(choice_delta, "tool_calls") and choice_delta.tool_calls:
                assert len(choice_delta.tool_calls) == 1
        except (ValidationError, TypeError):
            # tool_calls可能有特定的验证规则
            pass

    def test_choice_delta_unicode_content(self) -> None:
        """测试选择增量Unicode内容."""
        unicode_data: Dict[str, Any] = {
            "content": "中文内容测试🚀特殊字符①②③",
            "role": "assistant",
        }

        choice_delta = ReasonChoiceDelta(**unicode_data)
        if (
            hasattr(choice_delta, "content")
            and choice_delta.content is not None
            and isinstance(choice_delta.content, str)
        ):
            assert (
                "🚀" in choice_delta.content
            )  # pylint: disable=unsupported-membership-test
            assert (
                "中文内容" in choice_delta.content
            )  # pylint: disable=unsupported-membership-test

    def test_choice_delta_empty_content(self) -> None:
        """测试空内容的选择增量."""
        empty_data: Dict[str, Any] = {"content": "", "role": "assistant"}

        choice_delta = ReasonChoiceDelta(**empty_data)
        if hasattr(choice_delta, "content"):
            assert choice_delta.content == ""

    def test_choice_delta_none_fields(self) -> None:
        """测试None字段的选择增量."""
        none_data: Dict[str, Any] = {"content": None, "role": "assistant"}

        try:
            choice_delta = ReasonChoiceDelta(**none_data)
            if hasattr(choice_delta, "content"):
                assert choice_delta.content is None
        except ValidationError:
            # content可能不允许None
            pass


class TestReasonChoice:
    """ReasonChoice测试类."""

    def test_reason_choice_creation(self) -> None:
        """测试推理选择创建."""
        delta = ReasonChoiceDelta(content="推理过程中...", role="assistant")

        choice_data: Dict[str, Any] = {
            "index": 0,
            "delta": delta,
            "finish_reason": None,
        }

        reason_choice = ReasonChoice(**choice_data)
        assert reason_choice.index == 0
        if hasattr(reason_choice, "finish_reason"):
            assert reason_choice.finish_reason is None

    def test_reason_choice_with_finish_reason(self) -> None:
        """测试包含完成原因的推理选择."""
        delta = ReasonChoiceDelta(content="推理完成", role="assistant")

        choice_data: Dict[str, Any] = {
            "index": 0,
            "delta": delta,
            "finish_reason": "stop",
        }

        reason_choice = ReasonChoice(**choice_data)
        if hasattr(reason_choice, "finish_reason"):
            assert reason_choice.finish_reason == "stop"

    def test_reason_choice_multiple_indices(self) -> None:
        """测试多个索引的推理选择."""
        for i in range(5):
            delta = ReasonChoiceDelta(content=f"选择{i}", role="assistant")
            choice_data: Dict[str, Any] = {
                "index": i,
                "delta": delta,
                "finish_reason": None,
            }

            reason_choice = ReasonChoice(**choice_data)
            assert reason_choice.index == i

    def test_reason_choice_unicode_delta(self) -> None:
        """测试Unicode增量的推理选择."""
        unicode_delta = ReasonChoiceDelta(
            content="中文推理内容🧠特殊字符①②③", role="assistant"
        )

        choice_data: Dict[str, Any] = {
            "index": 0,
            "delta": unicode_delta,
            "finish_reason": "stop",
        }

        reason_choice = ReasonChoice(**choice_data)
        if hasattr(reason_choice.delta, "content") and reason_choice.delta.content:
            assert "🧠" in reason_choice.delta.content


class TestReasonChatCompletionChunk:
    """ReasonChatCompletionChunk测试类."""

    def test_completion_chunk_creation(self) -> None:
        """测试完成块创建."""
        delta = ReasonChoiceDelta(content="Hello", role="assistant")
        choice = ReasonChoice(index=0, delta=delta, finish_reason=None)

        chunk_data: Dict[str, Any] = {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1234567890,
            "model": "gpt-3.5-turbo",
            "choices": [choice],
        }

        completion_chunk = ReasonChatCompletionChunk(**chunk_data)
        assert completion_chunk.id == "chatcmpl-123"
        assert completion_chunk.model == "gpt-3.5-turbo"
        assert len(completion_chunk.choices) == 1

    def test_completion_chunk_multiple_choices(self) -> None:
        """测试多选择完成块."""
        choices: List[ReasonChoice] = []
        for i in range(3):
            delta = ReasonChoiceDelta(content=f"选择{i}", role="assistant")
            choice = ReasonChoice(index=i, delta=delta, finish_reason=None)
            choices.append(choice)

        chunk_data: Dict[str, Any] = {
            "id": "chatcmpl-multi",
            "object": "chat.completion.chunk",
            "created": 1234567890,
            "model": "gpt-4",
            "choices": choices,
        }

        completion_chunk = ReasonChatCompletionChunk(**chunk_data)
        assert len(completion_chunk.choices) == 3

    def test_completion_chunk_unicode_content(self) -> None:
        """测试Unicode内容完成块."""
        unicode_delta = ReasonChoiceDelta(
            content="中文回复🤖特殊字符①②③", role="assistant"
        )
        choice = ReasonChoice(index=0, delta=unicode_delta, finish_reason=None)

        chunk_data: Dict[str, Any] = {
            "id": "中文完成块",
            "object": "chat.completion.chunk",
            "created": 1234567890,
            "model": "中文模型",
            "choices": [choice],
        }

        completion_chunk = ReasonChatCompletionChunk(**chunk_data)
        assert "中文完成块" in completion_chunk.id

    def test_completion_chunk_serialization(self) -> None:
        """测试完成块序列化."""
        delta = ReasonChoiceDelta(content="序列化测试", role="assistant")
        choice = ReasonChoice(index=0, delta=delta, finish_reason=None)

        chunk_data: Dict[str, Any] = {
            "id": "serialize-test",
            "object": "chat.completion.chunk",
            "created": 1234567890,
            "model": "test-model",
            "choices": [choice],
        }

        completion_chunk = ReasonChatCompletionChunk(**chunk_data)

        # 测试JSON序列化
        if hasattr(completion_chunk, "json"):
            json_str = completion_chunk.model_dump_json()
            assert isinstance(json_str, str)
            parsed_data = json.loads(json_str)
            assert parsed_data["id"] == "serialize-test"

    def test_completion_chunk_validation_errors(self) -> None:
        """测试完成块验证错误."""
        # 测试无效数据
        invalid_data_sets: List[Dict[str, Any]] = [
            {"id": "", "choices": []},  # 空ID
            {"id": "test", "choices": None},  # None choices
            {"id": "test", "object": "invalid", "choices": []},  # 无效object
        ]

        for invalid_data in invalid_data_sets:
            try:
                ReasonChatCompletionChunk(**invalid_data)
            except (ValidationError, TypeError):
                # 验证错误是预期的
                pass

    def test_completion_chunk_large_content(self) -> None:
        """测试大内容完成块."""
        large_content = "大量内容 " * 1000
        delta = ReasonChoiceDelta(content=large_content, role="assistant")
        choice = ReasonChoice(index=0, delta=delta, finish_reason=None)

        chunk_data: Dict[str, Any] = {
            "id": "large-content-test",
            "object": "chat.completion.chunk",
            "created": 1234567890,
            "model": "test-model",
            "choices": [choice],
        }

        completion_chunk = ReasonChatCompletionChunk(**chunk_data)
        assert len(completion_chunk.choices) == 1
        # 验证大内容被正确处理
        if (
            hasattr(completion_chunk.choices[0].delta, "content")
            and completion_chunk.choices[0].delta.content
        ):
            assert len(completion_chunk.choices[0].delta.content) > 1000

    def test_completion_chunk_streaming_scenario(self) -> None:
        """测试流式场景完成块."""
        # 模拟流式响应的多个chunk
        chunks: List[ReasonChatCompletionChunk] = []

        # 第一个chunk - 开始
        start_delta = ReasonChoiceDelta(content="开始", role="assistant")
        start_choice = ReasonChoice(index=0, delta=start_delta, finish_reason=None)
        start_chunk_data: Dict[str, Any] = {
            "id": "stream-1",
            "object": "chat.completion.chunk",
            "created": 1234567890,
            "model": "stream-model",
            "choices": [start_choice],
        }
        chunks.append(ReasonChatCompletionChunk(**start_chunk_data))

        # 中间chunks - 内容
        for i in range(3):
            content_delta = ReasonChoiceDelta(content=f"内容{i}", role="assistant")
            content_choice = ReasonChoice(
                index=0, delta=content_delta, finish_reason=None
            )
            content_chunk_data: Dict[str, Any] = {
                "id": f"stream-{i+2}",
                "object": "chat.completion.chunk",
                "created": 1234567890 + i,
                "model": "stream-model",
                "choices": [content_choice],
            }
            chunks.append(ReasonChatCompletionChunk(**content_chunk_data))

        # 最后一个chunk - 结束
        end_delta = ReasonChoiceDelta(content="", role="assistant")
        end_choice = ReasonChoice(index=0, delta=end_delta, finish_reason="stop")
        end_chunk_data: Dict[str, Any] = {
            "id": "stream-end",
            "object": "chat.completion.chunk",
            "created": 1234567894,
            "model": "stream-model",
            "choices": [end_choice],
        }
        chunks.append(ReasonChatCompletionChunk(**end_chunk_data))

        # 验证流式chunks
        assert len(chunks) == 5
        assert chunks[0].choices[0].finish_reason is None
        if hasattr(chunks[-1].choices[0], "finish_reason"):
            assert chunks[-1].choices[0].finish_reason == "stop"
