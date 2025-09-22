"""
Unit tests for common.otlp.ip module.
"""

import socket
from unittest.mock import Mock, patch

import pytest

from common.otlp.ip import get_host_ip, local_ip


class TestIP:
    """Test IP utility functions."""

    def test_get_host_ip(self):
        """Test get_host_ip function."""
        with patch("socket.socket") as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value = mock_sock
            mock_sock.getsockname.return_value = ("192.168.1.100", 12345)

            ip = get_host_ip()
            assert ip == "192.168.1.100"
            mock_sock.connect.assert_called_once_with(("8.8.8.8", 80))
            mock_sock.close.assert_called_once()

    def test_get_host_ip_exception(self):
        """Test get_host_ip with exception."""
        with patch("socket.socket") as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value = mock_sock
            mock_sock.connect.side_effect = Exception("Connection failed")

            ip = get_host_ip()
            assert ip == ""
            mock_sock.close.assert_called_once()

    def test_local_ip(self):
        """Test local_ip variable."""
        # local_ip is set at module level, so we can't easily test it
        # but we can verify it's a string
        assert isinstance(local_ip, str)
