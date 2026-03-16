from __future__ import annotations

from typing import Any

import pytest

from agb.agb import AGB
from agb.model.response import SessionStatusResult
from agb.session import Session


class _FakeGetSessionDetailResponse:
    def __init__(
        self,
        *,
        request_id: str,
        http_status_code: int,
        code: str,
        success: bool,
        status: str,
        error_message: str,
    ):
        self.request_id = request_id
        self.http_status_code = http_status_code
        self.code = code
        self._success = success
        self._status = status
        self._error_message = error_message

    def is_successful(self) -> bool:
        return self._success

    def get_error_message(self) -> str:
        return self._error_message

    def get_status(self) -> str:
        return self._status


def test_session_get_status_success(monkeypatch: pytest.MonkeyPatch) -> None:
    agb = AGB(api_key="dummy")
    session = Session(agb, "sid-1")

    def _fake_get_session_detail(_request: Any) -> Any:
        return _FakeGetSessionDetailResponse(
            request_id="rid",
            http_status_code=200,
            code="",
            success=True,
            status="RUNNING",
            error_message="",
        )

    monkeypatch.setattr(session.agb.client, "get_session_detail", _fake_get_session_detail)

    result = session.get_status()
    assert isinstance(result, SessionStatusResult)
    assert result.success is True
    assert result.status == "RUNNING"
    assert result.request_id == "rid"
    assert result.http_status_code == 200


def test_session_get_status_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    agb = AGB(api_key="dummy")
    session = Session(agb, "sid-2")

    def _fake_get_session_detail(_request: Any) -> Any:
        return _FakeGetSessionDetailResponse(
            request_id="rid2",
            http_status_code=403,
            code="AccessDenied",
            success=False,
            status="",
            error_message="access denied",
        )

    monkeypatch.setattr(session.agb.client, "get_session_detail", _fake_get_session_detail)

    result = session.get_status()
    assert result.success is False
    assert result.code == "AccessDenied"
    assert result.http_status_code == 403
    assert "access denied" in result.error_message


