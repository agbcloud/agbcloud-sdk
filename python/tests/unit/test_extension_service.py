from __future__ import annotations

from types import SimpleNamespace

import pytest

from agb.exceptions import AGBError
from agb.extension import EXTENSIONS_BASE_PATH, Extension, ExtensionOption, ExtensionsService


class _FakeContext:
    def __init__(self, cid="ctx-1"):
        self.id = cid


class _FakeContextService:
    def __init__(self):
        self.get_calls = []
        self.list_files_calls = []
        self.delete_file_calls = []
        self.delete_calls = []
        self.get_file_upload_url_calls = []
        self._get_result = SimpleNamespace(success=True, context=_FakeContext("ctx-1"))

    def get(self, context_id, create=False):
        self.get_calls.append((context_id, create))
        return self._get_result

    def list_files(self, **kwargs):
        self.list_files_calls.append(kwargs)
        # Return one fake extension file
        entry = SimpleNamespace(file_name="ext_1.zip", gmt_create="2026-01-01T00:00:00Z")
        return SimpleNamespace(success=True, entries=[entry])

    def delete_file(self, context_id, remote_path):
        self.delete_file_calls.append((context_id, remote_path))
        return SimpleNamespace(success=True)

    def delete(self, context):
        self.delete_calls.append(context)
        return True

    def get_file_upload_url(self, context_id, remote_path):
        self.get_file_upload_url_calls.append((context_id, remote_path))
        return SimpleNamespace(success=True, url="https://oss/upload")


class _FakeAGB:
    def __init__(self, context_service):
        self.context = context_service


def test_extension_option_validation_and_str_repr():
    opt = ExtensionOption(context_id="ctx", extension_ids=["a", "b"])
    assert opt.validate() is True
    assert "ExtensionOption(" in repr(opt)
    assert "extension(s)" in str(opt)

    with pytest.raises(ValueError):
        ExtensionOption(context_id="", extension_ids=["a"])
    with pytest.raises(ValueError):
        ExtensionOption(context_id="ctx", extension_ids=[])


def test_extensions_service_init_creates_context(monkeypatch):
    ctx_svc = _FakeContextService()
    agb = _FakeAGB(ctx_svc)

    # Force deterministic generated name
    import agb.extension as ext_mod

    monkeypatch.setattr(ext_mod.time, "time", lambda: 123)
    svc = ExtensionsService(agb, context_id="")
    assert svc.context_id == "ctx-1"
    assert ctx_svc.get_calls[0][1] is True


def test_extensions_service_init_raises_when_context_create_fails():
    ctx_svc = _FakeContextService()
    ctx_svc._get_result = SimpleNamespace(success=False, context=None)
    agb = _FakeAGB(ctx_svc)
    with pytest.raises(AGBError):
        ExtensionsService(agb, context_id="bad")


def test_list_returns_extensions():
    ctx_svc = _FakeContextService()
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")
    exts = svc.list()
    assert len(exts) == 1
    assert isinstance(exts[0], Extension)
    assert ctx_svc.list_files_calls[0]["parent_folder_path"] == EXTENSIONS_BASE_PATH


def test_create_validates_file_and_calls_upload(tmp_path, monkeypatch):
    ctx_svc = _FakeContextService()
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")

    p = tmp_path / "a.zip"
    p.write_bytes(b"zip")

    # Avoid real upload; also make uuid deterministic
    monkeypatch.setattr(svc, "_upload_to_cloud", lambda *a, **k: None)
    import agb.extension as ext_mod

    monkeypatch.setattr(ext_mod.uuid, "uuid4", lambda: SimpleNamespace(hex="deadbeef"))

    ext = svc.create(str(p))
    assert ext.id.startswith("ext_deadbeef")
    assert ext.name == "a.zip"

    with pytest.raises(ValueError):
        bad = tmp_path / "a.txt"
        bad.write_text("x", encoding="utf-8")
        svc.create(str(bad))


def test_update_checks_existence(tmp_path, monkeypatch):
    ctx_svc = _FakeContextService()
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")

    newp = tmp_path / "new.zip"
    newp.write_bytes(b"zip")

    monkeypatch.setattr(svc, "_upload_to_cloud", lambda *a, **k: None)
    monkeypatch.setattr(svc, "list", lambda: [Extension(id="ext_1.zip", name="x")])
    out = svc.update("ext_1.zip", str(newp))
    assert out.id == "ext_1.zip"

    with pytest.raises(ValueError):
        svc.update("missing.zip", str(newp))


def test_delete_and_cleanup():
    ctx_svc = _FakeContextService()
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")

    assert svc.delete("ext_1.zip") is True
    assert ctx_svc.delete_file_calls[-1][1] == f"{EXTENSIONS_BASE_PATH}/ext_1.zip"

    assert svc.cleanup() is True
    assert len(ctx_svc.delete_calls) == 1


def test_extension_option_validate_false_cases():
    opt = ExtensionOption(context_id="ctx", extension_ids=["a"])
    opt.context_id = ""
    assert opt.validate() is False

    opt = ExtensionOption(context_id="ctx", extension_ids=[" "])
    assert opt.validate() is False  # invalid ext id (blank)

    opt = ExtensionOption(context_id="ctx", extension_ids=["a"])
    opt.extension_ids = []  # type: ignore[assignment]
    assert opt.validate() is False

    opt = ExtensionOption(context_id="ctx", extension_ids=["a"])
    opt.extension_ids = None  # type: ignore[assignment]
    assert opt.validate() is False


