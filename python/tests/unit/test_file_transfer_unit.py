from __future__ import annotations

from types import SimpleNamespace

import pytest

from agb.modules.file_transfer import FileTransfer


class _FakeInternalContextResponse:
    def __init__(self, ok: bool, data=None, err: str | None = None):
        self._ok = ok
        self._data = data
        self._err = err

    def is_successful(self) -> bool:
        return self._ok

    def get_error_message(self):
        return self._err

    def get_context_list(self):
        return self._data


class _FakeSession:
    def __init__(self, sid="s1"):
        self._sid = sid
        self.command = SimpleNamespace(
            execute=lambda *a, **k: SimpleNamespace(success=True)
        )
        self.context = SimpleNamespace()

    def get_session_id(self):
        return self._sid


class _FakeClient:
    def __init__(self, resp):
        self._resp = resp

    def get_and_load_internal_context(self, request):
        return self._resp


class _FakeContextSvc:
    def __init__(self, upload_url_result=None):
        self._upload_url_result = upload_url_result

    def get_file_upload_url(self, context_id, file_path):
        return self._upload_url_result


class _FakeAGB:
    def __init__(self, api_key="ak", client=None, context=None):
        self.api_key = api_key
        self.client = client
        self.context = context


def test_ensure_context_id_success_sets_context_fields():
    resp = _FakeInternalContextResponse(
        ok=True,
        data=[{"contextId": "cid", "contextPath": "/tmp"}],
    )
    agb = _FakeAGB(client=_FakeClient(resp), context=_FakeContextSvc())
    ft = FileTransfer(agb, _FakeSession("s-123"))

    ok, msg = ft.ensure_context_id()
    assert ok is True
    assert msg == ""
    assert ft.context_id == "cid"
    assert ft.context_path == "/tmp"


def test_ensure_context_id_api_error_returns_false():
    resp = _FakeInternalContextResponse(ok=False, data=None, err="expired")
    agb = _FakeAGB(client=_FakeClient(resp), context=_FakeContextSvc())
    ft = FileTransfer(agb, _FakeSession("s-123"))

    ok, msg = ft.ensure_context_id()
    assert ok is False
    assert "expired" in (msg or "")


def test_upload_returns_error_when_local_file_missing(tmp_path):
    resp = _FakeInternalContextResponse(ok=True, data=[{"contextId": "cid", "contextPath": "/tmp"}])
    agb = _FakeAGB(client=_FakeClient(resp), context=_FakeContextSvc())
    ft = FileTransfer(agb, _FakeSession("s-123"))

    out = ft.upload(str(tmp_path / "missing.txt"), "/tmp/remote.txt")
    assert out.success is False
    assert "Local file not found" in (out.error_message or "")


def test_upload_fails_when_ensure_context_id_fails(tmp_path, monkeypatch):
    # create real local file
    p = tmp_path / "a.txt"
    p.write_text("hi", encoding="utf-8")
    agb = _FakeAGB(client=None, context=_FakeContextSvc())
    ft = FileTransfer(agb, _FakeSession("s-123"))

    monkeypatch.setattr(ft, "ensure_context_id", lambda: (False, "noctx"))
    out = ft.upload(str(p), "/tmp/remote.txt")
    assert out.success is False
    assert "noctx" in (out.error_message or "")


