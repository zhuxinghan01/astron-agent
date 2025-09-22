"""
Unit tests for engine.nodes.cot.cot_runner
"""

from typing import Any, AsyncIterator, List, cast
from unittest.mock import AsyncMock, Mock, patch

import pytest

from api.schemas.agent_response import AgentResponse, CotStep
from api.schemas.llm_message import LLMMessage
from api.schemas.node_trace_patch import NodeTrace
from common_imports import Span
from domain.models.base import BaseLLMModel
from engine.nodes.base import Scratchpad
from engine.nodes.cot.cot_runner import CotRunner, UpdatedNode, default_cot_step
from engine.nodes.cot_process.cot_process_runner import CotProcessRunner
from exceptions import cot_exc
from service.plugin.base import BasePlugin, PluginResponse
from service.plugin.workflow import WorkflowPlugin


class TestCotRunnerCreation:
    """Test cases for CotRunner creation and initialization."""

    @pytest.fixture
    def mock_llm_model(self) -> Mock:
        """Create mock LLM model."""
        mock_model = Mock(spec=BaseLLMModel)
        mock_model.name = "gpt-3.5-turbo"
        mock_model.stream = AsyncMock()
        return mock_model

    @pytest.fixture
    def mock_process_runner(self) -> Mock:
        """Create mock CoT process runner."""
        mock_runner = Mock(spec=CotProcessRunner)
        mock_runner.run = AsyncMock()
        return mock_runner

    @pytest.fixture
    def mock_plugins(self) -> List[BasePlugin]:
        """Create mock plugins."""
        mock_plugin = Mock(spec=BasePlugin)
        mock_plugin.name = "test_plugin"
        mock_plugin.schema_template = "Test plugin schema"
        mock_plugin.typ = "test"
        mock_plugin.run = AsyncMock()
        mock_plugin.run_result = None
        return [cast(BasePlugin, mock_plugin)]

    @pytest.fixture
    def sample_chat_history(self) -> List[LLMMessage]:
        """Sample chat history for testing."""
        return [
            LLMMessage(role="user", content="Hello"),
            LLMMessage(role="assistant", content="Hi there!"),
        ]

    @pytest.fixture
    def cot_runner(
        self,
        mock_llm_model: Mock,
        mock_process_runner: Mock,
        mock_plugins: List[BasePlugin],
        sample_chat_history: List[LLMMessage],
    ) -> CotRunner:
        """Create CotRunner instance for testing."""
        return CotRunner(
            model=mock_llm_model,
            chat_history=sample_chat_history,
            plugins=mock_plugins,
            process_runner=mock_process_runner,
            instruct="You are a helpful assistant.",
            knowledge="Some knowledge base content.",
            question="How can I help you today?",
        )

    @pytest.mark.unit
    def test_cot_runner_creation_with_all_fields(
        self,
        mock_llm_model: Mock,
        mock_process_runner: Mock,
        mock_plugins: List[BasePlugin],
        sample_chat_history: List[LLMMessage],
    ) -> None:
        """Test CotRunner creation with all fields."""
        # Act
        runner = CotRunner(
            model=mock_llm_model,
            chat_history=sample_chat_history,
            plugins=mock_plugins,
            process_runner=mock_process_runner,
            instruct="Custom instruction",
            knowledge="Knowledge content",
            question="Test question",
            max_loop=20,
        )

        # Assert
        assert runner.model == mock_llm_model
        assert len(runner.chat_history) == 2
        assert runner.instruct == "Custom instruction"
        assert runner.knowledge == "Knowledge content"
        assert runner.question == "Test question"
        assert runner.max_loop == 20
        assert len(runner.plugins) == 1
        assert runner.process_runner == mock_process_runner

    @pytest.mark.unit
    def test_cot_runner_creation_with_defaults(
        self,
        mock_llm_model: Mock,
        mock_process_runner: Mock,
        mock_plugins: List[BasePlugin],
        sample_chat_history: List[LLMMessage],
    ) -> None:
        """Test CotRunner creation with default values."""
        # Act
        runner = CotRunner(
            model=mock_llm_model,
            chat_history=sample_chat_history,
            plugins=mock_plugins,
            process_runner=mock_process_runner,
        )

        # Assert
        assert runner.instruct == ""
        assert runner.knowledge == ""
        assert runner.question == ""
        assert runner.max_loop == 30
        assert isinstance(runner.scratchpad, Scratchpad)


