"""Unit tests for custom exception classes module."""

import asyncio
from unittest.mock import patch

import pytest

from exceptions import codes
from exceptions.agent_exc import (
    AgentExc,
    AgentInternalExc,
    AgentNormalExc,
    BotConfigInvalidExc,
    BotConfigNotFoundExc,
    ReceiveHttpMsgExc,
    ReceiveWsMsgExc,
    RequestSparkFlowExc,
    RequestSparkLinkExc,
)
from exceptions.base import AgentException
from exceptions.middleware_exc import AppAuthFailedExc, MiddlewareExc, PingRedisExc
from exceptions.plugin_exc import (
    CallLlmPluginExc,
    GetMcpPluginExc,
    GetToolSchemaExc,
    KnowledgeQueryExc,
    PluginExc,
    RunMcpPluginExc,
    RunToolExc,
    RunWorkflowExc,
    llm_plugin_error,
)


class TestAgentException:
    """Test cases for AgentException base class."""

    @pytest.mark.unit
    def test_init_with_tuple_only(self) -> None:
        """Test initialization with tuple only."""
        error_tuple = (40001, "Failed to get bot configuration")
        exc = AgentException(error_tuple)

        assert exc.code == 40001
        assert exc.message == "Failed to get bot configuration"

    @pytest.mark.unit
    def test_init_with_tuple_and_message(self) -> None:
        """Test initialization with tuple and additional message."""
        error_tuple = (40001, "Failed to get bot configuration")
        additional_message = "Detailed error information"
        exc = AgentException(error_tuple, additional_message)

        assert exc.code == 40001
        assert (
            exc.message == "Failed to get bot configuration:Detailed error information"
        )

    @pytest.mark.unit
    def test_init_with_empty_additional_message(self) -> None:
        """Test initialization with empty additional message."""
        error_tuple = (40001, "Failed to get bot configuration")
        exc = AgentException(error_tuple, "")

        assert exc.code == 40001
        assert exc.message == "Failed to get bot configuration"

    @pytest.mark.unit
    def test_str_representation(self) -> None:
        """Test string representation."""
        error_tuple = (40001, "Failed to get bot configuration")
        exc = AgentException(error_tuple, "Test message")

        expected = (
            "AgentException: (40001, Failed to get bot configuration:Test message)"
        )
        assert str(exc) == expected

    @pytest.mark.unit
    def test_repr_representation(self) -> None:
        """Test repr representation."""
        error_tuple = (40001, "Failed to get bot configuration")
        exc = AgentException(error_tuple)

        expected = "AgentException: (40001, Failed to get bot configuration)"
        assert repr(exc) == expected

    @pytest.mark.unit
    def test_exception_inheritance(self) -> None:
        """Test exception inheritance hierarchy."""
        error_tuple = (40001, "Failed to get bot configuration")
        exc = AgentException(error_tuple)

        assert isinstance(exc, Exception)
        assert isinstance(exc, AgentException)

    @pytest.mark.unit
    def test_exception_raising(self) -> None:
        """Test exception raising mechanism."""
        error_tuple = (40001, "Failed to get bot configuration")

        with pytest.raises(AgentException) as exc_info:
            raise AgentException(error_tuple, "Test exception raised")

        assert exc_info.value.code == 40001
        assert "Test exception raised" in exc_info.value.message

    @pytest.mark.unit
    def test_unicode_support(self) -> None:
        """Test Unicode content support."""
        error_tuple = (40001, "Chinese error message🚨")
        additional_msg = "Additional Chinese information🔧"
        exc = AgentException(error_tuple, additional_msg)

        assert exc.message == "Chinese error message🚨:Additional Chinese information🔧"
        assert "Chinese error message🚨" in str(exc)

    @pytest.mark.unit
    def test_message_concatenation_edge_cases(self) -> None:
        """Test edge cases for message concatenation."""
        # Test with None additional message
        error_tuple = (40001, "Basic message")
        exc1 = AgentException(error_tuple)  # None converted to empty string
        assert exc1.message == "Basic message"

        # Test with whitespace additional message
        exc2 = AgentException(error_tuple, "   ")
        assert exc2.message == "Basic message"

        # Test with special characters
        exc3 = AgentException(error_tuple, "Special characters: @#$%^&*()")
        assert "Special characters: @#$%^&*()" in exc3.message

    @pytest.mark.unit
    def test_exception_attributes_access(self) -> None:
        """Test direct access to exception attributes."""
        error_tuple = (50001, "Critical error")
        exc = AgentException(error_tuple, "System failure")

        # Test attribute access
        assert hasattr(exc, "code")
        assert hasattr(exc, "message")
        assert exc.code == 50001
        assert exc.message == "Critical error:System failure"