def test_upload_fails_when_get_upload_url_fails(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("hi", encoding="utf-8")
    resp = _FakeInternalContextResponse(ok=True, data=[{"contextId": "cid", "contextPath": "/tmp"}])
    url_res = SimpleNamespace(success=False, url=None, request_id="rid", message="bad")
    agb = _FakeAGB(client=_FakeClient(resp), context=_FakeContextSvc(upload_url_result=url_res))
    ft = FileTransfer(agb, _FakeSession("s-123"))

    out = ft.upload(str(p), "/tmp/remote.txt")
    assert out.success is False
    assert out.request_id_upload_url == "rid"


def test_upload_fails_on_bad_http_status(tmp_path, monkeypatch):
    p = tmp_path / "a.txt"
    p.write_text("hi", encoding="utf-8")
    resp = _FakeInternalContextResponse(ok=True, data=[{"contextId": "cid", "contextPath": "/tmp"}])
    url_res = SimpleNamespace(success=True, url="https://oss/upload", request_id="rid", message=None)
    agb = _FakeAGB(client=_FakeClient(resp), context=_FakeContextSvc(upload_url_result=url_res))
    ft = FileTransfer(agb, _FakeSession("s-123"))

    monkeypatch.setattr(ft, "_put_file_sync", lambda *a, **k: (500, "etag", 3))
    out = ft.upload(str(p), "/tmp/remote.txt", wait=False)
    assert out.success is False
    assert out.http_status == 500


def test_upload_fails_when_sync_raises(tmp_path, monkeypatch):
    p = tmp_path / "a.txt"
    p.write_text("hi", encoding="utf-8")
    resp = _FakeInternalContextResponse(ok=True, data=[{"contextId": "cid", "contextPath": "/tmp"}])
    url_res = SimpleNamespace(success=True, url="https://oss/upload", request_id="rid", message=None)
    agb = _FakeAGB(client=_FakeClient(resp), context=_FakeContextSvc(upload_url_result=url_res))
    ft = FileTransfer(agb, _FakeSession("s-123"))

    monkeypatch.setattr(ft, "_put_file_sync", lambda *a, **k: (200, "etag", 3))
    monkeypatch.setattr(ft, "_await_sync", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("syncfail")))
    out = ft.upload(str(p), "/tmp/remote.txt", wait=False)
    assert out.success is False
    assert "syncfail" in (out.error_message or "")


def test_download_fails_when_ensure_context_id_fails(monkeypatch, tmp_path):
    agb = _FakeAGB(client=None, context=_FakeContextSvc())
    ft = FileTransfer(agb, _FakeSession("s-123"))
    monkeypatch.setattr(ft, "ensure_context_id", lambda: (False, "noctx"))
    out = ft.download("/tmp/remote.txt", str(tmp_path / "out.txt"), wait=False)
    assert out.success is False
    assert "noctx" in (out.error_message or "")


def test_download_fails_when_sync_raises(monkeypatch, tmp_path):
    resp = _FakeInternalContextResponse(ok=True, data=[{"contextId": "cid", "contextPath": "/tmp"}])
    url_res = SimpleNamespace(success=True, url="https://oss/dl", request_id="rid", message=None)

    class _CtxSvc(_FakeContextSvc):
        def get_file_download_url(self, context_id, file_path):
            return url_res

    agb = _FakeAGB(client=_FakeClient(resp), context=_CtxSvc(upload_url_result=None))
    ft = FileTransfer(agb, _FakeSession("s-123"))

    monkeypatch.setattr(ft, "_await_sync", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("syncfail")))
    out = ft.download("/tmp/remote.txt", str(tmp_path / "out.txt"), wait=False)
    assert out.success is False
    assert "syncfail" in (out.error_message or "")


def test_download_fails_when_wait_task_times_out(monkeypatch, tmp_path):
    resp = _FakeInternalContextResponse(ok=True, data=[{"contextId": "cid", "contextPath": "/tmp"}])
    url_res = SimpleNamespace(success=True, url="https://oss/dl", request_id="rid", message=None)

    class _CtxSvc(_FakeContextSvc):
        def get_file_download_url(self, context_id, file_path):
            return url_res

    agb = _FakeAGB(client=_FakeClient(resp), context=_CtxSvc(upload_url_result=None))
    ft = FileTransfer(agb, _FakeSession("s-123"))

    monkeypatch.setattr(ft, "_await_sync", lambda *a, **k: "syncRid")
    monkeypatch.setattr(ft, "_wait_for_task", lambda *a, **k: (False, "timeout"))
    out = ft.download("/tmp/remote.txt", str(tmp_path / "out.txt"), wait=True, wait_timeout=0.01, poll_interval=0.0)
    assert out.success is False
    assert "Download sync not finished" in (out.error_message or "")