class TestCotRunnerPromptGeneration:
    """Test cases for CotRunner prompt generation methods."""

    @pytest.fixture
    def mock_llm_model(self) -> Mock:
        """Create mock LLM model."""
        mock_model = Mock(spec=BaseLLMModel)
        mock_model.name = "gpt-3.5-turbo"
        mock_model.stream = AsyncMock()
        return mock_model

    @pytest.fixture
    def mock_process_runner(self) -> Mock:
        """Create mock CoT process runner."""
        mock_runner = Mock(spec=CotProcessRunner)
        mock_runner.run = AsyncMock()
        return mock_runner

    @pytest.fixture
    def mock_plugins(self) -> List[BasePlugin]:
        """Create mock plugins."""
        mock_plugin = Mock(spec=BasePlugin)
        mock_plugin.name = "test_plugin"
        mock_plugin.schema_template = "Test plugin schema"
        mock_plugin.typ = "test"
        mock_plugin.run = AsyncMock()
        mock_plugin.run_result = None
        return [cast(BasePlugin, mock_plugin)]

    @pytest.fixture
    def sample_chat_history(self) -> List[LLMMessage]:
        """Sample chat history for testing."""
        return [
            LLMMessage(role="user", content="Hello"),
            LLMMessage(role="assistant", content="Hi there!"),
        ]

    @pytest.fixture
    def cot_runner(
        self,
        mock_llm_model: Mock,
        mock_process_runner: Mock,
        mock_plugins: List[BasePlugin],
        sample_chat_history: List[LLMMessage],
    ) -> CotRunner:
        """Create CotRunner instance for testing."""
        return CotRunner(
            model=mock_llm_model,
            chat_history=sample_chat_history,
            plugins=mock_plugins,
            process_runner=mock_process_runner,
            instruct="You are a helpful assistant.",
            knowledge="Some knowledge base content.",
            question="How can I help you today?",
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_system_prompt(self, cot_runner: CotRunner) -> None:
        """Test system prompt creation."""
        # Mock cur_time to return predictable value
        with patch(
            "engine.nodes.base.RunnerBase.cur_time", return_value="2024-01-01 12:00:00"
        ):
            # Act
            system_prompt = await cot_runner.create_system_prompt()

            # Assert
            assert "2024-01-01 12:00:00" in system_prompt
            assert "You are a helpful assistant." in system_prompt
            assert "Some knowledge base content." in system_prompt
            assert "Test plugin schema" in system_prompt
            assert "test_plugin" in system_prompt

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_system_prompt_with_empty_fields(
        self,
        mock_llm_model: Mock,
        mock_process_runner: Mock,
        mock_plugins: List[BasePlugin],
        sample_chat_history: List[LLMMessage],
    ) -> None:
        """Test system prompt creation with empty instruct and knowledge."""
        # Arrange
        runner = CotRunner(
            model=mock_llm_model,
            chat_history=sample_chat_history,
            plugins=mock_plugins,
            process_runner=mock_process_runner,
            instruct="",
            knowledge="",
        )

        # Mock cur_time to return predictable value
        with patch(
            "engine.nodes.base.RunnerBase.cur_time", return_value="2024-01-01 12:00:00"
        ):
            # Act
            system_prompt = await runner.create_system_prompt()

            # Assert
            assert "2024-01-01 12:00:00" in system_prompt
            assert (
                "None" in system_prompt
            )  # Should replace empty instruct and knowledge with "None"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_system_prompt_with_r1_model(
        self,
        mock_llm_model: Mock,
        mock_process_runner: Mock,
        mock_plugins: List[BasePlugin],
        sample_chat_history: List[LLMMessage],
    ) -> None:
        """Test system prompt creation with R1 model."""
        # Arrange
        mock_llm_model.name = "xdeepseekr1"
        runner = CotRunner(
            model=mock_llm_model,
            chat_history=sample_chat_history,
            plugins=mock_plugins,
            process_runner=mock_process_runner,
        )

        # Mock cur_time to return predictable value
        with patch(
            "engine.nodes.base.RunnerBase.cur_time", return_value="2024-01-01 12:00:00"
        ):
            # Act
            await runner.create_system_prompt()

            # Assert
            assert "xdeepseekr1" in mock_llm_model.name
            # R1 template should be used

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user_prompt(self, cot_runner: CotRunner) -> None:
        """Test user prompt creation."""
        # Mock create_history_prompt to return predictable value
        expected_history = "User: Hello\nAssistant: Hi there!"
        with patch(
            "engine.nodes.base.RunnerBase.create_history_prompt",
            new_callable=AsyncMock,
            return_value=expected_history,
        ):
            # Act
            user_prompt = await cot_runner.create_user_prompt()

            # Assert
            assert expected_history in user_prompt
            assert "How can I help you today?" in user_prompt


