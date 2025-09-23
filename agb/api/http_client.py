# -*- coding: utf-8 -*-
"""
HTTP client interface implementation
Provides HTTP communication functionality with AGB API
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import aiohttp
import requests

from .models.call_mcp_tool_request import CallMcpToolRequest
from .models.call_mcp_tool_response import CallMcpToolResponse
from .models.create_session_request import CreateSessionRequest
from .models.create_session_response import CreateSessionResponse
from .models.get_link_request import GetLinkRequest
from .models.get_link_response import GetLinkResponse
from .models.get_mcp_resource_request import GetMcpResourceRequest
from .models.get_mcp_resource_response import GetMcpResourceResponse
from .models.init_browser_request import InitBrowserRequest
from .models.init_browser_response import InitBrowserResponse
from .models.list_mcp_tools_request import ListMcpToolsRequest
from .models.list_mcp_tools_response import ListMcpToolsResponse
from .models.release_session_request import ReleaseSessionRequest
from .models.release_session_response import ReleaseSessionResponse


class HTTPClient:
    """HTTP client class for communicating with AGB API"""

    # Class-level default configuration
    _default_config = None

    @classmethod
    def set_default_config(cls, config):
        """Set default configuration for all HTTPClient instances"""
        cls._default_config = config

    @classmethod
    def get_default_config(cls):
        """Get default configuration"""
        return cls._default_config

    def __init__(self, api_key: str = "", cfg=None):
        """
        Initialize HTTP client

        Args:
            api_key (str): API key for authentication
            cfg (Config): Configuration object, if not provided will use default config
        """
        # Load configuration
        if cfg is not None:
            # Use provided configuration object
            self.timeout_ms = cfg.timeout_ms
            endpoint = cfg.endpoint
            self.api_key = api_key
        else:
            # Use default configuration if available
            if self._default_config is not None:
                self.timeout_ms = self._default_config.timeout_ms
                endpoint = self._default_config.endpoint
                self.api_key = api_key
            else:
                raise ValueError("No configuration provided and no default config set")

        # Process endpoint - ensure it includes http:// prefix
        self._process_endpoint(endpoint)

        # Process timeout - convert milliseconds to seconds
        self.timeout = self.timeout_ms // 1000

        # Ensure base_url is not empty
        if not self.base_url:
            raise ValueError("base_url cannot be empty")

        self.session = requests.Session()

        # Add Authorization header
        self.session.headers["authorization"] = self.api_key

        # Set default request headers
        self.session.headers.update(
            {
                "Content-Type": "application/json",
            }
        )

    def _process_endpoint(self, endpoint: str):
        """Process endpoint logic"""
        # Use endpoint from config directly as base_url, ensure it includes http:// prefix
        if endpoint and not endpoint.startswith(("http://", "https://")):
            self.base_url = f"http://{endpoint}"
        else:
            self.base_url = endpoint

    def create_session(self, request: CreateSessionRequest) -> CreateSessionResponse:
        """
        HTTP request interface for creating session

        Args:
            request (CreateSessionRequest): Request object for creating session

        Returns:
            CreateSessionResponse: Structured response object
        """
        # Build request headers
        headers: Dict[str, str] = {}

        # Build query parameters
        params = request.get_params()

        # Build request body
        body = request.get_body()

        # Call _make_request
        response_dict = self._make_request(
            method="POST",
            endpoint="/mcp/createSession",
            headers=headers,
            params=params,
            json_data=body,
        )

        # Return structured response object
        return CreateSessionResponse.from_http_response(response_dict)

    def release_session(self, request: ReleaseSessionRequest) -> ReleaseSessionResponse:
        """
        HTTP request interface for releasing session

        Args:
            request (ReleaseSessionRequest): Request object for releasing session

        Returns:
            ReleaseSessionResponse: Structured response object
        """
        # Build request headers
        headers: Dict[str, str] = {}

        # Build query parameters
        params = request.get_params()

        # Build request body
        body = request.get_body()

        # Call _make_request
        response_dict = self._make_request(
            method="POST",
            endpoint="/mcp/releaseSession",
            headers=headers,
            params=params,
            json_data=body,
        )

        # Return structured response object
        return ReleaseSessionResponse.from_http_response(response_dict)

    def call_mcp_tool(
        self,
        request: CallMcpToolRequest,
        read_timeout: Optional[int] = None,
        connect_timeout: Optional[int] = None,
    ) -> CallMcpToolResponse:
        """
        HTTP request interface for calling MCP tool

        Args:
            request (CallMcpToolRequest): Request object for calling MCP tool

        Returns:
            CallMcpToolResponse: Structured response object
        """
        # Build request headers
        headers: Dict[str, str] = {}

        # Build query parameters
        params = request.get_params()

        # Build request body
        body = request.get_body()

        # Call _make_request
        response_dict = self._make_request(
            method="POST",
            endpoint="/mcp",
            headers=headers,
            params=params,
            json_data=body,
            read_timeout=read_timeout,
            connect_timeout=connect_timeout,
        )

        # Return structured response object
        return CallMcpToolResponse.from_http_response(response_dict)

    def list_mcp_tools(self, request: ListMcpToolsRequest) -> ListMcpToolsResponse:
        """
        HTTP request interface for listing MCP tools

        Args:
            request (ListMcpToolsRequest): Request object for listing MCP tools

        Returns:
            ListMcpToolsResponse: Structured response object
        """
        # Build request headers
        headers: Dict[str, str] = {}

        # Build query parameters
        params = request.get_params()

        # Build request body
        body = request.get_body()

        # Call _make_request
        response_dict = self._make_request(
            method="POST",
            endpoint="/mcp/listTools",
            headers=headers,
            params=params,
            json_data=body,
        )

        # Return structured response object
        return ListMcpToolsResponse.from_http_response(response_dict)

    def get_mcp_resource(
        self, request: GetMcpResourceRequest
    ) -> GetMcpResourceResponse:
        """
        HTTP request interface for getting MCP resource

        Args:
            request (GetMcpResourceRequest): Request object for getting MCP resource

        Returns:
            GetMcpResourceResponse: Structured response object
        """
        # Build request headers
        headers: Dict[str, str] = {}

        # Build query parameters
        params = request.get_params()

        # Build request body
        body = request.get_body()

        # Call _make_request
        response_dict = self._make_request(
            method="POST",
            endpoint="/mcp/getMcpResource",
            headers=headers,
            params=params,
            json_data=body,
        )

        # Return structured response object
        return GetMcpResourceResponse.from_http_response(response_dict)

    def init_browser(self, request: InitBrowserRequest) -> InitBrowserResponse:
        """
        HTTP request interface for initializing browser

        Args:
            request (InitBrowserRequest): Request object for initializing browser

        Returns:
            InitBrowserResponse: Structured response object
        """
        # Build request headers
        headers: Dict[str, str] = {}

        # Build query parameters
        params = request.get_params()

        # Build request body
        body = request.get_body()

        # Call _make_request
        response_dict = self._make_request(
            method="POST",
            endpoint="/browser/init",
            headers=headers,
            params=params,
            json_data=body,
        )

        # Return structured response object
        return InitBrowserResponse.from_http_response(response_dict)

    async def init_browser_async(
        self, request: InitBrowserRequest
    ) -> InitBrowserResponse:
        """
        Async HTTP request interface for initializing browser

        Args:
            request (InitBrowserRequest): Request object for initializing browser

        Returns:
            InitBrowserResponse: Structured response object
        """
        # Build request headers
        headers: Dict[str, str] = {}

        # Build query parameters
        params = request.get_params()

        # Build request body
        body = request.get_body()

        # Call async _make_request
        response_dict = await self._make_request_async(
            method="POST",
            endpoint="/browser/init",
            headers=headers,
            params=params,
            json_data=body,
        )

        # Return structured response object
        return InitBrowserResponse.from_http_response(response_dict)

    def get_link(self, request: GetLinkRequest) -> GetLinkResponse:
        """
        HTTP request interface for getting session link

        Args:
            request (GetLinkRequest): Request object for getting session link

        Returns:
            GetLinkResponse: Structured response object
        """
        # Build request headers
        headers: Dict[str, str] = {}

        # Build query parameters
        params = request.get_params()

        # Call _make_request
        response_dict = self._make_request(
            method="GET", endpoint="/internet/getLink", headers=headers, params=params
        )

        # Return structured response object
        return GetLinkResponse.from_http_response(response_dict)

    async def get_link_async(self, request: GetLinkRequest) -> GetLinkResponse:
        """
        Async HTTP request interface for getting session link

        Args:
            request (GetLinkRequest): Request object for getting session link

        Returns:
            GetLinkResponse: Structured response object
        """
        # Build request headers
        headers: Dict[str, str] = {}

        # Build query parameters
        params = request.get_params()

        # Call async _make_request
        response_dict = await self._make_request_async(
            method="GET", endpoint="/mcp/getLink", headers=headers, params=params
        )

        # Return structured response object
        return GetLinkResponse.from_http_response(response_dict)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        read_timeout: Optional[int] = None,
        connect_timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute HTTP request

        Args:
            method (str): HTTP method
            endpoint (str): API endpoint
            headers (Optional[Dict[str, str]]): Request headers
            params (Optional[Dict[str, Any]]): Query parameters
            json_data (Optional[Dict[str, Any]]): JSON data
            data (Optional[Dict[str, Any]]): Form data

        Returns:
            Dict[str, Any]: Response result
        """
        url = f"{self.base_url}{endpoint}"

        # Merge request headers and ensure all values are strings
        request_headers: Dict[str, str] = {}
        for key, value in self.session.headers.items():
            request_headers[str(key)] = str(value)

        # Add Authorization header
        request_headers["authorization"] = self.api_key

        if headers:
            request_headers.update(headers)

        # Determine timeout values
        if read_timeout is not None and connect_timeout is not None:
            # Use separate connect and read timeouts
            timeout = (
                connect_timeout / 1000,
                read_timeout / 1000,
            )  # Convert ms to seconds
            timeout_display = f"connect={connect_timeout}ms, read={read_timeout}ms"
        else:
            # Use default timeout
            timeout = self.timeout
            timeout_display = f"{self.timeout} seconds"

        # Print request information
        print("\n=== HTTP Request Information ===")
        print(f"URL: {url}")
        print(f"Timeout: {timeout_display}")

        if params:
            print(f"Query Parameters: {params}")
        else:
            print("Query Parameters: None")

        if json_data:
            print(f"JSON Data: {json_data}")
        elif data:
            print(f"Form Data: {data}")
        else:
            print("Request Body: None")

        print("=" * 50)

        try:
            # Execute request
            if method.upper() == "GET":
                response = self.session.get(
                    url, headers=request_headers, params=params, timeout=timeout
                )
            elif method.upper() == "POST":
                if json_data:
                    response = self.session.post(
                        url,
                        headers=request_headers,
                        params=params,
                        json=json_data,
                        timeout=timeout,
                    )
                else:
                    response = self.session.post(
                        url,
                        headers=request_headers,
                        params=params,
                        data=data,
                        json={},
                        timeout=timeout,
                    )
            elif method.upper() == "PUT":
                response = self.session.put(
                    url,
                    headers=request_headers,
                    params=params,
                    json=json_data,
                    timeout=timeout,
                )
            elif method.upper() == "DELETE":
                response = self.session.delete(
                    url, headers=request_headers, params=params, timeout=timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Build response result
            result = {
                "status_code": response.status_code,
                "url": response.url,
                "headers": dict(response.headers),
                "success": response.status_code < 400,
            }

            # Try to parse JSON response
            try:
                result["json"] = response.json()
            except ValueError:
                result["text"] = response.text
                result["json"] = None

            # Print response information
            print("\n=== HTTP Response Information ===")
            print(
                f"Response Body: {result.get('json', result.get('text', 'No content'))}"
            )
            print("=" * 50)

            return result

        except requests.exceptions.RequestException as e:
            # Print error information
            print("\n=== HTTP Request Error ===")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print(f"Request URL: {url}")
            print("=" * 50)

            return {"success": False, "error": str(e), "status_code": None, "url": url}

    async def _make_request_async(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute async HTTP request using aiohttp

        Args:
            method (str): HTTP method
            endpoint (str): API endpoint
            headers (Optional[Dict[str, str]]): Request headers
            params (Optional[Dict[str, Any]]): Query parameters
            json_data (Optional[Dict[str, Any]]): JSON data
            data (Optional[Dict[str, Any]]): Form data

        Returns:
            Dict[str, Any]: Response result
        """
        url = f"{self.base_url}{endpoint}"

        # Merge request headers and ensure all values are strings
        request_headers: Dict[str, str] = {}
        for key, value in self.session.headers.items():
            request_headers[str(key)] = str(value)

        if headers:
            request_headers.update(headers)

        # Print request information
        print("\n=== Async HTTP Request Information ===")
        print(f"URL: {url}")
        print(f"Timeout: {self.timeout} seconds")

        if params:
            print(f"Query Parameters: {params}")
        else:
            print("Query Parameters: None")

        if json_data:
            print(f"JSON Data: {json_data}")
        elif data:
            print(f"Form Data: {data}")
        else:
            print("Request Body: None")

        print("=" * 50)

        try:
            # Create aiohttp session and execute request
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            # Pass the merged headers to aiohttp session
            async with aiohttp.ClientSession(
                timeout=timeout, headers=request_headers
            ) as session:
                if method.upper() == "GET":
                    async with session.get(url, params=params) as response:
                        response_text = await response.text()
                        response_dict = {
                            "status_code": response.status,
                            "url": str(response.url),
                            "headers": dict(response.headers),
                            "text": response_text,
                            "success": response.status < 400,
                        }

                        # Try to parse JSON response
                        try:
                            response_dict["json"] = await response.json()
                        except:
                            response_dict["json"] = None

                        # Print response information (like sync version)
                        print("\n=== Async HTTP Response Information ===")
                        print(
                            f"Response Body: {response_dict.get('json', response_dict.get('text', 'No content'))}"
                        )
                        print("=" * 50)

                        return response_dict

                elif method.upper() == "POST":
                    if json_data:
                        async with session.post(
                            url, params=params, json=json_data
                        ) as response:
                            response_text = await response.text()
                            response_dict = {
                                "status_code": response.status,
                                "url": str(response.url),
                                "headers": dict(response.headers),
                                "text": response_text,
                                "success": response.status < 400,
                            }

                            # Try to parse JSON response
                            try:
                                response_dict["json"] = await response.json()
                            except:
                                response_dict["json"] = None

                            # Print response information (like sync version)
                            print("\n=== Async HTTP Response Information ===")
                            print(
                                f"Response Body: {response_dict.get('json', response_dict.get('text', 'No content'))}"
                            )
                            print("=" * 50)

                            return response_dict
                    else:
                        async with session.post(
                            url, params=params, data=data
                        ) as response:
                            response_text = await response.text()
                            response_dict = {
                                "status_code": response.status,
                                "url": str(response.url),
                                "headers": dict(response.headers),
                                "text": response_text,
                                "success": response.status < 400,
                            }

                            # Try to parse JSON response
                            try:
                                response_dict["json"] = await response.json()
                            except:
                                response_dict["json"] = None

                            # Print response information (like sync version)
                            print("\n=== Async HTTP Response Information ===")
                            print(
                                f"Response Body: {response_dict.get('json', response_dict.get('text', 'No content'))}"
                            )
                            print("=" * 50)

                            return response_dict
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

        except asyncio.TimeoutError:
            # Print error information
            print("\n=== Async HTTP Request Timeout ===")
            print(f"Request URL: {url}")
            print(f"Timeout: {self.timeout} seconds")
            print("=" * 50)

            return {
                "success": False,
                "error": "Request timeout",
                "status_code": None,
                "url": url,
            }

        except Exception as e:
            # Print error information
            print("\n=== Async HTTP Request Error ===")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print(f"Request URL: {url}")
            print("=" * 50)

            return {"success": False, "error": str(e), "status_code": None, "url": url}

    def close(self):
        """Close HTTP session"""
        if self.session:
            self.session.close()