def test_download_fails_when_get_download_url_fails(monkeypatch, tmp_path):
    resp = _FakeInternalContextResponse(ok=True, data=[{"contextId": "cid", "contextPath": "/tmp"}])
    url_res = SimpleNamespace(success=False, url=None, request_id="rid", message="bad")

    class _CtxSvc(_FakeContextSvc):
        def get_file_download_url(self, context_id, file_path):
            return url_res

    agb = _FakeAGB(client=_FakeClient(resp), context=_CtxSvc(upload_url_result=None))
    ft = FileTransfer(agb, _FakeSession("s-123"))

    monkeypatch.setattr(ft, "_await_sync", lambda *a, **k: "syncRid")
    out = ft.download("/tmp/remote.txt", str(tmp_path / "out.txt"), wait=False)
    assert out.success is False
    assert out.request_id_download_url == "rid"


def test_download_respects_overwrite_false(monkeypatch, tmp_path):
    resp = _FakeInternalContextResponse(ok=True, data=[{"contextId": "cid", "contextPath": "/tmp"}])
    url_res = SimpleNamespace(success=True, url="https://oss/dl", request_id="rid", message=None)

    class _CtxSvc(_FakeContextSvc):
        def get_file_download_url(self, context_id, file_path):
            return url_res

    agb = _FakeAGB(client=_FakeClient(resp), context=_CtxSvc(upload_url_result=None))
    ft = FileTransfer(agb, _FakeSession("s-123"))

    # create destination file
    out_path = tmp_path / "out.txt"
    out_path.write_text("exists", encoding="utf-8")

    monkeypatch.setattr(ft, "_await_sync", lambda *a, **k: "syncRid")
    out = ft.download("/tmp/remote.txt", str(out_path), wait=False, overwrite=False)
    assert out.success is False
    assert "overwrite=False" in (out.error_message or "")


def test_download_fails_when_http_status_not_200(monkeypatch, tmp_path):
    resp = _FakeInternalContextResponse(ok=True, data=[{"contextId": "cid", "contextPath": "/tmp"}])
    url_res = SimpleNamespace(success=True, url="https://oss/dl", request_id="rid", message=None)

    class _CtxSvc(_FakeContextSvc):
        def get_file_download_url(self, context_id, file_path):
            return url_res

    agb = _FakeAGB(client=_FakeClient(resp), context=_CtxSvc(upload_url_result=None))
    ft = FileTransfer(agb, _FakeSession("s-123"))

    monkeypatch.setattr(ft, "_await_sync", lambda *a, **k: "syncRid")
    monkeypatch.setattr(ft, "_get_file_sync", lambda *a, **k: (404, 0))
    out = ft.download("/tmp/remote.txt", str(tmp_path / "out.txt"), wait=False)
    assert out.success is False
    assert out.http_status == 404


def test_download_success_writes_file(monkeypatch, tmp_path):
    resp = _FakeInternalContextResponse(ok=True, data=[{"contextId": "cid", "contextPath": "/tmp"}])
    url_res = SimpleNamespace(success=True, url="https://oss/dl", request_id="rid", message=None)

    class _CtxSvc(_FakeContextSvc):
        def get_file_download_url(self, context_id, file_path):
            return url_res

    agb = _FakeAGB(client=_FakeClient(resp), context=_CtxSvc(upload_url_result=None))
    ft = FileTransfer(agb, _FakeSession("s-123"))

    out_path = tmp_path / "out.txt"

    def _fake_get(url, local_path, *a, **k):
        # simulate download by writing bytes
        with open(local_path, "wb") as f:
            f.write(b"data")
        return 200, 4

    monkeypatch.setattr(ft, "_await_sync", lambda *a, **k: "syncRid")
    monkeypatch.setattr(ft, "_get_file_sync", _fake_get)
    out = ft.download("/tmp/remote.txt", str(out_path), wait=False)
    assert out.success is True
    assert out.bytes_received == 4


def test_extract_remote_dir_path_rules():
    # file path -> parent dir
    assert FileTransfer._extract_remote_dir_path("/a/b.txt") == "/a"
    # dir path with trailing slash -> normalized dir
    assert FileTransfer._extract_remote_dir_path("/a/b/") == "/a/b"
    # root preserved
    assert FileTransfer._extract_remote_dir_path("/") == "/"
    # relative file -> None
    assert FileTransfer._extract_remote_dir_path("a.txt") is None
    # empty/blank -> None
    assert FileTransfer._extract_remote_dir_path("   ") is None
    # windows style -> normalized
    assert FileTransfer._extract_remote_dir_path("\\a\\b\\c.txt") == "/a/b"


