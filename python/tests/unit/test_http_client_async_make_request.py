import pytest

from agb.api.http_client import HTTPClient


class _Cfg:
    endpoint = "example.com"
    timeout_ms = 5000


class _FakeAiohttpResponse:
    def __init__(self, status=200, json_obj=None, text="ok", headers=None, url="https://example.com/x"):
        self.status = status
        self._json_obj = json_obj
        self._text = text
        self.headers = headers or {}
        self.url = url

    async def text(self):
        return self._text

    async def json(self):
        if isinstance(self._json_obj, Exception):
            raise self._json_obj
        return self._json_obj

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeAiohttpSession:
    def __init__(self, responses):
        self._responses = responses
        self.calls = []

    def get(self, url, params=None):
        self.calls.append(("GET", url, params, None, None))
        return self._responses["GET"]

    def post(self, url, params=None, json=None, data=None):
        self.calls.append(("POST", url, params, json, data))
        # decide based on whether json was passed
        if json is not None:
            return self._responses["POST_JSON"]
        return self._responses["POST_FORM"]

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_make_request_async_get_and_post(monkeypatch):
    c = HTTPClient(api_key="Bearer x", cfg=_Cfg())

    responses = {
        "GET": _FakeAiohttpResponse(status=200, json_obj={"requestId": "rid"}, headers={"x-request-id": "hdr"}),
        "POST_JSON": _FakeAiohttpResponse(status=200, json_obj={"requestId": "rid2"}),
        "POST_FORM": _FakeAiohttpResponse(status=200, json_obj={"requestId": "rid3"}),
    }
    fake_session = _FakeAiohttpSession(responses)

    # Patch aiohttp.ClientSession and ClientTimeout inside module
    import agb.api.http_client as http_client_mod

    monkeypatch.setattr(http_client_mod.aiohttp, "ClientTimeout", lambda total=None: object())
    monkeypatch.setattr(http_client_mod.aiohttp, "ClientSession", lambda **kwargs: fake_session)

    # GET
    res = await c._make_request_async("GET", "/mcp/getSession", params={"a": "b"})
    assert res["success"] is True
    assert res["request_id"] == "rid"

    # POST JSON
    res = await c._make_request_async("POST", "/mcp/createSession", json_data={"x": 1})
    assert res["success"] is True
    assert res["request_id"] == "rid2"

    # POST form
    res = await c._make_request_async("POST", "/mcp/createSession", data={"k": "v"})
    assert res["success"] is True
    assert res["request_id"] == "rid3"


@pytest.mark.asyncio
async def test_make_request_async_handles_exception(monkeypatch):
    c = HTTPClient(api_key="Bearer x", cfg=_Cfg())

    import agb.api.http_client as http_client_mod

    class _BoomSession:
        def get(self, url, params=None):
            raise RuntimeError("boom")

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(http_client_mod.aiohttp, "ClientTimeout", lambda total=None: object())
    monkeypatch.setattr(http_client_mod.aiohttp, "ClientSession", lambda **kwargs: _BoomSession())

    res = await c._make_request_async("GET", "/mcp/getSession")
    assert res["success"] is False
    assert "boom" in res["error"]

