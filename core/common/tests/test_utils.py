"""
Unit tests for common.utils module.
"""

from unittest.mock import Mock, patch

import pytest

from common.utils.hmac_auth import HMACAuth


class TestHMACAuth:
    """Test HMACAuth class."""

    def test_build_auth_params_basic(self):
        """Test build_auth_params with basic parameters."""
        request_url = "https://api.example.com/v1/test"
        method = "GET"
        api_key = "test_api_key"
        api_secret = "test_api_secret"

        with patch("common.utils.hmac_auth.format_date_time") as mock_format_date:
            mock_format_date.return_value = "Wed, 01 Jan 2024 12:00:00 GMT"

            result = HMACAuth.build_auth_params(
                request_url, method, api_key, api_secret
            )

            assert "host" in result
            assert "date" in result
            assert "authorization" in result
            assert result["host"] == "api.example.com"
            assert result["date"] == "Wed, 01 Jan 2024 12:00:00 GMT"
            assert isinstance(result["authorization"], str)
            assert len(result["authorization"]) > 0

    def test_build_auth_params_different_methods(self):
        """Test build_auth_params with different HTTP methods."""
        request_url = "https://api.example.com/v1/test"
        api_key = "test_api_key"
        api_secret = "test_api_secret"

        with patch("common.utils.hmac_auth.format_date_time") as mock_format_date:
            mock_format_date.return_value = "Wed, 01 Jan 2024 12:00:00 GMT"

            # Test POST method
            result_post = HMACAuth.build_auth_params(
                request_url, "POST", api_key, api_secret
            )
            assert result_post["host"] == "api.example.com"

            # Test PUT method
            result_put = HMACAuth.build_auth_params(
                request_url, "PUT", api_key, api_secret
            )
            assert result_put["host"] == "api.example.com"

            # Results should be different due to different method in signature
            assert result_post["authorization"] != result_put["authorization"]

    def test_build_auth_params_different_urls(self):
        """Test build_auth_params with different URLs."""
        api_key = "test_api_key"
        api_secret = "test_api_secret"
        method = "GET"

        with patch("common.utils.hmac_auth.format_date_time") as mock_format_date:
            mock_format_date.return_value = "Wed, 01 Jan 2024 12:00:00 GMT"

            # Test different paths
            url1 = "https://api.example.com/v1/test"
            url2 = "https://api.example.com/v1/another"

            result1 = HMACAuth.build_auth_params(url1, method, api_key, api_secret)
            result2 = HMACAuth.build_auth_params(url2, method, api_key, api_secret)

            assert result1["host"] == result2["host"]  # Same host
            assert (
                result1["authorization"] != result2["authorization"]
            )  # Different paths

    def test_build_auth_request_url(self):
        """Test build_auth_request_url method."""
        request_url = "https://api.example.com/v1/test"
        method = "GET"
        api_key = "test_api_key"
        api_secret = "test_api_secret"

        with patch("common.utils.hmac_auth.format_date_time") as mock_format_date:
            mock_format_date.return_value = "Wed, 01 Jan 2024 12:00:00 GMT"

            result = HMACAuth.build_auth_request_url(
                request_url, method, api_key, api_secret
            )

            assert result.startswith(request_url)
            assert "?" in result
            assert "host=" in result
            assert "date=" in result
            assert "authorization=" in result

    def test_build_auth_header_basic(self):
        """Test build_auth_header with basic parameters."""
        request_url = "https://api.example.com/v1/test"
        method = "GET"
        api_key = "test_api_key"
        api_secret = "test_api_secret"

        with patch("common.utils.hmac_auth.format_date_time") as mock_format_date:
            mock_format_date.return_value = "Wed, 01 Jan 2024 12:00:00 GMT"

            result = HMACAuth.build_auth_header(
                request_url, method, api_key, api_secret
            )

            assert "Method" in result
            assert "Host" in result
            assert "Date" in result
            assert "Digest" in result
            assert "Authorization" in result

            assert result["Method"] == method
            assert result["Host"] == "api.example.com"
            assert result["Date"] == "Wed, 01 Jan 2024 12:00:00 GMT"
            assert isinstance(result["Digest"], str)
            assert result["Digest"].startswith("SHA256=")
            assert isinstance(result["Authorization"], str)

    def test_build_auth_header_different_methods(self):
        """Test build_auth_header with different HTTP methods."""
        request_url = "https://api.example.com/v1/test"
        api_key = "test_api_key"
        api_secret = "test_api_secret"

        with patch("common.utils.hmac_auth.format_date_time") as mock_format_date:
            mock_format_date.return_value = "Wed, 01 Jan 2024 12:00:00 GMT"

            # Test different methods
            result_get = HMACAuth.build_auth_header(
                request_url, "GET", api_key, api_secret
            )
            result_post = HMACAuth.build_auth_header(
                request_url, "POST", api_key, api_secret
            )

            assert result_get["Method"] == "GET"
            assert result_post["Method"] == "POST"
            assert result_get["Host"] == result_post["Host"]
            assert result_get["Authorization"] != result_post["Authorization"]

    def test_build_auth_header_different_urls(self):
        """Test build_auth_header with different URLs."""
        api_key = "test_api_key"
        api_secret = "test_api_secret"
        method = "GET"

        with patch("common.utils.hmac_auth.format_date_time") as mock_format_date:
            mock_format_date.return_value = "Wed, 01 Jan 2024 12:00:00 GMT"

            url1 = "https://api.example.com/v1/test"
            url2 = "https://api.example.com/v1/another"

            result1 = HMACAuth.build_auth_header(url1, method, api_key, api_secret)
            result2 = HMACAuth.build_auth_header(url2, method, api_key, api_secret)

            assert result1["Host"] == result2["Host"]
            assert result1["Authorization"] != result2["Authorization"]

    def test_authorization_format(self):
        """Test that authorization follows expected format."""
        request_url = "https://api.example.com/v1/test"
        method = "GET"
        api_key = "test_api_key"
        api_secret = "test_api_secret"

        with patch("common.utils.hmac_auth.format_date_time") as mock_format_date:
            mock_format_date.return_value = "Wed, 01 Jan 2024 12:00:00 GMT"

            result = HMACAuth.build_auth_header(
                request_url, method, api_key, api_secret
            )
            auth_header = result["Authorization"]

            # Check that authorization contains expected components
            assert 'api_key="test_api_key"' in auth_header
            assert 'algorithm="hmac-sha256"' in auth_header
            assert "headers=" in auth_header
            assert "signature=" in auth_header

    def test_digest_format(self):
        """Test that digest follows expected format."""
        request_url = "https://api.example.com/v1/test"
        method = "GET"
        api_key = "test_api_key"
        api_secret = "test_api_secret"

        with patch("common.utils.hmac_auth.format_date_time") as mock_format_date:
            mock_format_date.return_value = "Wed, 01 Jan 2024 12:00:00 GMT"

            result = HMACAuth.build_auth_header(
                request_url, method, api_key, api_secret
            )
            digest = result["Digest"]

            assert digest.startswith("SHA256=")
            # SHA256 base64 encoded string should be 44 characters (32 bytes * 4/3)
            digest_value = digest[7:]  # Remove "SHA256=" prefix
            assert len(digest_value) == 44

    def test_empty_parameters(self):
        """Test with empty parameters."""
        request_url = "https://api.example.com/v1/test"

        with patch("common.utils.hmac_auth.format_date_time") as mock_format_date:
            mock_format_date.return_value = "Wed, 01 Jan 2024 12:00:00 GMT"

            # Test with empty api_key and api_secret
            result = HMACAuth.build_auth_params(request_url, "GET", "", "")

            assert "host" in result
            assert "date" in result
            assert "authorization" in result
            assert result["host"] == "api.example.com"

    def test_unicode_parameters(self):
        """Test with unicode parameters."""
        request_url = "https://api.example.com/v1/test"
        api_key = "测试密钥"
        api_secret = "测试密钥"

        with patch("common.utils.hmac_auth.format_date_time") as mock_format_date:
            mock_format_date.return_value = "Wed, 01 Jan 2024 12:00:00 GMT"

            result = HMACAuth.build_auth_params(request_url, "GET", api_key, api_secret)

            assert "host" in result
            assert "date" in result
            assert "authorization" in result
            assert result["host"] == "api.example.com"
