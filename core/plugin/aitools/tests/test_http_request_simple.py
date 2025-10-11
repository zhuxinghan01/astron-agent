"""Simplified unit tests for HttpRequest module."""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import Mock, patch

# Import the class directly
from plugin.aitools.common.http_request import HttpRequest


class TestHttpRequestBasic:
    """Basic test cases for HttpRequest class."""

    def test_init_with_config(self):
        """Test HttpRequest initialization."""
        config = {"url": "https://test.com", "method": "GET"}
        http_req = HttpRequest(config)
        assert http_req.config == config

    def test_init_empty_config(self):
        """Test initialization with empty config."""
        http_req = HttpRequest({})
        assert http_req.config == {}

    @patch('requests.request')
    def test_send_basic(self, mock_request):
        """Test basic send functionality."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        config = {"url": "https://test.com"}
        http_req = HttpRequest(config)
        response = http_req.send()

        mock_request.assert_called_once()
        assert response == mock_response

    @patch('requests.request')
    def test_send_with_method(self, mock_request):
        """Test send with different HTTP methods."""
        mock_response = Mock()
        mock_request.return_value = mock_response

        config = {"url": "https://test.com", "method": "POST"}
        http_req = HttpRequest(config)
        http_req.send()

        # Verify POST method was used
        call_args = mock_request.call_args
        assert call_args[1]['method'] == 'POST'

    @patch('requests.request')
    def test_send_with_timeout(self, mock_request):
        """Test send with custom timeout."""
        mock_response = Mock()
        mock_request.return_value = mock_response

        config = {"url": "https://test.com", "timeout": 30}
        http_req = HttpRequest(config)
        http_req.send()

        # Verify timeout was set
        call_args = mock_request.call_args
        assert call_args[1]['timeout'] == 30

    @patch('requests.request')
    def test_send_default_values(self, mock_request):
        """Test send uses correct default values."""
        mock_response = Mock()
        mock_request.return_value = mock_response

        config = {"url": "https://test.com"}
        http_req = HttpRequest(config)
        http_req.send()

        call_args = mock_request.call_args
        assert call_args[1]['method'] == 'GET'
        assert call_args[1]['timeout'] == 10
        assert call_args[1]['headers'] == {}
        assert call_args[1]['params'] == {}
        assert call_args[1]['json'] == {}

    @patch('requests.request')
    def test_send_with_headers(self, mock_request):
        """Test send with custom headers."""
        mock_response = Mock()
        mock_request.return_value = mock_response

        headers = {"Authorization": "Bearer token"}
        config = {"url": "https://test.com", "headers": headers}
        http_req = HttpRequest(config)
        http_req.send()

        call_args = mock_request.call_args
        assert call_args[1]['headers'] == headers

    @patch('requests.request')
    def test_send_with_params(self, mock_request):
        """Test send with URL parameters."""
        mock_response = Mock()
        mock_request.return_value = mock_response

        params = {"key": "value"}
        config = {"url": "https://test.com", "params": params}
        http_req = HttpRequest(config)
        http_req.send()

        call_args = mock_request.call_args
        assert call_args[1]['params'] == params

    @patch('requests.request')
    def test_send_with_payload(self, mock_request):
        """Test send with JSON payload."""
        mock_response = Mock()
        mock_request.return_value = mock_response

        payload = {"data": "test"}
        config = {"url": "https://test.com", "payload": payload}
        http_req = HttpRequest(config)
        http_req.send()

        call_args = mock_request.call_args
        assert call_args[1]['json'] == payload

    @patch('requests.request')
    def test_method_case_conversion(self, mock_request):
        """Test that method is converted to uppercase."""
        mock_response = Mock()
        mock_request.return_value = mock_response

        config = {"url": "https://test.com", "method": "post"}
        http_req = HttpRequest(config)
        http_req.send()

        call_args = mock_request.call_args
        assert call_args[1]['method'] == 'POST'