class TestAgentExceptions:
    """Test cases for specific Agent exception classes."""

    @pytest.mark.unit
    def test_agent_normal_exc(self) -> None:
        """Test normal operation exception."""
        exc = AgentNormalExc

        # Exception objects in test environment have different attribute names
        # Use code and message instead of c and m
        assert exc.code == 0
        assert "success" in exc.message
        assert isinstance(exc, AgentExc)

    @pytest.mark.unit
    def test_agent_internal_exc(self) -> None:
        """Test internal service error exception."""
        exc = AgentInternalExc

        assert exc.code == 40500
        assert "Agent internal service error" in exc.message

    @pytest.mark.unit
    def test_bot_config_not_found_exc(self) -> None:
        """Test bot configuration not found exception."""
        exc = BotConfigNotFoundExc

        assert exc.code == 40001
        assert "Failed to get bot configuration" in exc.message

    @pytest.mark.unit
    def test_receive_ws_msg_exc(self) -> None:
        """Test WebSocket message reception exception."""
        exc = ReceiveWsMsgExc

        assert exc.code == 40002
        assert "invalid client message format for websocket" in exc.message

    @pytest.mark.unit
    def test_bot_config_invalid_exc(self) -> None:
        """Test bot configuration validation exception."""
        exc = BotConfigInvalidExc

        assert exc.code == 40003
        assert "config of the bot is invalid" in exc.message

    @pytest.mark.unit
    def test_request_spark_flow_exc(self) -> None:
        """Test Spark Flow request exception."""
        exc = RequestSparkFlowExc

        assert exc.code == 40004
        assert "failed to request flow" in exc.message

    @pytest.mark.unit
    def test_request_spark_link_exc(self) -> None:
        """Test Spark Link request exception."""
        exc = RequestSparkLinkExc

        assert exc.code == 40005
        assert "failed to request link" in exc.message

    @pytest.mark.unit
    def test_receive_http_msg_exc(self) -> None:
        """Test HTTP message reception exception."""
        exc = ReceiveHttpMsgExc

        assert exc.code == 40006
        assert "invalid client message format for api" in exc.message

    @pytest.mark.unit
    def test_exception_chaining(self) -> None:
        """Test exception chaining with cause tracking."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as original_error:
                raise AgentExc(
                    40001,
                    "Failed to get bot configuration, configuration lookup failed",
                ) from original_error
        except AgentExc as chained_exc:
            assert chained_exc.__cause__ is not None
            assert isinstance(chained_exc.__cause__, ValueError)
            assert "Original error" in str(chained_exc.__cause__)

    @pytest.mark.unit
    def test_all_agent_exceptions_have_codes(self) -> None:
        """Test that all agent exceptions have valid error codes."""
        agent_exceptions = [
            AgentNormalExc,
            AgentInternalExc,
            BotConfigNotFoundExc,
            ReceiveWsMsgExc,
            BotConfigInvalidExc,
            RequestSparkFlowExc,
            RequestSparkLinkExc,
            ReceiveHttpMsgExc,
        ]

        for exc in agent_exceptions:
            assert hasattr(exc, "code")
            assert hasattr(exc, "message")
            assert isinstance(exc.code, int)
            assert isinstance(exc.message, str)
            assert len(exc.message) > 0


class TestPluginExceptions:
    """Test cases for Plugin exception classes."""

    @pytest.mark.unit
    def test_get_tool_schema_exc(self) -> None:
        """Test tool schema retrieval exception."""
        exc = GetToolSchemaExc

        assert exc.code == 40023
        assert "Failed to get link tool protocol" in exc.message
        assert isinstance(exc, PluginExc)

    @pytest.mark.unit
    def test_run_tool_exc(self) -> None:
        """Test tool execution exception."""
        exc = RunToolExc

        assert exc.code == 40024
        assert "Failed to execute link tool" in exc.message

    @pytest.mark.unit
    def test_knowledge_query_exc(self) -> None:
        """Test knowledge base query exception."""
        exc = KnowledgeQueryExc

        assert exc.code == 40025
        assert "Failed to query knowledge base" in exc.message

    @pytest.mark.unit
    def test_get_mcp_plugin_exc(self) -> None:
        """Test MCP plugin retrieval exception."""
        exc = GetMcpPluginExc

        assert exc.code == 40026
        assert "Failed to get MCP server protocol" in exc.message

    @pytest.mark.unit
    def test_run_mcp_plugin_exc(self) -> None:
        """Test MCP plugin execution exception."""
        exc = RunMcpPluginExc

        assert exc.code == 40027
        assert "Failed to execute MCP server tool" in exc.message

    @pytest.mark.unit
    def test_run_workflow_exc(self) -> None:
        """Test workflow execution exception."""
        exc = RunWorkflowExc

        assert exc.code == 40028
        assert "Failed to call workflow tool" in exc.message

    @pytest.mark.unit
    def test_call_llm_plugin_exc(self) -> None:
        """Test LLM plugin call exception."""
        exc = CallLlmPluginExc

        assert exc.code == 40029
        assert "Failed to call large language model" in exc.message

    @pytest.mark.unit
    def test_llm_plugin_error_function(self) -> None:
        """Test LLM plugin error function."""
        with patch("exceptions.plugin_exc.ify_code_convert") as mock_convert:
            mock_convert.return_value = (500, "Converted error")

            with pytest.raises(PluginExc) as exc_info:
                llm_plugin_error(500, "LLM error")

            mock_convert.assert_called_once_with(500)
            assert isinstance(exc_info.value, PluginExc)

    @pytest.mark.unit
    def test_llm_plugin_error_with_different_codes(self) -> None:
        """Test LLM plugin error with various error codes."""
        test_cases = [
            ("400", "Client error"),
            (500, "Server error"),
            (-1, "Unknown error"),
        ]

        with patch("exceptions.plugin_exc.ify_code_convert") as mock_convert:
            for code, message in test_cases:
                mock_convert.return_value = (
                    int(str(code).replace("-", "")),
                    f"Conversion code{code}",
                )

                with pytest.raises(PluginExc):
                    llm_plugin_error(code, message)

    @pytest.mark.unit
    def test_plugin_exception_inheritance(self) -> None:
        """Test plugin exception inheritance structure."""
        plugin_exceptions = [
            GetToolSchemaExc,
            RunToolExc,
            KnowledgeQueryExc,
            GetMcpPluginExc,
            RunMcpPluginExc,
            RunWorkflowExc,
            CallLlmPluginExc,
        ]

        for exc in plugin_exceptions:
            assert isinstance(exc, PluginExc)
            assert hasattr(exc, "code")
            assert hasattr(exc, "message")


class TestMiddlewareExceptions:
    """Test cases for Middleware exception classes."""

    @pytest.mark.unit
    def test_app_auth_failed_exc(self) -> None:
        """Test application authentication failure exception."""
        exc = AppAuthFailedExc

        assert exc.code == 40040
        assert "AppId authentication information query failed" in exc.message
        assert isinstance(exc, MiddlewareExc)

    @pytest.mark.unit
    def test_ping_redis_exc(self) -> None:
        """Test Redis connection failure exception."""
        exc = PingRedisExc

        assert exc.code == 40041
        assert "Ping Redis failed" in exc.message

    @pytest.mark.unit
    def test_middleware_exception_hierarchy(self) -> None:
        """Test middleware exception inheritance."""
        middleware_exceptions = [AppAuthFailedExc, PingRedisExc]

        for exc in middleware_exceptions:
            assert isinstance(exc, MiddlewareExc)
            assert hasattr(exc, "code")
            assert hasattr(exc, "message")


class TestExceptionCodes:
    """Test cases for exception code constants."""

    @pytest.mark.unit
    def test_success_code(self) -> None:
        """Test success code constant."""
        assert codes.c_0 == (0, "success")

    @pytest.mark.unit
    def test_bot_config_codes(self) -> None:
        """Test bot configuration related codes."""
        assert codes.c_40001 == (40001, "Failed to get bot configuration")
        assert codes.c_40002 == (40002, "invalid client message format for websocket")
        assert codes.c_40003 == (40003, "config of the bot is invalid")

    @pytest.mark.unit
    def test_plugin_codes(self) -> None:
        """Test plugin related error codes."""
        assert codes.c_40023 == (40023, "Failed to get link tool protocol")
        assert codes.c_40024 == (40024, "Failed to execute link tool")
        assert codes.c_40025 == (40025, "Failed to query knowledge base")
        assert codes.c_40029 == (40029, "Failed to call large language model")

    @pytest.mark.unit
    def test_middleware_codes(self) -> None:
        """Test middleware related error codes."""
        assert codes.c_40040 == (40040, "AppId authentication information query failed")
        assert codes.c_40041 == (40041, "Ping Redis failed")

    @pytest.mark.unit
    def test_internal_error_code(self) -> None:
        """Test internal error code constant."""
        assert codes.c_40500 == (40500, "Agent internal service error")

    @pytest.mark.unit
    def test_flow_control_codes(self) -> None:
        """Test flow control related error codes."""
        assert codes.c_11200 == (
            11200,
            "Authorization error: this appId does not have authorization for related functions or business volume exceeds limit",
        )
        assert codes.c_11201 == (
            11201,
            "Authorization error: daily flow control exceeded. Exceeded daily maximum access limit",
        )
        assert codes.c_11202 == (
            11202,
            "Authorization error: second-level flow control exceeded. Second-level concurrency exceeds authorized connection limit",
        )
        assert codes.c_11203 == (
            11203,
            "Authorization error: concurrent flow control exceeded. Concurrent connections exceed authorized connection limit",
        )

    @pytest.mark.unit
    def test_content_security_codes(self) -> None:
        """Test content security related error codes."""
        assert codes.c_10013 == (
            10013,
            "Input content moderation failed, suspected violation, please adjust input content",
        )
        assert codes.c_10014 == (
            10014,
            "Output content involves sensitive information, moderation failed, subsequent results cannot be displayed to user",
        )
        assert codes.c_10019 == (
            10019,
            "Indicates that this session content has a tendency to involve violations; developers are advised to prompt users about violation-related input when receiving this error code",
        )

    @pytest.mark.unit
    def test_token_limit_codes(self) -> None:
        """Test token limit related error codes."""
        assert codes.c_10907 == (
            10907,
            "Token count exceeds limit. Conversation history + question text too long, input needs to be simplified",
        )
        assert codes.c_40372 == (
            40372,
            "Token count exceeds limit. Conversation history + question text too long, input needs to be simplified",
        )

    @pytest.mark.unit
    def test_code_constants_format(self) -> None:
        """Test error code constants format consistency."""
        # Get all code constants from the codes module
        code_attributes = [attr for attr in dir(codes) if attr.startswith("c_")]

        for attr_name in code_attributes:
            code_tuple = getattr(codes, attr_name)

            # Verify it's a tuple with two elements
            assert isinstance(code_tuple, tuple)
            assert len(code_tuple) == 2

            # Verify first element is integer (code)
            assert isinstance(code_tuple[0], int)

            # Verify second element is string (message)
            assert isinstance(code_tuple[1], str)
            assert len(code_tuple[1]) > 0


class TestExceptionIntegration:
    """Integration test cases for exception system."""

    @pytest.mark.unit
    def test_exception_hierarchy(self) -> None:
        """Test complete exception hierarchy structure."""
        # Test base exception
        base_exc = AgentException((40001, "Basic error"))
        assert isinstance(base_exc, Exception)

        # Test derived exceptions
        agent_exc = BotConfigNotFoundExc
        plugin_exc = RunToolExc
        middleware_exc = AppAuthFailedExc

        # Verify inheritance relationships
        assert isinstance(agent_exc, Exception)
        assert isinstance(plugin_exc, Exception)
        assert isinstance(middleware_exc, Exception)

    @pytest.mark.unit
    def test_multiple_exception_handling(self) -> None:
        """Test handling multiple exception types."""
        exceptions_to_test = [
            BotConfigNotFoundExc,
            RunToolExc,
            AppAuthFailedExc,
        ]

        for exc_instance in exceptions_to_test:
            with pytest.raises(type(exc_instance)) as exc_info:  # type: ignore
                raise exc_instance  # type: ignore

            # Verify each exception has required attributes
            assert hasattr(exc_info.value, "code")
            assert hasattr(exc_info.value, "message")
            assert exc_info.value.code > 0

    @pytest.mark.unit
    def test_exception_serialization(self) -> None:
        """Test exception serialization capabilities."""
        exc = BotConfigNotFoundExc

        # Test string conversion
        exc_str = str(exc)
        assert "40001" in exc_str
        assert "Failed to get bot configuration" in exc_str

        # Test repr conversion
        exc_repr = repr(exc)
        assert exc_str == exc_repr

    @pytest.mark.unit
    def test_concurrent_exception_handling(self) -> None:
        """Test concurrent exception handling scenarios."""

        async def raise_exception(exc_instance: Exception) -> None:
            await asyncio.sleep(0.01)  # Simulate async operation
            raise exc_instance

        async def test_concurrent_exceptions() -> list:
            tasks = [
                asyncio.create_task(raise_exception(BotConfigNotFoundExc)),
                asyncio.create_task(raise_exception(RunToolExc)),
                asyncio.create_task(raise_exception(AppAuthFailedExc)),
            ]

            # Collect all exceptions
            exceptions = []
            for task in tasks:
                try:
                    await task
                except (
                    AgentExc,
                    PluginExc,
                    MiddlewareExc,
                ) as exc:
                    exceptions.append(exc)

            return exceptions

        # Run concurrent test
        exceptions = asyncio.run(test_concurrent_exceptions())

        # Verify all exceptions were captured
        assert len(exceptions) == 3

        # Verify exception types by their codes
        codes_found = [exc.code for exc in exceptions]
        assert 40001 in codes_found  # BotConfigNotFoundExc
        assert 40024 in codes_found  # RunToolExc
        assert 40040 in codes_found  # AppAuthFailedExc

    @pytest.mark.unit
    def test_exception_with_none_values(self) -> None:
        """Test exception handling with None values."""
        exc1 = BotConfigNotFoundExc
        assert exc1.message != ""
        assert exc1.message is not None

        exc2 = BotConfigNotFoundExc
        assert exc2.message == "Failed to get bot configuration"

    @pytest.mark.unit
    def test_large_error_message(self) -> None:
        """Test handling of large error messages."""
        exc = BotConfigNotFoundExc

        # Test basic message length
        assert len(exc.message) > 0
        assert len(str(exc)) > 0

        # Test with custom large message
        large_message = "Very long error message " * 100
        custom_exc = AgentException((50001, "Basic error"), large_message)
        assert len(custom_exc.message) > 100
        assert "Basic error" in custom_exc.message

    @pytest.mark.unit
    def test_exception_code_uniqueness(self) -> None:
        """Test that exception codes are unique across the system."""
        all_exceptions = [
            AgentNormalExc,
            AgentInternalExc,
            BotConfigNotFoundExc,
            ReceiveWsMsgExc,
            BotConfigInvalidExc,
            RequestSparkFlowExc,
            RequestSparkLinkExc,
            ReceiveHttpMsgExc,
            GetToolSchemaExc,
            RunToolExc,
            KnowledgeQueryExc,
            GetMcpPluginExc,
            RunMcpPluginExc,
            RunWorkflowExc,
            CallLlmPluginExc,
            AppAuthFailedExc,
            PingRedisExc,
        ]

        codes_list = [exc.code for exc in all_exceptions]  # type: ignore

        # Verify all codes are unique (except for success code 0)
        non_zero_codes = [code for code in codes_list if code != 0]
        assert len(non_zero_codes) == len(set(non_zero_codes))

    @pytest.mark.unit
    def test_exception_message_localization(self) -> None:
        """Test exception message localization support."""
        # Test Chinese messages
        chinese_exceptions = [
            BotConfigNotFoundExc,
            KnowledgeQueryExc,
            AppAuthFailedExc,
        ]

        for exc in chinese_exceptions:
            # Verify Chinese characters are properly handled
            assert len(exc.message) > 0  # type: ignore
            # Check if message contains non-ASCII characters (simplified test)
            has_non_ascii = any(ord(char) > 127 for char in exc.message)  # type: ignore
            # This is no longer expected as we've translated to English
            # Original Chinese messages have been translated to English
