import types

import pytest

from agb.api.client import Client
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


class _FakeHTTPClient:
    def __init__(self):
        self.calls = []
        self.close_calls = 0

    def close(self):
        self.close_calls += 1

    def _ret(self, name, *args, **kwargs):
        self.calls.append((name, args, kwargs))
        return f"resp:{name}"

    async def _aret(self, name, *args, **kwargs):
        self.calls.append((name, args, kwargs))
        return f"resp:{name}"

    # Sync methods used by Client wrappers
    def create_session(self, request):  # pragma: no cover (covered via wrapper)
        return self._ret("create_session", request)

    def release_session(self, request):
        return self._ret("release_session", request)

    def get_session(self, request):
        return self._ret("get_session", request)

    def get_session_detail(self, request):
        return self._ret("get_session_detail", request)

    def list_sessions(self, request):
        return self._ret("list_sessions", request)

    def call_mcp_tool(self, request, read_timeout=None, connect_timeout=None):
        return self._ret(
            "call_mcp_tool",
            request,
            read_timeout=read_timeout,
            connect_timeout=connect_timeout,
        )

    def list_mcp_tools(self, request):
        return self._ret("list_mcp_tools", request)

    def get_mcp_resource(self, request):
        return self._ret("get_mcp_resource", request)

    def init_browser(self, request):
        return self._ret("init_browser", request)

    async def init_browser_async(self, request):
        return await self._aret("init_browser_async", request)

    def get_link(self, request):
        return self._ret("get_link", request)

    async def get_link_async(self, request):
        return await self._aret("get_link_async", request)

    def list_contexts(self, request):
        return self._ret("list_contexts", request)

    def get_context(self, request):
        return self._ret("get_context", request)

    def modify_context(self, request):
        return self._ret("modify_context", request)

    def delete_context(self, request):
        return self._ret("delete_context", request)

    def clear_context(self, request):
        return self._ret("clear_context", request)

    def sync_context(self, request):
        return self._ret("sync_context", request)

    def get_context_info(self, request):
        return self._ret("get_context_info", request)

    def get_context_file_download_url(self, request):
        return self._ret("get_context_file_download_url", request)

    def get_context_file_upload_url(self, request):
        return self._ret("get_context_file_upload_url", request)

    def delete_context_file(self, request):
        return self._ret("delete_context_file", request)

    def describe_context_files(self, request):
        return self._ret("describe_context_files", request)

    def set_label(self, request):
        return self._ret("set_label", request)

    def get_label(self, request):
        return self._ret("get_label", request)

    def get_and_load_internal_context(self, request):
        return self._ret("get_and_load_internal_context", request)

    def delete_session_async(self, request):
        return self._ret("delete_session_async", request)


@pytest.fixture
def fake_http_client():
    return _FakeHTTPClient()


@pytest.fixture
def client(fake_http_client, monkeypatch):
    c = Client(config=None)
    monkeypatch.setattr(c, "_get_http_client", lambda api_key: fake_http_client)
    return c


def test_client_requires_authorization_create_session(client):
    with pytest.raises(ValueError, match="authorization is required"):
        client.create_mcp_session(CreateSessionRequest(authorization=""))


def test_client_requires_session_id_for_some_apis(client):
    with pytest.raises(ValueError, match="session_id is required"):
        client.get_mcp_resource(GetMcpResourceRequest(authorization="Bearer x", session_id=""))
    with pytest.raises(ValueError, match="session_id is required"):
        client.get_link(GetLinkRequest(authorization="Bearer x", session_id=""))