class TestCotRunnerStepParsing:
    """Test cases for CotRunner step parsing functionality."""

    @pytest.fixture
    def mock_llm_model(self) -> Mock:
        """Create mock LLM model."""
        mock_model = Mock(spec=BaseLLMModel)
        mock_model.name = "gpt-3.5-turbo"
        mock_model.stream = AsyncMock()
        return mock_model

    @pytest.fixture
    def mock_process_runner(self) -> Mock:
        """Create mock CoT process runner."""
        mock_runner = Mock(spec=CotProcessRunner)
        mock_runner.run = AsyncMock()
        return mock_runner

    @pytest.fixture
    def mock_plugins(self) -> List[BasePlugin]:
        """Create mock plugins."""
        mock_plugin = Mock(spec=BasePlugin)
        mock_plugin.name = "test_plugin"
        mock_plugin.schema_template = "Test plugin schema"
        mock_plugin.typ = "test"
        mock_plugin.run = AsyncMock()
        mock_plugin.run_result = None
        return [cast(BasePlugin, mock_plugin)]

    @pytest.fixture
    def sample_chat_history(self) -> List[LLMMessage]:
        """Sample chat history for testing."""
        return [
            LLMMessage(role="user", content="Hello"),
            LLMMessage(role="assistant", content="Hi there!"),
        ]

    @pytest.fixture
    def cot_runner(
        self,
        mock_llm_model: Mock,
        mock_process_runner: Mock,
        mock_plugins: List[BasePlugin],
        sample_chat_history: List[LLMMessage],
    ) -> CotRunner:
        """Create CotRunner instance for testing."""
        return CotRunner(
            model=mock_llm_model,
            chat_history=sample_chat_history,
            plugins=mock_plugins,
            process_runner=mock_process_runner,
            instruct="You are a helpful assistant.",
            knowledge="Some knowledge base content.",
            question="How can I help you today?",
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_parse_cot_step_with_final_answer(
        self, cot_runner: CotRunner
    ) -> None:
        """Test parsing CoT step with Final Answer."""
        # Act
        step_content = (
            "Thought: This is the final step\nFinal Answer: This is the answer"
        )
        cot_step = await cot_runner.parse_cot_step(step_content)

        # Assert
        assert cot_step.thought == "This is the final step"
        assert cot_step.finished_cot is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_parse_cot_step_with_action(self, cot_runner: CotRunner) -> None:
        """Test parsing CoT step with action."""
        # Act
        step_content = """Thought: I need to use a plugin
Action: test_plugin
Action Input: {"query": "test query"}
Observation:"""

        cot_step = await cot_runner.parse_cot_step(step_content)

        # Assert
        assert cot_step.thought == "I need to use a plugin"
        assert cot_step.action == "test_plugin"
        assert cot_step.action_input == {"query": "test query"}
        assert cot_step.finished_cot is False

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_parse_cot_step_invalid_format(self, cot_runner: CotRunner) -> None:
        """Test parsing CoT step with invalid format."""
        # Act & Assert
        step_content = "Thought: Invalid format without action"
        with pytest.raises(type(cot_exc.CotFormatIncorrectExc)):
            await cot_runner.parse_cot_step(step_content)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_parse_cot_step_invalid_json(self, cot_runner: CotRunner) -> None:
        """Test parsing CoT step with invalid JSON in action input."""
        # Act & Assert
        step_content = """Thought: Test
Action: test_plugin
Action Input: {invalid json}
Observation:"""

        with pytest.raises(type(cot_exc.CotFormatIncorrectExc)):
            await cot_runner.parse_cot_step(step_content)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_parse_cot_step_invalid_plugin(self, cot_runner: CotRunner) -> None:
        """Test parsing CoT step with invalid plugin name."""
        # Act & Assert
        step_content = """Thought: Test
Action: invalid_plugin
Action Input: {"query": "test"}
Observation:"""

        with pytest.raises(type(cot_exc.CotFormatIncorrectExc)):
            await cot_runner.parse_cot_step(step_content)


class TestCotRunnerPluginOperations:
    """Test cases for CotRunner plugin operations."""

    @pytest.fixture
    def mock_llm_model(self) -> Mock:
        """Create mock LLM model."""
        mock_model = Mock(spec=BaseLLMModel)
        mock_model.name = "gpt-3.5-turbo"
        mock_model.stream = AsyncMock()
        return mock_model

    @pytest.fixture
    def mock_process_runner(self) -> Mock:
        """Create mock CoT process runner."""
        mock_runner = Mock(spec=CotProcessRunner)
        mock_runner.run = AsyncMock()
        return mock_runner

    @pytest.fixture
    def mock_plugins(self) -> List[BasePlugin]:
        """Create mock plugins."""
        mock_plugin = Mock(spec=BasePlugin)
        mock_plugin.name = "test_plugin"
        mock_plugin.schema_template = "Test plugin schema"
        mock_plugin.typ = "test"
        mock_plugin.run = AsyncMock()
        mock_plugin.run_result = None
        return [cast(BasePlugin, mock_plugin)]

    @pytest.fixture
    def sample_chat_history(self) -> List[LLMMessage]:
        """Sample chat history for testing."""
        return [
            LLMMessage(role="user", content="Hello"),
            LLMMessage(role="assistant", content="Hi there!"),
        ]

    @pytest.fixture
    def cot_runner(
        self,
        mock_llm_model: Mock,
        mock_process_runner: Mock,
        mock_plugins: List[BasePlugin],
        sample_chat_history: List[LLMMessage],
    ) -> CotRunner:
        """Create CotRunner instance for testing."""
        return CotRunner(
            model=mock_llm_model,
            chat_history=sample_chat_history,
            plugins=mock_plugins,
            process_runner=mock_process_runner,
            instruct="You are a helpful assistant.",
            knowledge="Some knowledge base content.",
            question="How can I help you today?",
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_is_valid_plugin(self, cot_runner: CotRunner) -> None:
        """Test plugin validation."""
        # Act & Assert
        assert await cot_runner.is_valid_plugin("test_plugin") is True
        assert await cot_runner.is_valid_plugin("invalid_plugin") is False
        assert await cot_runner.is_valid_plugin("  test_plugin  ") is True  # Test strip

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_plugin(self, cot_runner: CotRunner) -> None:
        """Test getting plugin by name."""
        # Arrange
        cot_step = CotStep(action="test_plugin")

        # Act
        plugin = await cot_runner.get_plugin(cot_step)

        # Assert
        assert plugin is not None
        assert plugin.name == "test_plugin"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_plugin_not_found(self, cot_runner: CotRunner) -> None:
        """Test getting non-existent plugin."""
        # Arrange
        cot_step = CotStep(action="nonexistent_plugin")

        # Act
        plugin = await cot_runner.get_plugin(cot_step)

        # Assert
        assert plugin is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_plugin_success(self, cot_runner: CotRunner) -> None:
        """Test successful plugin execution."""
        # Arrange
        mock_span = Mock(spec=Span)
        mock_span.sid = "test_span_id"
        mock_span_context = Mock()
        context_manager = Mock()
        context_manager.__enter__ = Mock(return_value=mock_span_context)
        context_manager.__exit__ = Mock(return_value=None)
        mock_span.start = Mock(return_value=context_manager)

        cot_step = CotStep(action="test_plugin", action_input={"query": "test"})

        expected_response = PluginResponse(
            result={"answer": "Plugin response"}, log=["Plugin executed successfully"]
        )
        # Mock the plugin run method
        mock_run = AsyncMock(return_value=expected_response)
        cot_runner.plugins[0].run = mock_run

        # Act
        result = await cot_runner.run_plugin(cot_step, mock_span)

        # Assert
        assert result == expected_response
        mock_run.assert_called_once_with({"query": "test"}, mock_span_context)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_plugin_not_found(self, cot_runner: CotRunner) -> None:
        """Test plugin execution with non-existent plugin."""
        # Arrange
        mock_span = Mock(spec=Span)
        mock_span.sid = "test_span_id"
        mock_span_context = Mock()
        context_manager = Mock()
        context_manager.__enter__ = Mock(return_value=mock_span_context)
        context_manager.__exit__ = Mock(return_value=None)
        mock_span.start = Mock(return_value=context_manager)

        cot_step = CotStep(action="nonexistent_plugin", action_input={"query": "test"})

        # Act
        result = await cot_runner.run_plugin(cot_step, mock_span)

        # Assert
        assert result.result["code"] == 400
        assert "not found" in result.result["message"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_workflow_plugin(self, cot_runner: CotRunner) -> None:
        """Test workflow plugin execution."""
        # Arrange
        mock_span = Mock(spec=Span)
        mock_span.sid = "test_span_id"
        mock_span_context = Mock()
        context_manager = Mock()
        context_manager.__enter__ = Mock(return_value=mock_span_context)
        context_manager.__exit__ = Mock(return_value=None)
        mock_span.start = Mock(return_value=context_manager)

        workflow_plugin = Mock(spec=WorkflowPlugin)
        workflow_plugin.typ = "workflow"
        workflow_plugin.run_result = None

        async def mock_workflow_run(
            *_args: Any, **_kw_args: Any
        ) -> AsyncIterator[PluginResponse]:  # pylint: disable=unused-argument
            yield PluginResponse(result={"content": "Workflow response"})

        workflow_plugin.run = mock_workflow_run

        cot_step = CotStep(action="workflow_plugin", action_input={"task": "test"})

        # Act
        responses = []
        async for response in cot_runner.run_workflow_plugin(
            workflow_plugin, cot_step, mock_span
        ):
            responses.append(response)

        # Assert
        assert len(responses) >= 1
        assert cot_step.tool_type == "workflow"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_read_response_with_final_answer(self, cot_runner: CotRunner) -> None:
        """Test reading response with Final Answer."""
        # Arrange
        mock_span = Mock(spec=Span)
        mock_span.sid = "test_span_id"
        mock_span_context = Mock()
        context_manager = Mock()
        context_manager.__enter__ = Mock(return_value=mock_span_context)
        context_manager.__exit__ = Mock(return_value=None)
        mock_span.start = Mock(return_value=context_manager)

        mock_node_trace = Mock(spec=NodeTrace)
        mock_node_trace.trace = []

        # Mock model stream response
        mock_choice = Mock()
        mock_choice.delta.model_dump.return_value = {
            "reasoning_content": "",
            "content": "Final Answer: This is my final answer",
        }

        mock_chunk = Mock()
        mock_chunk.choices = [mock_choice]
        mock_chunk.usage = None

        async def mock_stream(
            *_args: Any, **_kw_args: Any
        ) -> AsyncIterator[Any]:  # pylint: disable=unused-argument
            yield mock_chunk

        cot_runner.model.stream = mock_stream  # type: ignore

        messages = Mock()
        messages.list.return_value = []

        # Act
        responses = []
        async for response in cot_runner.read_response(
            messages, True, mock_span, mock_node_trace
        ):
            responses.append(response)

        # Assert
        assert len(responses) >= 1


class TestCotRunnerExecution:
    """Test cases for CotRunner main execution logic."""

    @pytest.fixture
    def mock_llm_model(self) -> Mock:
        """Create mock LLM model."""
        mock_model = Mock(spec=BaseLLMModel)
        mock_model.name = "gpt-3.5-turbo"
        mock_model.stream = AsyncMock()
        return mock_model

    @pytest.fixture
    def mock_process_runner(self) -> Mock:
        """Create mock CoT process runner."""
        mock_runner = Mock(spec=CotProcessRunner)
        mock_runner.run = AsyncMock()
        return mock_runner

    @pytest.fixture
    def mock_plugins(self) -> List[BasePlugin]:
        """Create mock plugins."""
        mock_plugin = Mock(spec=BasePlugin)
        mock_plugin.name = "test_plugin"
        mock_plugin.schema_template = "Test plugin schema"
        mock_plugin.typ = "test"
        mock_plugin.run = AsyncMock()
        mock_plugin.run_result = None
        return [cast(BasePlugin, mock_plugin)]

    @pytest.fixture
    def sample_chat_history(self) -> List[LLMMessage]:
        """Sample chat history for testing."""
        return [
            LLMMessage(role="user", content="Hello"),
            LLMMessage(role="assistant", content="Hi there!"),
        ]

    @pytest.fixture
    def cot_runner(
        self,
        mock_llm_model: Mock,
        mock_process_runner: Mock,
        mock_plugins: List[BasePlugin],
        sample_chat_history: List[LLMMessage],
    ) -> CotRunner:
        """Create CotRunner instance for testing."""
        return CotRunner(
            model=mock_llm_model,
            chat_history=sample_chat_history,
            plugins=mock_plugins,
            process_runner=mock_process_runner,
            instruct="You are a helpful assistant.",
            knowledge="Some knowledge base content.",
            question="How can I help you today?",
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_success_with_final_answer(self, cot_runner: CotRunner) -> None:
        """Test successful run execution with Final Answer."""
        # Arrange
        mock_span = Mock(spec=Span)
        mock_span.sid = "test_span_id"
        mock_span_context = Mock()
        context_manager = Mock()
        context_manager.__enter__ = Mock(return_value=mock_span_context)
        context_manager.__exit__ = Mock(return_value=None)
        mock_span.start = Mock(return_value=context_manager)

        mock_node_trace = Mock(spec=NodeTrace)
        mock_node_trace.trace = []

        # Mock system and user prompt creation
        with patch(
            "engine.nodes.cot.cot_runner.CotRunner.create_system_prompt",
            AsyncMock(return_value="System prompt"),
        ):
            with patch(
                "engine.nodes.cot.cot_runner.CotRunner.create_user_prompt",
                AsyncMock(return_value="User prompt {scratchpad}"),
            ):
                with patch(
                    "engine.nodes.base.Scratchpad.template", AsyncMock(return_value="")
                ):
                    # Mock read_response to return final answer
                    async def mock_read_response(
                        *_args: Any, **_kw_args: Any
                    ) -> AsyncIterator[
                        AgentResponse
                    ]:  # pylint: disable=unused-argument
                        yield AgentResponse(
                            typ="content", content="Final answer", model="gpt-3.5-turbo"
                        )

                    with patch(
                        "engine.nodes.cot.cot_runner.CotRunner.read_response",
                        side_effect=mock_read_response,
                    ):
                        # Act
                        responses = []
                        async for response in cot_runner.run(
                            mock_span, mock_node_trace
                        ):
                            responses.append(response)

                        # Assert
                        assert len(responses) == 1
                        assert responses[0].typ == "content"
                        assert responses[0].content == "Final answer"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_max_loop_exceeded(self, cot_runner: CotRunner) -> None:
        """Test run execution when max loop is exceeded."""
        # Arrange
        cot_runner.max_loop = 2  # Set low max loop for testing

        mock_span = Mock(spec=Span)
        mock_span.sid = "test_span_id"
        mock_span_context = Mock()
        context_manager = Mock()
        context_manager.__enter__ = Mock(return_value=mock_span_context)
        context_manager.__exit__ = Mock(return_value=None)
        mock_span.start = Mock(return_value=context_manager)

        mock_node_trace = Mock(spec=NodeTrace)
        mock_node_trace.trace = []

        # Mock process runner to return some response
        async def mock_process_run(
            *_args: Any, **_kw_args: Any
        ) -> AsyncIterator[AgentResponse]:  # pylint: disable=unused-argument
            yield AgentResponse(
                typ="content", content="Process result", model="gpt-3.5-turbo"
            )

        # Create a Mock wrapper that can track calls
        mock_wrapper = Mock(side_effect=mock_process_run)
        cot_runner.process_runner.run = mock_wrapper  # type: ignore

        # Mock system and user prompt creation
        with patch(
            "engine.nodes.cot.cot_runner.CotRunner.create_system_prompt",
            AsyncMock(return_value="System prompt"),
        ):
            with patch(
                "engine.nodes.cot.cot_runner.CotRunner.create_user_prompt",
                AsyncMock(return_value="User prompt {scratchpad}"),
            ):
                with patch(
                    "engine.nodes.base.Scratchpad.template", AsyncMock(return_value="")
                ):

                    # Mock read_response to always return CoT step (never final answer)
                    cot_step = CotStep(
                        thought="I need to continue",
                        action="test_plugin",
                        action_input={"query": "test"},
                    )

                    async def mock_read_response(
                        *_args: Any, **_kw_args: Any
                    ) -> AsyncIterator[
                        AgentResponse
                    ]:  # pylint: disable=unused-argument
                        yield AgentResponse(
                            typ="cot_step", content=cot_step, model="gpt-3.5-turbo"
                        )

                    # Mock plugin execution
                    plugin_response = PluginResponse(
                        result={"answer": "Plugin response"}, log=["Plugin executed"]
                    )

                    with patch(
                        "engine.nodes.cot.cot_runner.CotRunner.read_response",
                        side_effect=mock_read_response,
                    ):
                        with patch(
                            "engine.nodes.cot.cot_runner.CotRunner.run_plugin",
                            AsyncMock(return_value=plugin_response),
                        ):
                            # Act
                            responses = []
                            async for response in cot_runner.run(
                                mock_span, mock_node_trace
                            ):
                                responses.append(response)

                            # Assert - Should call process runner after max loops
                            cot_runner.process_runner.run.assert_called_once()


class TestCotRunnerUtilities:
    """Test cases for CotRunner utility functions."""

    @pytest.mark.unit
    def test_updated_node_creation(self) -> None:
        """Test UpdatedNode creation."""
        # Act
        node = UpdatedNode(node_name="test_node")

        # Assert
        assert node.node_name == "test_node"

    @pytest.mark.unit
    def test_default_cot_step(self) -> None:
        """Test default CoT step."""
        # Assert
        assert default_cot_step.empty is True