def test_get_extension_info_returns_none_on_list_exception(monkeypatch):
    ctx_svc = _FakeContextService()
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")
    monkeypatch.setattr(svc, "list", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    assert svc._get_extension_info("ext_1.zip") is None


def test_delete_returns_false_on_exception(monkeypatch):
    ctx_svc = _FakeContextService()
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")
    monkeypatch.setattr(ctx_svc, "delete_file", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    assert svc.delete("ext_1.zip") is False


def test_list_raises_agb_error_on_exception(monkeypatch):
    ctx_svc = _FakeContextService()
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")
    monkeypatch.setattr(ctx_svc, "list_files", lambda **k: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(AGBError, match="listing browser extensions"):
        svc.list()


def test_create_raises_file_not_found():
    ctx_svc = _FakeContextService()
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")
    with pytest.raises(FileNotFoundError):
        svc.create("/path/does/not/exist.zip")


def test_upload_to_cloud_wraps_request_exception(monkeypatch, tmp_path):
    import agb.extension as ext_mod

    ctx_svc = _FakeContextService()
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")

    p = tmp_path / "a.zip"
    p.write_bytes(b"zip")

    class _Sess:
        def mount(self, *a, **k):
            pass

        def put(self, url, data=None, timeout=None):
            raise ext_mod.requests.exceptions.RequestException("down")

        def close(self):
            pass

    monkeypatch.setattr(ext_mod.requests, "Session", lambda: _Sess())
    with pytest.raises(AGBError, match="uploading the file"):
        svc._upload_to_cloud(str(p), f"{EXTENSIONS_BASE_PATH}/ext_1.zip")


def test_cleanup_noop_when_not_auto_created():
    ctx_svc = _FakeContextService()
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")
    svc.auto_created = False
    assert svc.cleanup() is True


def test_cleanup_returns_false_when_delete_returns_false(monkeypatch):
    ctx_svc = _FakeContextService()
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")
    monkeypatch.setattr(ctx_svc, "delete", lambda ctx: False)
    assert svc.cleanup() is False


def test_create_extension_option_smoke():
    ctx_svc = _FakeContextService()
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")
    opt = svc.create_extension_option(["ext_1.zip"])
    assert opt.context_id == svc.context_id
    assert opt.extension_ids == ["ext_1.zip"]


def test_update_raises_file_not_found(tmp_path):
    ctx_svc = _FakeContextService()
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")
    with pytest.raises(FileNotFoundError):
        svc.update("ext_1.zip", str(tmp_path / "missing.zip"))


def test_extension_option_validate_exception_branch():
    class _BadList:
        def __len__(self):
            raise RuntimeError("boom")

    opt = ExtensionOption(context_id="ctx", extension_ids=["a"])
    opt.extension_ids = _BadList()  # type: ignore[assignment]
    assert opt.validate() is False


def test_upload_to_cloud_raises_when_upload_url_missing(monkeypatch, tmp_path):
    ctx_svc = _FakeContextService()
    ctx_svc.get_file_upload_url = lambda context_id, remote_path: SimpleNamespace(  # type: ignore[method-assign]
        success=False, url=None
    )
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")

    p = tmp_path / "a.zip"
    p.write_bytes(b"zip")

    with pytest.raises(AGBError, match="Failed to get upload URL"):
        svc._upload_to_cloud(str(p), f"{EXTENSIONS_BASE_PATH}/ext_1.zip")


def test_upload_to_cloud_success_uses_requests_session(monkeypatch, tmp_path):
    import agb.extension as ext_mod

    ctx_svc = _FakeContextService()
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")

    p = tmp_path / "a.zip"
    p.write_bytes(b"zip")

    calls = {"put": 0, "mounted": 0, "closed": 0}

    class _Resp:
        def raise_for_status(self):
            return None

    class _Sess:
        def mount(self, *a, **k):
            calls["mounted"] += 1

        def put(self, url, data=None, timeout=None):
            calls["put"] += 1
            assert timeout == 120
            return _Resp()

        def close(self):
            calls["closed"] += 1

    monkeypatch.setattr(ext_mod.requests, "Session", lambda: _Sess())

    svc._upload_to_cloud(str(p), f"{EXTENSIONS_BASE_PATH}/ext_1.zip")
    assert calls["mounted"] >= 2  # http + https
    assert calls["put"] == 1
    assert calls["closed"] == 1


def test_upload_to_cloud_wraps_timeout(monkeypatch, tmp_path):
    import agb.extension as ext_mod

    ctx_svc = _FakeContextService()
    svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")

    p = tmp_path / "a.zip"
    p.write_bytes(b"zip")

    class _Sess:
        def mount(self, *a, **k):
            pass

        def put(self, url, data=None, timeout=None):
            raise ext_mod.requests.exceptions.Timeout("slow")

        def close(self):
            pass

    monkeypatch.setattr(ext_mod.requests, "Session", lambda: _Sess())

    with pytest.raises(AGBError, match="Upload timeout"):
        svc._upload_to_cloud(str(p), f"{EXTENSIONS_BASE_PATH}/ext_1.zip")