def test_wait_for_task_success(monkeypatch):
    # Arrange a FileTransfer with a fake session.context.info
    resp = _FakeInternalContextResponse(ok=True, data=[{"contextId": "cid", "contextPath": "/tmp"}])
    agb = _FakeAGB(client=_FakeClient(resp), context=_FakeContextSvc())
    sess = _FakeSession("s-123")
    ft = FileTransfer(agb, sess)
    ft.context_id = "cid"

    class _Item:
        context_id = "cid"
        path = "/tmp"
        task_type = "upload"
        status = "success"
        error_message = None

    sess.context.info = lambda **kwargs: SimpleNamespace(context_status_data=[_Item()])  # type: ignore[attr-defined]

    ok, err = ft._wait_for_task(
        context_id="cid",
        remote_path="/tmp/file.txt",
        task_type="upload",
        timeout=0.01,
        interval=0.0,
    )
    assert ok is True
    assert err is None


def test_wait_for_task_error_message(monkeypatch):
    resp = _FakeInternalContextResponse(ok=True, data=[{"contextId": "cid", "contextPath": "/tmp"}])
    agb = _FakeAGB(client=_FakeClient(resp), context=_FakeContextSvc())
    sess = _FakeSession("s-123")
    ft = FileTransfer(agb, sess)
    ft.context_id = "cid"

    class _Item:
        context_id = "cid"
        path = "/tmp"
        task_type = "upload"
        status = "running"
        error_message = "boom"

    sess.context.info = lambda **kwargs: SimpleNamespace(context_status_data=[_Item()])  # type: ignore[attr-defined]

    ok, err = ft._wait_for_task(
        context_id="cid",
        remote_path="/tmp/file.txt",
        task_type="upload",
        timeout=0.01,
        interval=0.0,
    )
    assert ok is False
    assert "boom" in (err or "")


def test_await_sync_fallback_on_typeerror(monkeypatch):
    resp = _FakeInternalContextResponse(ok=True, data=[{"contextId": "cid", "contextPath": "/tmp"}])
    agb = _FakeAGB(client=_FakeClient(resp), context=_FakeContextSvc())
    sess = _FakeSession("s-123")
    ft = FileTransfer(agb, sess)

    calls = {"n": 0}

    async def _sync(**kwargs):
        # First call with (mode, path, context_id) -> TypeError
        calls["n"] += 1
        if calls["n"] == 1:
            raise TypeError("no context_id")
        return SimpleNamespace(success=True, request_id="rid-sync")

    sess.context.sync = _sync  # type: ignore[attr-defined]
    rid = ft._await_sync("upload", "/tmp/file.txt", "cid")
    assert rid == "rid-sync"


def test_put_and_get_file_sync_use_httpx(monkeypatch, tmp_path):
    from agb.modules import file_transfer as ft_mod

    p = tmp_path / "in.bin"
    p.write_bytes(b"abcd")
    out = tmp_path / "out.bin"

    class _Resp:
        status_code = 200
        headers = {"ETag": "etag"}

    class _StreamResp:
        status_code = 200

        def iter_bytes(self):
            yield b"ab"
            yield b"cd"

        def read(self):
            return b""

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class _Client:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def put(self, url, content=None, headers=None):
            return _Resp()

        def stream(self, method, url):
            assert method == "GET"
            return _StreamResp()

    monkeypatch.setattr(ft_mod.httpx, "Client", _Client)

    status, etag, sent = FileTransfer._put_file_sync(
        "https://oss/up", str(p), 1.0, True, None, None
    )
    assert status == 200
    assert etag == "etag"
    assert sent == 4

    status, recv = FileTransfer._get_file_sync(
        "https://oss/dl", str(out), 1.0, True, None
    )
    assert status == 200
    assert recv == 4
    assert out.read_bytes() == b"abcd"

