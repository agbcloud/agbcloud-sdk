# -*- coding: utf-8 -*-
"""
AGB API client implementation using HTTP client
"""

from typing import Any, Dict, List, Optional, Union

import aiohttp

from agb.api.models import (
    CallMcpToolRequest,
    CallMcpToolResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    GetLinkRequest,
    GetLinkResponse,
    GetMcpResourceRequest,
    GetMcpResourceResponse,
    InitBrowserRequest,
    InitBrowserResponse,
    ListMcpToolsRequest,
    ListMcpToolsResponse,
    ReleaseSessionRequest,
    ReleaseSessionResponse,
)

from .http_client import HTTPClient


class Client:
    """
    AGB API client that uses HTTP client
    """

    def __init__(self, config=None):
        """
        Initialize the client

        Args:
            config: Configuration object for HTTP client
        """
        self.config = config
        self._http_client = None

    def _get_http_client(self, api_key: str) -> HTTPClient:
        """
        Get HTTP client instance, creating a new one for each request

        Args:
            api_key: API key for authentication

        Returns:
            HTTPClient: HTTP client instance
        """
        # Always create a new HTTP client for each request
        return HTTPClient(api_key=api_key, cfg=self.config)

    def create_mcp_session(
        self, request: CreateSessionRequest
    ) -> CreateSessionResponse:
        """
        Create MCP session using HTTP client
        """
        # Extract API key from authorization header
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.create_session(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def release_mcp_session(
        self, request: ReleaseSessionRequest
    ) -> ReleaseSessionResponse:
        """
        Release MCP session using HTTP client
        """
        if not request.session_id:
            raise ValueError("session_id is required")

        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.release_session(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def call_mcp_tool(
        self,
        request: CallMcpToolRequest,
        read_timeout: Optional[int] = None,
        connect_timeout: Optional[int] = None,
    ) -> CallMcpToolResponse:
        """
        Call MCP tool using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.call_mcp_tool(
                request, read_timeout=read_timeout, connect_timeout=connect_timeout
            )
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def list_mcp_tools(self, request: ListMcpToolsRequest) -> ListMcpToolsResponse:
        """
        List MCP tools using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.list_mcp_tools(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def get_mcp_resource(
        self, request: GetMcpResourceRequest
    ) -> GetMcpResourceResponse:
        """
        Get MCP resource using HTTP client
        """
        if not request.session_id:
            raise ValueError("session_id is required")

        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.get_mcp_resource(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def init_browser(self, request: InitBrowserRequest) -> InitBrowserResponse:
        """
        Initialize browser using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.init_browser(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    async def init_browser_async(
        self,
        request: InitBrowserRequest,
    ) -> InitBrowserResponse:
        """
        Async version of init_browser using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make async request
        http_client = self._get_http_client(request.authorization)

        try:
            response = await http_client.init_browser_async(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def close(self):
        """Close HTTP client and clean up resources"""
        # No need to manage long-lived HTTP client anymore
        # Each request creates a new client that gets cleaned up automatically
        pass

    async def call_api_async_with_requests(
        url, method="GET", headers=None, params=None, data=None, json=None, timeout=30
    ):
        """
        Implement async HTTP requests using aiohttp, mimicking requests usage.
        """
        async with aiohttp.ClientSession() as session:
            req_method = getattr(session, method.lower())
            async with req_method(
                url,
                headers=headers,
                params=params,
                data=data,
                json=json,
                timeout=timeout,
            ) as resp:
                resp_data = await resp.text()
                # You can return resp.json() or resp.read() as needed
                return {
                    "status_code": resp.status,
                    "headers": dict(resp.headers),
                    "body": resp_data,
                }

    def get_link(
        self,
        request: GetLinkRequest,
    ) -> GetLinkResponse:
        """
        Get session link using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        if not request.session_id:
            raise ValueError("session_id is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.get_link(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    async def get_link_async(
        self,
        request: GetLinkRequest,
    ) -> GetLinkResponse:
        """
        Async version of get_link using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        if not request.session_id:
            raise ValueError("session_id is required")

        # Get HTTP client and make async request
        http_client = self._get_http_client(request.authorization)

        try:
            response = await http_client.get_link_async(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()
