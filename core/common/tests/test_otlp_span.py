"""
Unit tests for common.otlp.trace.span module.
"""

from unittest.mock import Mock, patch

import pytest

from common.otlp.trace.span import Span


class TestSpan:
    """Test Span class."""

    def test_init_without_sid_generator(self):
        """Test initialization without sid_generator2."""
        with patch("common.otlp.sid.sid_generator2", None):
            with pytest.raises(Exception, match="sid_generator2 is not initialized"):
                Span()

    def test_init_basic(self):
        """Test basic initialization."""
        with patch("common.otlp.sid.sid_generator2") as mock_gen:
            mock_gen.gen.return_value = "test_sid_123"

            span = Span(app_id="test_app", uid="test_user", chat_id="test_chat")

            assert span.app_id == "test_app"
            assert span.uid == "test_user"
            assert span.chat_id == "test_chat"
            assert span.sid == "test_sid_123"

    def test_init_with_oss_service(self):
        """Test initialization with OSS service."""
        mock_oss_service = Mock()

        with patch("common.otlp.sid.sid_generator2") as mock_gen:
            mock_gen.gen.return_value = "test_sid_123"

            span = Span(
                app_id="test_app",
                uid="test_user",
                chat_id="test_chat",
                oss_service=mock_oss_service,
            )

            assert span.oss_service == mock_oss_service

    def test_get_source_function_name(self):
        """Test _get_source_function_name method."""
        with patch("common.otlp.sid.sid_generator2") as mock_gen:
            mock_gen.gen.return_value = "test_sid_123"

            span = Span()

            # Test with mock frame
            with patch("inspect.currentframe") as mock_frame:
                mock_cf = Mock()
                mock_cf.f_back.f_back.f_back.f_code.co_name = "test_function"
                mock_frame.return_value = mock_cf

                func_name = span._get_source_function_name()
                assert func_name == "test_function"

    def test_get_source_function_name_no_frame(self):
        """Test _get_source_function_name with no frame."""
        with patch("common.otlp.sid.sid_generator2") as mock_gen:
            mock_gen.gen.return_value = "test_sid_123"

            span = Span()

            with patch("inspect.currentframe", return_value=None):
                func_name = span._get_source_function_name()
                assert func_name == "unknown"

    def test_start_context_manager(self):
        """Test start context manager."""
        with patch("common.otlp.sid.sid_generator2") as mock_gen:
            mock_gen.gen.return_value = "test_sid_123"

            span = Span()

            with patch("trace.get_tracer") as mock_tracer:
                mock_tracer_instance = Mock()
                mock_tracer.return_value = mock_tracer_instance
                mock_tracer_instance.start_as_current_span.return_value.__enter__.return_value = (
                    Mock()
                )

                with span.start("test_function") as context_span:
                    assert context_span == span

    def test_set_attribute(self):
        """Test set_attribute method."""
        with patch("common.otlp.sid.sid_generator2") as mock_gen:
            mock_gen.gen.return_value = "test_sid_123"

            span = Span()

            with patch("trace.get_current_span") as mock_current_span:
                mock_span = Mock()
                mock_current_span.return_value = mock_span

                span.set_attribute("test_key", "test_value")
                mock_span.set_attribute.assert_called_once_with(
                    "test_key", "test_value"
                )

    def test_set_status(self):
        """Test set_status method."""
        with patch("common.otlp.sid.sid_generator2") as mock_gen:
            mock_gen.gen.return_value = "test_sid_123"

            span = Span()

            with patch("trace.get_current_span") as mock_current_span:
                mock_span = Mock()
                mock_current_span.return_value = mock_span

                from opentelemetry.trace import Status, StatusCode

                status = Status(StatusCode.ERROR)
                span.set_status(status)
                mock_span.set_status.assert_called_once_with(status)

    def test_set_attributes(self):
        """Test set_attributes method."""
        with patch("common.otlp.sid.sid_generator2") as mock_gen:
            mock_gen.gen.return_value = "test_sid_123"

            span = Span()

            with patch("trace.get_current_span") as mock_current_span:
                mock_span = Mock()
                mock_current_span.return_value = mock_span

                attributes = {"key1": "value1", "key2": "value2"}
                span.set_attributes(attributes)
                mock_span.set_attributes.assert_called_once_with(attributes)

    def test_set_code(self):
        """Test set_code method."""
        with patch("common.otlp.sid.sid_generator2") as mock_gen:
            mock_gen.gen.return_value = "test_sid_123"

            span = Span()

            with patch.object(span, "set_attribute") as mock_set_attr:
                span.set_code(200)
                mock_set_attr.assert_called_once_with("code", 200)

    def test_get_otlp_span(self):
        """Test get_otlp_span method."""
        with patch("common.otlp.sid.sid_generator2") as mock_gen:
            mock_gen.gen.return_value = "test_sid_123"

            span = Span()

            with patch("trace.get_current_span") as mock_current_span:
                mock_span = Mock()
                mock_current_span.return_value = mock_span

                result = span.get_otlp_span()
                assert result == mock_span

    def test_record_exception(self):
        """Test record_exception method."""
        with patch("common.otlp.sid.sid_generator2") as mock_gen:
            mock_gen.gen.return_value = "test_sid_123"

            span = Span()

            with patch("trace.get_current_span") as mock_current_span:
                mock_span = Mock()
                mock_current_span.return_value = mock_span

                with patch.object(span, "set_status") as mock_set_status:
                    with patch("time.time", return_value=1640995200.0):
                        exception = Exception("Test exception")
                        span.record_exception(exception)

                        mock_span.record_exception.assert_called_once()
                        mock_set_status.assert_called_once()

    def test_add_event(self):
        """Test add_event method."""
        with patch("common.otlp.sid.sid_generator2") as mock_gen:
            mock_gen.gen.return_value = "test_sid_123"

            span = Span()

            with patch("trace.get_current_span") as mock_current_span:
                mock_span = Mock()
                mock_current_span.return_value = mock_span

                attributes = {"key": "value"}
                span.add_event("test_event", attributes=attributes)
                mock_span.add_event.assert_called_once_with(
                    "test_event", attributes=attributes, timestamp=None
                )

    def test_add_info_event(self):
        """Test add_info_event method."""
        with patch("common.otlp.sid.sid_generator2") as mock_gen:
            mock_gen.gen.return_value = "test_sid_123"

            span = Span()

            with patch("trace.get_current_span") as mock_current_span:
                mock_span = Mock()
                mock_current_span.return_value = mock_span

                span.add_info_event("test info")
                mock_span.add_event.assert_called_once_with(
                    "INFO", attributes={"INFO LOG": "test info"}
                )

    def test_add_info_event_large_content(self):
        """Test add_info_event with large content."""
        with patch("common.otlp.sid.sid_generator2") as mock_gen:
            mock_gen.gen.return_value = "test_sid_123"

            mock_oss_service = Mock()
            mock_oss_service.upload_file.return_value = "http://test-bucket/test-file"
            span = Span(oss_service=mock_oss_service)

            with patch("trace.get_current_span") as mock_current_span:
                mock_span = Mock()
                mock_current_span.return_value = mock_span

                # Create large content
                large_content = "x" * (10 * 1024 + 1)  # Larger than SPAN_SIZE_LIMIT
                span.add_info_event(large_content)

                # Should upload to OSS
                mock_oss_service.upload_file.assert_called_once()
                mock_span.add_event.assert_called_once()

    def test_add_error_event(self):
        """Test add_error_event method."""
        with patch("common.otlp.sid.sid_generator2") as mock_gen:
            mock_gen.gen.return_value = "test_sid_123"

            span = Span()

            with patch("trace.get_current_span") as mock_current_span:
                mock_span = Mock()
                mock_current_span.return_value = mock_span

                with patch.object(span, "set_attribute") as mock_set_attr:
                    span.add_error_event("test error")
                    mock_set_attr.assert_called_once_with("error", True)
                    mock_span.add_event.assert_called_once_with(
                        "ERROR", attributes={"ERROR LOG": "test error"}
                    )

