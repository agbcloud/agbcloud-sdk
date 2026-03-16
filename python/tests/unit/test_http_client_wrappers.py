from types import SimpleNamespace

import pytest

from agb.api.http_client import HTTPClient
from agb.api.models import (
    CallMcpToolRequest,
    ClearContextRequest,
    CreateSessionRequest,
    DeleteContextFileRequest,
    DeleteContextRequest,
    DeleteSessionAsyncRequest,
    DescribeContextFilesRequest,
    GetAndLoadInternalContextRequest,
    GetContextFileDownloadUrlRequest,
    GetContextFileUploadUrlRequest,
    GetContextInfoRequest,
    GetContextRequest,
    GetLabelRequest,
    GetLinkRequest,
    GetMcpResourceRequest,
    GetSessionDetailRequest,
    GetSessionRequest,
    InitBrowserRequest,
    ListContextsRequest,
    ListMcpToolsRequest,
    ListSessionRequest,
    ModifyContextRequest,
    ReleaseSessionRequest,
    SetLabelRequest,
    SyncContextRequest,
)


class _Cfg:
    endpoint = "example.com"
    timeout_ms = 5000


def _ok_http_response():
    # A generic response shape accepted by most *.from_http_response() model classes
    return {
        "status_code": 200,
        "url": "https://example.com/x",
        "headers": {},
        "success": True,
        "json": {"success": True, "requestId": "rid", "data": {}},
        "text": None,
        "request_id": "rid",
    }


def test_http_client_wrapper_methods_call_make_request(monkeypatch):
    c = HTTPClient(api_key="Bearer x", cfg=_Cfg())

    calls = []

    def _fake_make_request(method, endpoint, **kwargs):
        calls.append((method, endpoint, kwargs))
        return _ok_http_response()

    monkeypatch.setattr(c, "_make_request", _fake_make_request)

    # MCP session APIs
    c.create_session(CreateSessionRequest(authorization="Bearer x", image_id="img"))
    c.release_session(ReleaseSessionRequest(authorization="Bearer x", session_id="s1"))
    c.get_session(GetSessionRequest(authorization="Bearer x", session_id="s1"))
    c.get_session_detail(GetSessionDetailRequest(authorization="Bearer x", session_id="s1"))
    c.list_sessions(ListSessionRequest(authorization="Bearer x"))
    c.list_mcp_tools(ListMcpToolsRequest(authorization="Bearer x"))
    c.get_mcp_resource(GetMcpResourceRequest(authorization="Bearer x", session_id="s1"))
    c.call_mcp_tool(
        CallMcpToolRequest(
            authorization="Bearer x",
            session_id="s1",
            name="Filesystem.read_file",  # MCP tool name unchanged
            args={"path": "/tmp/a"},
        ),
        read_timeout=123,
        connect_timeout=456,
    )

    # Browser APIs
    c.init_browser(InitBrowserRequest(authorization="Bearer x", session_id="s1", persistent_path="/tmp"))
    c.get_link(GetLinkRequest(authorization="Bearer x", session_id="s1"))

    # Context APIs
    c.list_contexts(ListContextsRequest(authorization="Bearer x"))
    c.get_context(GetContextRequest(authorization="Bearer x", id="c1"))
    c.modify_context(ModifyContextRequest(authorization="Bearer x", id="c1", name="n1"))
    c.delete_context(DeleteContextRequest(authorization="Bearer x", id="c1"))
    c.clear_context(ClearContextRequest(authorization="Bearer x", id="c1"))
    c.sync_context(SyncContextRequest(authorization="Bearer x", session_id="s1", context_id="c1", path="/", mode="upload"))
    c.get_context_info(GetContextInfoRequest(authorization="Bearer x", session_id="s1", context_id="c1"))
    c.get_context_file_download_url(GetContextFileDownloadUrlRequest(authorization="Bearer x", context_id="c1", file_path="/a"))
    c.get_context_file_upload_url(GetContextFileUploadUrlRequest(authorization="Bearer x", context_id="c1", file_path="/a"))
    c.delete_context_file(DeleteContextFileRequest(authorization="Bearer x", context_id="c1", file_path="/a"))
    c.describe_context_files(DescribeContextFilesRequest(authorization="Bearer x", context_id="c1", parent_folder_path="/"))

    # Label APIs
    c.set_label(SetLabelRequest(authorization="Bearer x", session_id="s1", labels="k=v"))
    c.get_label(GetLabelRequest(authorization="Bearer x", session_id="s1"))

    # Internal context + async deletion
    c.get_and_load_internal_context(GetAndLoadInternalContextRequest(authorization="Bearer x", session_id="s1", context_types=["file_transfer"]))
    c.delete_session_async(DeleteSessionAsyncRequest(authorization="Bearer x", session_id="s1"))

    # Close
    c.close()

    # Smoke-check: we exercised a bunch of wrapper calls
    assert len(calls) >= 20

