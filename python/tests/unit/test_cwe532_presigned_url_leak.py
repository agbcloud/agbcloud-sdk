"""
PoC test for CWE-532: Pre-signed URLs logged in plaintext (file_transfer.py).

Pre-signed upload/download URLs contain authentication tokens in query-string
parameters (e.g. Signature, OSSAccessKeyId, Expires).  These are bearer tokens:
anyone who reads log output can use them.

The test captures log output emitted by FileTransfer.upload() and
FileTransfer.download() and asserts it does NOT contain the query parameters.
"""
from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from loguru import logger

from agb.modules.file_transfer import FileTransfer

# ---------------------------------------------------------------------------
# Fakes (same pattern as existing unit tests)
# ---------------------------------------------------------------------------

PRESIGNED_UPLOAD_URL = (
    "https://bucket.oss-cn-hangzhou.aliyuncs.com/path/file.txt"
    "?OSSAccessKeyId=AKID1234567890"
    "&Expires=1719999999"
    "&Signature=dGhpcyBpcyBhIHNlY3JldA%3D%3D"
)

PRESIGNED_DOWNLOAD_URL = (
    "https://bucket.oss-cn-hangzhou.aliyuncs.com/path/remote.txt"
    "?OSSAccessKeyId=AKID0987654321"
    "&Expires=1720000000"
    "&Signature=c2Vuc2l0aXZlc2lnbmF0dXJl"
)


class _FakeInternalContextResponse:
    def __init__(self, ok=True, data=None, err=None):
        self._ok = ok
        self._data = data
        self._err = err

    def is_successful(self):
        return self._ok

    def get_error_message(self):
        return self._err

    def get_context_list(self):
        return self._data


class _FakeSession:
    def __init__(self, sid="s1"):
        self._sid = sid
        self.context = SimpleNamespace()

    def get_session_id(self):
        return self._sid


class _FakeClient:
    def __init__(self, resp):
        self._resp = resp

    def get_and_load_internal_context(self, request):
        return self._resp


class _FakeContextSvc:
    def __init__(self, upload_url=None, download_url=None):
        self._up = upload_url
        self._dl = download_url

    def get_file_upload_url(self, cid, path):
        return self._up

    def get_file_download_url(self, cid, path):
        return self._dl


class _FakeAGB:
    def __init__(self, api_key="ak", client=None, context=None):
        self.api_key = api_key
        self.client = client
        self.context = context


# ---------------------------------------------------------------------------
# Helper: capture loguru output as a list of strings
# ---------------------------------------------------------------------------

class _LogCapture:
    """Sink for loguru that stores messages."""

    def __init__(self):
        self.messages: list[str] = []

    def write(self, message):
        self.messages.append(str(message))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_upload_does_not_log_presigned_url_query_params(tmp_path):
    """upload() must not emit pre-signed URL query parameters to logs."""
    # Prepare local file
    local = tmp_path / "data.bin"
    local.write_bytes(b"hello")

    resp = _FakeInternalContextResponse(
        ok=True, data=[{"contextId": "cid", "contextPath": "/tmp"}]
    )
    url_res = SimpleNamespace(
        success=True,
        url=PRESIGNED_UPLOAD_URL,
        request_id="rid-up",
        message=None,
    )
    agb = _FakeAGB(
        client=_FakeClient(resp),
        context=_FakeContextSvc(upload_url=url_res),
    )
    ft = FileTransfer(agb, _FakeSession("s-1"))

    # Capture logs
    capture = _LogCapture()
    handler_id = logger.add(capture, format="{message}", level="DEBUG")

    try:
        with patch.object(ft, "_put_file_sync", return_value=(200, "etag", 5)):
            with patch.object(ft, "_await_sync", return_value="rid-sync"):
                ft.upload(str(local), "/path/file.txt", wait=False)
    finally:
        logger.remove(handler_id)

    all_logs = "\n".join(capture.messages)

    # The URL path is fine to log, but query params with secrets must NOT appear
    assert "OSSAccessKeyId" not in all_logs, (
        f"Pre-signed URL query parameter leaked in logs:\n{all_logs}"
    )
    assert "Signature" not in all_logs, (
        f"Pre-signed URL signature leaked in logs:\n{all_logs}"
    )
    assert "Expires" not in all_logs, (
        f"Pre-signed URL expiry leaked in logs:\n{all_logs}"
    )


def test_download_does_not_log_presigned_url_query_params(tmp_path):
    """download() must not emit pre-signed URL query parameters to logs."""
    resp = _FakeInternalContextResponse(
        ok=True, data=[{"contextId": "cid", "contextPath": "/tmp"}]
    )
    dl_url_res = SimpleNamespace(
        success=True,
        url=PRESIGNED_DOWNLOAD_URL,
        request_id="rid-dl",
        message=None,
    )
    agb = _FakeAGB(
        client=_FakeClient(resp),
        context=_FakeContextSvc(download_url=dl_url_res),
    )
    ft = FileTransfer(agb, _FakeSession("s-2"))

    capture = _LogCapture()
    handler_id = logger.add(capture, format="{message}", level="DEBUG")

    def _fake_get(url, dest, *a, **k):
        with open(dest, "wb") as f:
            f.write(b"data")
        return 200, 4

    try:
        with patch.object(ft, "_await_sync", return_value="rid-sync"):
            with patch.object(ft, "_get_file_sync", side_effect=_fake_get):
                ft.download("/path/remote.txt", str(tmp_path / "out.bin"), wait=False)
    finally:
        logger.remove(handler_id)

    all_logs = "\n".join(capture.messages)

    assert "OSSAccessKeyId" not in all_logs, (
        f"Pre-signed URL query parameter leaked in logs:\n{all_logs}"
    )
    assert "Signature" not in all_logs, (
        f"Pre-signed URL signature leaked in logs:\n{all_logs}"
    )
    assert "Expires" not in all_logs, (
        f"Pre-signed URL expiry leaked in logs:\n{all_logs}"
    )
