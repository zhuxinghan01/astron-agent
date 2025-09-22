"""
Pytest configuration and fixtures for common module tests.
"""

import os
import sys
from pathlib import Path

# Add the core directory to Python path for imports
core_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(core_dir))

from unittest.mock import Mock, patch

import pytest

from common.otlp.sid import SidInfo


@pytest.fixture
def mock_sid_info():
    """Mock SidInfo for testing."""
    return SidInfo(
        sub="test",
        location="test_location",
        index=1,
        local_ip="127.0.0.1",
        local_port="8080",
    )


@pytest.fixture
def mock_span():
    """Mock Span object for testing."""
    with patch("common.otlp.sid.sid_generator2") as mock_gen:
        mock_gen.gen.return_value = "test_sid_123"
        from common.otlp.trace.span import Span

        return Span(app_id="test_app", uid="test_user", chat_id="test_chat")


@pytest.fixture
def mock_oss_service():
    """Mock OSS service for testing."""
    mock_service = Mock()
    mock_service.upload_file.return_value = "http://test-bucket/test-file"
    return mock_service


@pytest.fixture
def sample_content():
    """Sample content for testing."""
    return "这是一个测试内容，包含中文和English text。"


@pytest.fixture
def sample_audit_context():
    """Sample audit context for testing."""
    from common.audit_system.base import AuditContext

    return AuditContext(
        chat_sid="test_chat_sid",
        template_id="test_template",
        chat_app_id="test_app",
        uid="test_user",
    )