@pytest.mark.parametrize(
    "method_name, request_obj, expected_call",
    [
        ("create_mcp_session", CreateSessionRequest(authorization="Bearer x", image_id="img"), "create_session"),
        ("release_mcp_session", ReleaseSessionRequest(authorization="Bearer x", session_id="s1"), "release_session"),
        ("get_mcp_session", GetSessionRequest(authorization="Bearer x", session_id="s1"), "get_session"),
        ("get_session_detail", GetSessionDetailRequest(authorization="Bearer x", session_id="s1"), "get_session_detail"),
        ("list_sessions", ListSessionRequest(authorization="Bearer x"), "list_sessions"),
        ("list_mcp_tools", ListMcpToolsRequest(authorization="Bearer x"), "list_mcp_tools"),
        ("get_mcp_resource", GetMcpResourceRequest(authorization="Bearer x", session_id="s1"), "get_mcp_resource"),
        ("init_browser", InitBrowserRequest(authorization="Bearer x", session_id="s1", persistent_path="/tmp"), "init_browser"),
        ("get_link", GetLinkRequest(authorization="Bearer x", session_id="s1"), "get_link"),
        ("list_contexts", ListContextsRequest(authorization="Bearer x"), "list_contexts"),
        ("get_context", GetContextRequest(authorization="Bearer x", id="c1"), "get_context"),
        ("modify_context", ModifyContextRequest(authorization="Bearer x", id="c1", name="n1"), "modify_context"),
        ("delete_context", DeleteContextRequest(authorization="Bearer x", id="c1"), "delete_context"),
        ("clear_context", ClearContextRequest(authorization="Bearer x", id="c1"), "clear_context"),
        ("sync_context", SyncContextRequest(authorization="Bearer x", session_id="s1", context_id="c1", path="/", mode="upload"), "sync_context"),
        ("get_context_info", GetContextInfoRequest(authorization="Bearer x", session_id="s1", context_id="c1"), "get_context_info"),
        ("get_context_file_download_url", GetContextFileDownloadUrlRequest(authorization="Bearer x", context_id="c1", file_path="/a"), "get_context_file_download_url"),
        ("get_context_file_upload_url", GetContextFileUploadUrlRequest(authorization="Bearer x", context_id="c1", file_path="/a"), "get_context_file_upload_url"),
        ("delete_context_file", DeleteContextFileRequest(authorization="Bearer x", context_id="c1", file_path="/a"), "delete_context_file"),
        ("describe_context_files", DescribeContextFilesRequest(authorization="Bearer x", context_id="c1", parent_folder_path="/"), "describe_context_files"),
        ("set_label", SetLabelRequest(authorization="Bearer x", session_id="s1", labels="k=v"), "set_label"),
        ("get_label", GetLabelRequest(authorization="Bearer x", session_id="s1"), "get_label"),
        ("get_and_load_internal_context", GetAndLoadInternalContextRequest(authorization="Bearer x", session_id="s1", context_types=["file_transfer"]), "get_and_load_internal_context"),
        ("delete_session_async", DeleteSessionAsyncRequest(authorization="Bearer x", session_id="s1"), "delete_session_async"),
    ],
)
def test_client_calls_http_client_and_always_closes(client, fake_http_client, method_name, request_obj, expected_call):
    before_close = fake_http_client.close_calls
    resp = getattr(client, method_name)(request_obj)
    assert resp == f"resp:{expected_call}"
    assert fake_http_client.calls[-1][0] == expected_call
    assert fake_http_client.close_calls == before_close + 1


def test_client_call_mcp_tool_passes_timeouts(client, fake_http_client):
    req = CallMcpToolRequest(
        authorization="Bearer x",
        session_id="s1",
        name="Filesystem.read_file",  # MCP tool name unchanged
        args={"path": "/tmp/a"},
    )
    resp = client.call_mcp_tool(req, read_timeout=1234, connect_timeout=567)
    assert resp == "resp:call_mcp_tool"
    name, _args, kwargs = fake_http_client.calls[-1]
    assert name == "call_mcp_tool"
    assert kwargs["read_timeout"] == 1234
    assert kwargs["connect_timeout"] == 567


@pytest.mark.asyncio
async def test_client_async_wrappers_close(client, fake_http_client):
    before = fake_http_client.close_calls
    resp = await client.init_browser_async(
        InitBrowserRequest(authorization="Bearer x", session_id="s1", persistent_path="/tmp")
    )
    assert resp == "resp:init_browser_async"
    assert fake_http_client.close_calls == before + 1

    before = fake_http_client.close_calls
    resp = await client.get_link_async(GetLinkRequest(authorization="Bearer x", session_id="s1"))
    assert resp == "resp:get_link_async"
    assert fake_http_client.close_calls == before + 1


@pytest.mark.asyncio
async def test_call_api_async_with_requests_builds_response(monkeypatch):
    # Avoid real aiohttp usage by stubbing ClientSession
    from agb.api import client as client_mod

    class _Resp:
        status = 200
        headers = {"x": "y"}

        async def text(self):
            return "ok"

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class _Sess:
        def get(self, *args, **kwargs):
            return _Resp()

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(client_mod.aiohttp, "ClientSession", lambda: _Sess())
    out = await Client.call_api_async_with_requests("https://example.com", method="GET")
    assert out["status_code"] == 200
    assert out["headers"]["x"] == "y"
    assert out["body"] == "ok"

