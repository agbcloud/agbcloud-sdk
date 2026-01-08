# -*- coding: utf-8 -*-
"""
AGB API client implementation using HTTP client
"""

from typing import Any, Dict, List, Optional, Union

import aiohttp

from .models import (
    CallMcpToolRequest,
    CallMcpToolResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    GetLinkRequest,
    GetLinkResponse,
    GetMcpResourceRequest,
    GetMcpResourceResponse,
    GetSessionRequest,
    GetSessionResponse,
    GetSessionDetailRequest,
    GetSessionDetailResponse,
    InitBrowserRequest,
    InitBrowserResponse,
    ListMcpToolsRequest,
    ListMcpToolsResponse,
    ListSessionRequest,
    ListSessionResponse,
    ReleaseSessionRequest,
    ReleaseSessionResponse,
    SetLabelRequest,
    SetLabelResponse,
    GetLabelRequest,
    GetLabelResponse,
    # Delete session async imports
    DeleteSessionAsyncRequest,
    DeleteSessionAsyncResponse,
    # Context related imports
    ListContextsRequest,
    ListContextsResponse,
    GetContextRequest,
    GetContextResponse,
    ModifyContextRequest,
    ModifyContextResponse,
    DeleteContextRequest,
    DeleteContextResponse,
    ClearContextRequest,
    ClearContextResponse,
    SyncContextRequest,
    SyncContextResponse,
    GetContextInfoRequest,
    GetContextInfoResponse,
    GetContextFileDownloadUrlRequest,
    GetContextFileDownloadUrlResponse,
    GetContextFileUploadUrlRequest,
    GetContextFileUploadUrlResponse,
    DeleteContextFileRequest,
    DeleteContextFileResponse,
    DescribeContextFilesRequest,
    DescribeContextFilesResponse,
    GetAndLoadInternalContextRequest,
    GetAndLoadInternalContextResponse,
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

    def get_mcp_session(self, request: GetSessionRequest) -> GetSessionResponse:
        """
        Get MCP session information using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.get_session(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def get_session_detail(
        self, request: GetSessionDetailRequest
    ) -> GetSessionDetailResponse:
        """
        Get session detail (status only) using HTTP client.
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        http_client = self._get_http_client(request.authorization)
        try:
            response = http_client.get_session_detail(request)
            return response
        finally:
            http_client.close()

    def list_sessions(self, request: ListSessionRequest) -> ListSessionResponse:
        """
        List sessions using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.list_sessions(request)
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

    # Context related methods
    def list_contexts(self, request: ListContextsRequest) -> ListContextsResponse:
        """
        List contexts using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.list_contexts(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def get_context(self, request: GetContextRequest) -> GetContextResponse:
        """
        Get context using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.get_context(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def modify_context(self, request: ModifyContextRequest) -> ModifyContextResponse:
        """
        Modify context using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.modify_context(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def delete_context(self, request: DeleteContextRequest) -> DeleteContextResponse:
        """
        Delete context using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.delete_context(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def clear_context(self, request: ClearContextRequest) -> ClearContextResponse:
        """
        Clear context using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.clear_context(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def sync_context(self, request: SyncContextRequest) -> SyncContextResponse:
        """
        Sync context using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.sync_context(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def get_context_info(
        self, request: GetContextInfoRequest
    ) -> GetContextInfoResponse:
        """
        Get context info using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.get_context_info(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def get_context_file_download_url(
        self, request: GetContextFileDownloadUrlRequest
    ) -> GetContextFileDownloadUrlResponse:
        """
        Get context file download URL using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.get_context_file_download_url(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def get_context_file_upload_url(
        self, request: GetContextFileUploadUrlRequest
    ) -> GetContextFileUploadUrlResponse:
        """
        Get context file upload URL using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.get_context_file_upload_url(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def delete_context_file(
        self, request: DeleteContextFileRequest
    ) -> DeleteContextFileResponse:
        """
        Delete context file using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.delete_context_file(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def describe_context_files(
        self, request: DescribeContextFilesRequest
    ) -> DescribeContextFilesResponse:
        """
        Describe context files using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.describe_context_files(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def set_label(self, request: SetLabelRequest) -> SetLabelResponse:
        """
        Set label using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.set_label(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def get_label(self, request: GetLabelRequest) -> GetLabelResponse:
        """
        Get label using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.get_label(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def get_and_load_internal_context(
        self, request: GetAndLoadInternalContextRequest
    ) -> GetAndLoadInternalContextResponse:
        """
        Get and load internal context using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.get_and_load_internal_context(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()

    def delete_session_async(
        self, request: "DeleteSessionAsyncRequest"
    ) -> "DeleteSessionAsyncResponse":
        """
        Delete session asynchronously using HTTP client
        """
        if not request.authorization:
            raise ValueError("authorization is required")

        if not request.session_id:
            raise ValueError("session_id is required")

        # Get HTTP client and make request directly with the input request
        http_client = self._get_http_client(request.authorization)

        try:
            response = http_client.delete_session_async(request)
            return response
        finally:
            # Always close the HTTP client to release resources
            http_client.close()
