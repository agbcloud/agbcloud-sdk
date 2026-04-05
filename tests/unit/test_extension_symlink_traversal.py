"""Tests for symlink / path-traversal protection in ExtensionsService (CWE-22)."""
from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

from agb.extension import (
    EXTENSIONS_BASE_PATH,
    Extension,
    ExtensionsService,
    _validate_local_path,
)


# ---------------------------------------------------------------------------
# Reusable fakes (same pattern as existing test_extension_service.py)
# ---------------------------------------------------------------------------

class _FakeContext:
    def __init__(self, cid="ctx-1"):
        self.id = cid


class _FakeContextService:
    def __init__(self):
        self._get_result = SimpleNamespace(success=True, context=_FakeContext("ctx-1"))

    def get(self, context_id, create=False):
        return self._get_result

    def list_files(self, **kwargs):
        entry = SimpleNamespace(file_name="ext_1.zip", gmt_create="2026-01-01T00:00:00Z")
        return SimpleNamespace(success=True, entries=[entry])

    def delete_file(self, context_id, remote_path):
        return SimpleNamespace(success=True)

    def delete(self, context):
        return True

    def get_file_upload_url(self, context_id, remote_path):
        return SimpleNamespace(success=True, url="https://oss/upload")


class _FakeAGB:
    def __init__(self, context_service):
        self.context = context_service


# ---------------------------------------------------------------------------
# _validate_local_path unit tests
# ---------------------------------------------------------------------------

class TestValidateLocalPath:
    def test_rejects_symlink(self, tmp_path):
        target = tmp_path / "real.zip"
        target.write_bytes(b"PK")
        link = tmp_path / "link.zip"
        os.symlink(str(target), str(link))

        with pytest.raises(ValueError, match="Symbolic links are not allowed"):
            _validate_local_path(str(link))

    def test_rejects_nonexistent(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            _validate_local_path(str(tmp_path / "missing.zip"))

    def test_rejects_directory(self, tmp_path):
        d = tmp_path / "adir"
        d.mkdir()
        with pytest.raises(FileNotFoundError):
            _validate_local_path(str(d))

    def test_accepts_regular_file(self, tmp_path):
        f = tmp_path / "ok.zip"
        f.write_bytes(b"PK")
        result = _validate_local_path(str(f))
        assert os.path.isabs(result)
        assert not os.path.islink(result)


# ---------------------------------------------------------------------------
# Integration: create() / update() reject symlinks
# ---------------------------------------------------------------------------

class TestCreateRejectsSymlink:
    def test_create_rejects_symlink_to_sensitive_file(self, tmp_path, monkeypatch):
        ctx_svc = _FakeContextService()
        svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")

        uploaded = []
        monkeypatch.setattr(svc, "_upload_to_cloud", lambda *a, **k: uploaded.append(1))

        sensitive = tmp_path / "secret_data"
        sensitive.write_text("TOP SECRET")

        symlink = tmp_path / "evil.zip"
        os.symlink(str(sensitive), str(symlink))

        with pytest.raises(ValueError, match="Symbolic links"):
            svc.create(str(symlink))

        assert len(uploaded) == 0

    def test_create_still_works_for_regular_zip(self, tmp_path, monkeypatch):
        ctx_svc = _FakeContextService()
        svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")

        monkeypatch.setattr(svc, "_upload_to_cloud", lambda *a, **k: None)

        import agb.extension as ext_mod
        monkeypatch.setattr(ext_mod.uuid, "uuid4", lambda: SimpleNamespace(hex="aabbccdd"))

        legit = tmp_path / "good.zip"
        legit.write_bytes(b"PK\x03\x04data")

        ext = svc.create(str(legit))
        assert ext.id.startswith("ext_aabbccdd")


class TestUpdateRejectsSymlink:
    def test_update_rejects_symlink(self, tmp_path, monkeypatch):
        ctx_svc = _FakeContextService()
        svc = ExtensionsService(_FakeAGB(ctx_svc), context_id="ctx")

        uploaded = []
        monkeypatch.setattr(svc, "_upload_to_cloud", lambda *a, **k: uploaded.append(1))
        monkeypatch.setattr(svc, "list", lambda: [Extension(id="ext_1.zip", name="x")])

        sensitive = tmp_path / "shadow"
        sensitive.write_text("root:x:0:0:::/bin/sh")

        symlink = tmp_path / "payload.zip"
        os.symlink(str(sensitive), str(symlink))

        with pytest.raises(ValueError, match="Symbolic links"):
            svc.update("ext_1.zip", str(symlink))

        assert len(uploaded) == 0
