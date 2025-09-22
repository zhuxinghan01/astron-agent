"""HTTP request processing module for tool execution.

This module provides HTTP request execution functionality with various
authentication methods and security validations.
"""

import json
import os
import re
import ipaddress
from urllib.parse import urljoin, urlparse, urlunparse, quote

import aiohttp

from plugin.link.exceptions.sparklink_exceptions import CallThirdApiException
from plugin.link.utils.errors.code import ErrCode
from plugin.link.consts import const
from plugin.link.infra.tool_exector.http_auth import public_query_url, assemble_ws_auth_url


class HttpRun:
    """HTTP request executor with authentication and security validation.

    Handles various authentication methods including MD5 and HMAC,
    validates against blacklists, and executes HTTP requests safely.

    Instance Attributes Organization:

    Request Configuration:
        - server: Target server URL
        - method: HTTP method (GET, POST, etc.)
        - path: Request path components
        - query: Query parameters dictionary
        - header: HTTP headers dictionary
        - body: Request body data

    Authentication State:
        - _is_authorization_md5: Boolean flag for MD5 auth detection
        - _is_auth_hmac: Boolean flag for HMAC auth detection
        - auth_con_js: HMAC authentication configuration object

    Security Validation:
        - _is_official: Boolean flag marking official API status
        - _is_in_blacklist: Boolean flag for blacklist validation result

    All attributes serve specific roles in HTTP request processing,
    authentication handling, and security validation workflows.
    """

    def __init__(self, server, method, path, query, header, body, open_api_schema=None):
        self.server = server
        self.method = method
        self.path = path
        self.query = query
        self.header = header
        self.body = body
        try:
            self._is_authorization_md5 = HttpRun.is_authorization_md5(open_api_schema)
        except Exception:
            self._is_authorization_md5 = False
        try:
            self._is_auth_hmac, self.auth_con_js = HttpRun.is_authorization_hmac(
                self.header
            )
        except Exception:
            self._is_auth_hmac = False
            self.auth_con_js = object
        try:
            self._is_official = HttpRun.is_official(open_api_schema)
        except Exception:
            self._is_official = False
        try:
            self._is_in_blacklist = HttpRun.is_in_blacklist(self.server)
        except Exception:
            self._is_in_blacklist = False

    async def do_call(self, span):
        """Execute the HTTP request with proper authentication and validation.

        Args:
            span: Tracing span for request monitoring

        Returns:
            str: Response text from the HTTP request

        Raises:
            CallThirdApiException: When request fails or server is blacklisted
        """
        url = self.server

        # DECISION TREE: Security validation - block blacklisted servers immediately
        if self._is_in_blacklist:
            raise CallThirdApiException(
                code=ErrCode.SERVER_VALIDATE_ERR.code,
                err_pre=ErrCode.SERVER_VALIDATE_ERR.msg,
                err="Request tool path hostname is in blacklist",
            )

        # BRANCH 1: URL path construction
        path_res = [frag for _, frag in self.path.items()]
        if self.path:
            url = urljoin(url, path_res[0])

        # DECISION TREE: Authentication method selection and URL construction
        if self._is_authorization_md5:
            # BRANCH 2A: MD5 Authentication flow
            url = public_query_url(url)
            if self.query:
                url = url + "&" + "&".join([f"{k}={v}" for k, v in self.query.items()])
        elif self._is_auth_hmac:
            # BRANCH 2B: HMAC Authentication flow
            url, headers = assemble_ws_auth_url(
                url, self.method, self.auth_con_js, self.body
            )
            self.header = headers
        else:
            # BRANCH 2C: No authentication - standard query parameter handling
            if self.query:
                url = url + "?" + "&".join([f"{k}={v}" for k, v in self.query.items()])

        third_result = ""
        with span.start(func_name="http_run") as span_context:
            try:
                try:
                    self.header.pop("@type")
                except Exception:
                    pass

                encoded_url = quote(url, safe="/:?=&")
                span_context.add_info_event(
                    f"raw_url: {url}, encoded_url: {encoded_url}"
                )
                span_context.add_info_event(
                    f"encoded_url: {encoded_url}, header: {self.header}, "
                    f"body: {self.body}"
                )
                # third_result = request(self.method, encoded_url, \
                #                       headers=self.header, json=self.body)
                status_code = 0
                third_result = ""
                kwargs = {}
                kwargs["headers"] = self.header if self.header else None
                kwargs["json"] = self.body if self.body else None
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        self.method, encoded_url, **kwargs
                    ) as response:
                        third_result = await response.text()
                        status_code = response.status

                span_context.add_info_event(f"{status_code}")
                span_context.add_info_event(f"{third_result}")
            except Exception as err:
                span.add_error_event(str(err))

                # DECISION TREE: Error code selection based on API type
                code_return = ErrCode.THIRD_API_REQUEST_FAILED_ERR.code
                err_pre_return = ErrCode.THIRD_API_REQUEST_FAILED_ERR.msg
                if self._is_official:
                    # BRANCH 3A: Official API error handling
                    code_return = ErrCode.OFFICIAL_API_REQUEST_FAILED_ERR.code
                    err_pre_return = ErrCode.OFFICIAL_API_REQUEST_FAILED_ERR.msg
                raise CallThirdApiException(
                    code=code_return, err_pre=err_pre_return, err=err
                ) from err

        # DECISION TREE: Status code validation and error response handling
        if status_code != 200:
            err_reason = f"Request error code: {status_code}, error message {third_result}"
            code_return = ErrCode.THIRD_API_REQUEST_FAILED_ERR.code
            err_pre_return = ErrCode.THIRD_API_REQUEST_FAILED_ERR.msg
            if self._is_official:
                # BRANCH 4: Official API status error handling
                code_return = ErrCode.OFFICIAL_API_REQUEST_FAILED_ERR.code
                err_pre_return = ErrCode.OFFICIAL_API_REQUEST_FAILED_ERR.msg
            raise CallThirdApiException(
                code=code_return, err_pre=err_pre_return, err=err_reason
            )
        return third_result

    @staticmethod
    def is_authorization_md5(open_api_schema):
        """Check if the API uses MD5 authorization.

        Args:
            open_api_schema: OpenAPI schema definition

        Returns:
            bool: True if MD5 authorization is used
        """
        if open_api_schema:
            paths = open_api_schema.get("paths")
            for _, get_dict in paths.items():
                parameters = get_dict["get"]["parameters"]
                for para in parameters:
                    if (
                        para["in"] == "header"
                        and para["name"] == "Authorization"
                        and para["schema"]["default"] == "MD5"
                    ):
                        return True
        return False

    @staticmethod
    def is_authorization_hmac(header):
        """Check if the request uses HMAC authorization.

        Args:
            header: Request headers dictionary

        Returns:
            tuple: (is_hmac, auth_config) - boolean and config object
        """
        if header:
            authorization = header.get("Authorization")
            if authorization and len(authorization) != 0:
                try:
                    ix = authorization.index(":")
                    auth_prefix = authorization[:ix]
                    if auth_prefix == "HMAC":
                        auth_con = authorization[ix + 1:].strip()
                        try:
                            auth_con_js = json.loads(auth_con)
                            return True, auth_con_js
                        except json.JSONDecodeError:
                            # Handle malformed JSON gracefully
                            return False, object
                except ValueError:
                    # Handle missing colon gracefully
                    return False, object

        return False, object

    @staticmethod
    def is_official(open_api_schema):
        """Check if the API is marked as official.

        Args:
            open_api_schema: OpenAPI schema definition

        Returns:
            bool: True if API is official
        """
        if open_api_schema:
            info = open_api_schema.get("info")
            if info.get("x-is-official"):
                return True

        return False

    @staticmethod
    def is_in_black_domain(url: str):
        """Check if URL domain is in the domain blacklist.

        Args:
            url: URL to check

        Returns:
            bool: True if domain is blacklisted
        """
        # Get environment variable and handle unset or empty cases
        black_list_str = os.getenv(const.DOMAIN_BLACK_LIST_KEY, "")
        if not black_list_str:
            return False

        # Split blacklist string into list
        domain_black_list = [
            domain.strip().lower() for domain in black_list_str.split(",")
        ]

        # Convert URL to lowercase to avoid case issues
        url_lower = url.lower()

        # Check if blacklisted domains are in URL
        for black_domain in domain_black_list:
            # Ensure matching complete domain names, not substrings
            if black_domain.lower() in url_lower:
                return True

        return False

    @staticmethod
    def is_in_blacklist(url):
        """Check if URL is in IP or network segment blacklist.

        Args:
            url: URL to validate against blacklists

        Returns:
            bool: True if URL is blacklisted
        """
        # SECTION 1: Domain-based blacklist validation
        # Domain blacklist filtering
        if HttpRun.is_in_black_domain(str(url)):
            return True

        # SECTION 2: URL parsing and normalization
        # Get real request URL
        parsed = urlparse(url)
        url = urlunparse((parsed.scheme, parsed.hostname, parsed.path, "", "", ""))

        # SECTION 3: Blacklist configuration loading
        # Pull blacklist network segments and IPs from online configuration
        segment_black_list = []
        for black_i in os.getenv(const.SEGMENT_BLACK_LIST_KEY).split(","):
            segment_black_list.append(ipaddress.ip_network(black_i))
        ip_black_list = os.getenv(const.IP_BLACK_LIST_KEY).split(",")

        # SECTION 4: IP extraction and validation
        if url:
            match = re.search(r"://([^/?#]+)", url)
            if match:
                host = match.group(1)
                # Handle cases that might include port numbers
                if ":" in host:
                    ip = host.split(":")[0]
                else:
                    ip = host

                # SECTION 5: IP blacklist checking
                for i_ip in ip_black_list:
                    if ip == i_ip:
                        return True

                # SECTION 6: Network segment validation
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
