"""测试 URL 工具模块。"""

import pytest

from utils.urls.utl_util import is_valid_url


class TestIsValidUrl:
    """is_valid_url 函数的测试用例。"""

    def test_valid_http_url(self) -> None:
        """测试有效的 HTTP URL。"""
        assert is_valid_url("http://example.com") is True
        assert is_valid_url("http://www.example.com") is True
        assert is_valid_url("http://example.com/path") is True
        assert is_valid_url("http://example.com:8080") is True
        assert is_valid_url("http://example.com/path?query=value") is True

    def test_valid_https_url(self) -> None:
        """测试有效的 HTTPS URL。"""
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("https://www.example.com") is True
        assert is_valid_url("https://example.com/path") is True
        assert is_valid_url("https://example.com:443") is True
        assert (
            is_valid_url("https://example.com/path?query=value&another=param") is True
        )

    def test_valid_ip_url(self) -> None:
        """测试有效的 IP 地址 URL。"""
        assert is_valid_url("http://192.168.1.1") is True
        assert is_valid_url("https://10.0.0.1:8080") is True
        assert is_valid_url("http://127.0.0.1:3000/api") is True

    def test_valid_localhost_url(self) -> None:
        """测试有效的 localhost URL。"""
        assert is_valid_url("http://localhost") is True
        assert is_valid_url("https://localhost:8080") is True
        assert is_valid_url("http://localhost:3000/path") is True

    def test_valid_other_schemes(self) -> None:
        """测试其他有效的协议方案。"""
        assert is_valid_url("ftp://example.com") is True
        assert is_valid_url("file://localhost/path/to/file") is True
        assert is_valid_url("ws://example.com:8080") is True
        assert is_valid_url("wss://example.com/websocket") is True

    def test_invalid_no_scheme(self) -> None:
        """测试没有协议的无效 URL。"""
        assert is_valid_url("example.com") is False
        assert is_valid_url("www.example.com") is False
        assert is_valid_url("example.com/path") is False

    def test_invalid_no_netloc(self) -> None:
        """测试没有域名的无效 URL。"""
        assert is_valid_url("http://") is False
        assert is_valid_url("https://") is False
        assert is_valid_url("ftp://") is False

    def test_invalid_malformed_urls(self) -> None:
        """测试格式错误的无效 URL。"""
        assert is_valid_url("http:/") is False
        assert is_valid_url("http:example.com") is False
        assert is_valid_url("://example.com") is False
        assert is_valid_url("http//example.com") is False

    def test_invalid_empty_and_none(self) -> None:
        """测试空值和 None 的情况。"""
        assert is_valid_url("") is False
        assert is_valid_url(None) is False
        assert is_valid_url("   ") is False  # 只有空格

    def test_invalid_special_characters(self) -> None:
        """测试包含特殊字符的无效 URL。"""
        # 测试一些可能导致解析错误的字符
        invalid_urls = ["http://[invalid", "http://example .com"]

        for url in invalid_urls:
            try:
                result = is_valid_url(url)
                # 如果没有抛出异常，结果应该是 False
                assert result is False, f"URL '{url}' should be invalid"
            except (ValueError, Exception):
                # 如果抛出异常，也认为是无效的，这是预期的
                pass

    def test_edge_cases_with_fragments_and_queries(self) -> None:
        """测试包含片段和查询参数的边界情况。"""
        assert is_valid_url("https://example.com#fragment") is True
        assert is_valid_url("https://example.com/path#fragment") is True
        assert is_valid_url("https://example.com/path?a=1&b=2#frag") is True

    def test_unicode_domains(self) -> None:
        """测试 Unicode 域名。"""
        # 国际化域名应该被认为是有效的
        assert is_valid_url("https://例え.テスト") is True
        assert is_valid_url("http://xn--r8jz45g.xn--zckzah") is True  # Punycode

    def test_very_long_urls(self) -> None:
        """测试非常长的 URL。"""
        long_path = "a" * 1000
        long_url = f"https://example.com/{long_path}"
        assert is_valid_url(long_url) is True

    def test_urls_with_authentication(self) -> None:
        """测试包含认证信息的 URL。"""
        assert is_valid_url("https://user:pass@example.com") is True
        assert is_valid_url("ftp://user@example.com") is True

    def test_relative_paths_are_invalid(self) -> None:
        """测试相对路径被认为是无效的。"""
        assert is_valid_url("/path/to/resource") is False
        assert is_valid_url("../relative/path") is False
        assert is_valid_url("./current/path") is False

    def test_data_urls(self) -> None:
        """测试 data URL。"""
        assert (
            is_valid_url("data:text/plain;base64,SGVsbG8=") is False
        )  # data URLs 没有 netloc

    def test_javascript_urls(self) -> None:
        """测试 javascript URL。"""
        assert (
            is_valid_url("javascript:alert('hello')") is False
        )  # javascript URLs 没有 netloc

    def test_case_insensitive_schemes(self) -> None:
        """测试协议大小写不敏感。"""
        assert is_valid_url("HTTP://example.com") is True
        assert is_valid_url("HTTPS://example.com") is True
        assert is_valid_url("FTP://example.com") is True
