from types import SimpleNamespace

import pytest

from agb import AGB


class _RespData:
    def __init__(self):
        self.app_instance_id = "app-1"
        self.resource_id = "r-1"
        self.session_id = "s-1"
        self.resource_url = "https://example.com"
        self.status = "running"


class _Resp:
    def __init__(self, ok: bool, *, request_id="rid", msg="bad", with_data=True):
        self.request_id = request_id
        self.status_code = 200
        self.code = "OK"
        self._ok = ok
        self._msg = msg
        self.data = _RespData() if with_data else None

    def is_successful(self):
        return self._ok

    def get_error_message(self):
        return self._msg

    def to_dict(self):
        return {"success": self._ok, "data": {"sessionId": "s-1"}}


def test_get_session_returns_error_on_api_failure(monkeypatch):
    agb = AGB(api_key="test-key")
    agb.client = SimpleNamespace(get_mcp_session=lambda request: _Resp(False, msg="expired"))

    out = agb.get_session("s-1")
    assert out.success is False
    assert "expired" in (out.error_message or "")


def test_get_session_success_populates_data(monkeypatch):
    agb = AGB(api_key="test-key")
    agb.client = SimpleNamespace(get_mcp_session=lambda request: _Resp(True))

    out = agb.get_session("s-1")
    assert out.success is True
    assert out.data is not None
    assert out.data.session_id == "s-1"
    assert out.data.resource_url == "https://example.com"


def test_get_success_creates_session_object(monkeypatch):
    agb = AGB(api_key="test-key")

    # Stub get_session() to hit the success path in AGB.get()
    def _fake_get_session(session_id):
        data = SimpleNamespace(
            app_instance_id="app-1",
            resource_id="r-1",
            session_id=session_id,
            resource_url="https://example.com",
            status="running",
        )
        return SimpleNamespace(success=True, request_id="rid", data=data, error_message="")

    monkeypatch.setattr(agb, "get_session", _fake_get_session)

    res = agb.get("s-1")
    assert res.success is True
    assert res.session is not None
    assert res.session.session_id == "s-1"
    assert res.session.resource_url == "https://example.com"


def test_get_returns_error_when_get_session_fails(monkeypatch):
    agb = AGB(api_key="test-key")
    monkeypatch.setattr(
        agb,
        "get_session",
        lambda session_id: SimpleNamespace(
            success=False, request_id="rid", data=None, error_message="nope"
        ),
    )

    res = agb.get("s-1")
    assert res.success is False
    assert "Failed to get session s-1" in (res.error_message or "")

