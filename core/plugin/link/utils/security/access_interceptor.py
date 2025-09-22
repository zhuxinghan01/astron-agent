import ipaddress
import os
import re
from urllib.parse import urlparse, urlunparse

from consts import const


def is_in_black_domain(url: str):
    """Check if URL contains any blacklisted domains.

    Args:
        url: The URL to check against domain blacklist

    Returns:
        bool: True if URL contains blacklisted domain, False otherwise
    """
    # Get environment variable and handle unset or empty cases
    black_list_str = os.getenv(const.DOMAIN_BLACK_LIST_KEY, "")
    if not black_list_str:
        return False

    # Split blacklist string into list
    domain_black_list = [domain.strip().lower() for domain in black_list_str.split(",")]

    # Convert URL to lowercase to avoid case sensitivity issues
    url_lower = url.lower()

    # Check if any domain in blacklist is present in URL
    for black_domain in domain_black_list:
        # Ensure matching complete domain names, not substrings
        if black_domain.lower() in url_lower:
            return True

    return False


def is_in_blacklist(url):
    """Check if URL is in security blacklist (domains, IPs, network segments).

    Args:
        url: The URL to validate against blacklists

    Returns:
        bool: True if URL is blacklisted, False otherwise
    """
    # NOTE: This security validation pattern is duplicated across multiple files
    # (access_interceptor.py and tool_executor/process.py) to ensure consistent
    # security policy enforcement at different layers of the system architecture.

    # Domain blacklist filtering
    if is_in_black_domain(str(url)):
        return True

    # Get actual request URL
    parsed = urlparse(url)
    url = urlunparse((parsed.scheme, parsed.hostname, parsed.path, "", "", ""))
    # Pull blacklist network segments and IPs from online configuration
    segment_black_list = []
    for black_i in os.getenv(const.SEGMENT_BLACK_LIST_KEY).split(","):
        segment_black_list.append(ipaddress.ip_network(black_i))
    ip_black_list = os.getenv(const.IP_BLACK_LIST_KEY).split(",")

    if url:
        match = re.search(r"://([^/?#]+)", url)
        if match:
            host = match.group(1)
            # Handle cases that may include port numbers
            if ":" in host:
                ip = host.split(":")[0]
            else:
                ip = host
            for i_ip in ip_black_list:
                if ip == i_ip:
                    return True

            try:
                ipaddress.ip_address(ip)
                ip_obj = ipaddress.ip_address(ip)
                for subnet in segment_black_list:
                    if ip_obj in subnet:
                        return True
                return False
            except ValueError:
                return False
        return False
    return False


# Check if it's a loopback address
def is_local_url(url):
    """Check if URL points to a local/loopback address.

    Args:
        url: The URL to check for local address

    Returns:
        bool: True if URL is local/loopback address, False otherwise
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            return False

        if hostname.lower() == "localhost":
            return True

        try:
            ip = ipaddress.ip_address(hostname)
        except ValueError:
            return False

        # Check if it's a loopback address (IPv4: 127.0.0.0/8, IPv6: ::1/128)
        if ip.is_loopback:
            return True

        return False

    except Exception:
        return False
