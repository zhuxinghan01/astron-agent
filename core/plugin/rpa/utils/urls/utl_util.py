"""URL 工具模块，提供 URL 验证功能。"""

from typing import Optional
from urllib.parse import urlparse


def is_valid_url(url: Optional[str]) -> bool:
    """验证给定的字符串是否为有效的 URL。"""
    try:
        result = urlparse(url)
        # 必须包含 scheme（协议）和 netloc（域名或 IP）
        return all([result.scheme, result.netloc])
    except (ValueError, AttributeError):
        return False
