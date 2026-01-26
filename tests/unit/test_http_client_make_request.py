import types

import pytest
import requests

from agb.api.http_client import HTTPClient


class _Cfg:
    endpoint = "example.com"
    timeout_ms = 5000


class _FakeResponse:
    def __init__(self, status_code=200, json_obj=None, text="txt", headers=None, url="https://example.com/x"):
        self.status_code = status_code
        self._json_obj = json_obj
        self.text = text
        self.headers = headers or {}
        self.url = url

    def json(self):
        if isinstance(self._json_obj, Exception):
            raise self._json_obj
        return self._json_obj


class _FakeSession:
    def __init__(self):
        self.headers = {"authorization": "Bearer x", "Content-Type": "application/json"}
        self.calls = []
        self.next_response = _FakeResponse(status_code=200, json_obj={"requestId": "rid"})

    def get(self, url, headers=None, params=None, timeout=None):
        self.calls.append(("GET", url, headers, params, None, None, timeout))
        return self.next_response

    def post(self, url, headers=None, params=None, json=None, data=None, timeout=None):
        self.calls.append(("POST", url, headers, params, json, data, timeout))
        return self.next_response

    def put(self, url, headers=None, params=None, json=None, timeout=None):
        self.calls.append(("PUT", url, headers, params, json, None, timeout))
        return self.next_response

    def delete(self, url, headers=None, params=None, timeout=None):
        self.calls.append(("DELETE", url, headers, params, None, None, timeout))
        return self.next_response


def _new_client():
    c = HTTPClient(api_key="Bearer x", cfg=_Cfg())
    c.session = _FakeSession()
    return c


def test_http_client_requires_config_when_no_default():
    with pytest.raises(ValueError, match="No configuration provided"):
        HTTPClient(api_key="x", cfg=None)


def test_make_request_get_parses_json_and_request_id():
    c = _new_client()
    res = c._make_request("GET", "/mcp/getSession", params={"a": "b"})
    assert res["success"] is True
    assert res["status_code"] == 200
    assert res["request_id"] == "rid"
    method, url, _headers, params, *_ = c.session.calls[-1]
    assert method == "GET"
    assert url == "https://example.com/mcp/getSession"
    assert params == {"a": "b"}


def test_make_request_timeout_tuple_when_separate_timeouts():
    c = _new_client()
    c._make_request(
        "GET",
        "/mcp/getSession",
        read_timeout=1234,
        connect_timeout=567,
    )
    *_prefix, timeout = c.session.calls[-1]
    assert timeout == (0.567, 1.234)


def test_make_request_post_uses_json_when_json_data_present():
    c = _new_client()
    c._make_request("POST", "/mcp/createSession", json_data={"x": 1})
    method, _url, _headers, _params, json_payload, data, _timeout = c.session.calls[-1]
    assert method == "POST"
    assert json_payload == {"x": 1}
    assert data is None


def test_make_request_post_uses_form_when_json_data_missing():
    c = _new_client()
    c._make_request("POST", "/mcp/createSession", data={"k": "v"})
    method, _url, _headers, _params, json_payload, data, _timeout = c.session.calls[-1]
    assert method == "POST"
    # implementation sends json={} when using form data
    assert json_payload == {}
    assert data == {"k": "v"}


def test_make_request_handles_non_json_response():
    c = _new_client()
    c.session.next_response = _FakeResponse(status_code=200, json_obj=ValueError("no json"), text="plain")
    res = c._make_request("GET", "/mcp/getSession")
    assert res["json"] is None
    assert res["text"] == "plain"
    assert "request_id" in res  # from header (may be empty)


def test_make_request_unsupported_method_raises():
    c = _new_client()
    with pytest.raises(ValueError, match="Unsupported HTTP method"):
        c._make_request("PATCH", "/x")


def test_make_request_handles_request_exception(monkeypatch):
    c = _new_client()

    def boom(*args, **kwargs):
        raise requests.exceptions.RequestException("down")

    c.session.get = boom  # type: ignore[method-assign]
    res = c._make_request("GET", "/mcp/getSession")
    assert res["success"] is False
    assert res["status_code"] is None
    assert "down" in res["error"]

