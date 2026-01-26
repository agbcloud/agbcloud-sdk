import builtins
from io import BytesIO
import sys
import types

import pytest

import agb.version_utils as vu


def test_get_sdk_version_from_installed_package(monkeypatch):
    import importlib.metadata as md

    monkeypatch.setattr(md, "version", lambda name: "9.9.9")
    assert vu.get_sdk_version() == "9.9.9"


def test_get_sdk_version_falls_back_to_pyproject(monkeypatch):
    import importlib.metadata as md

    def _raise(_name):
        raise md.PackageNotFoundError()

    monkeypatch.setattr(md, "version", _raise)

    # CI may run on Python < 3.11 where stdlib `tomllib` doesn't exist.
    # Inject a stub module so `agb.version_utils.get_sdk_version()` can import it.
    tomllib_stub = types.ModuleType("tomllib")
    tomllib_stub.load = lambda f: {"project": {"version": "0.8.0"}}  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "tomllib", tomllib_stub)

    monkeypatch.setattr(builtins, "open", lambda *a, **k: BytesIO(b"[project]\nversion='0.8.0'\n"))

    assert vu.get_sdk_version() == "0.8.0"


def test_get_sdk_version_returns_invalid_version_on_exception(monkeypatch):
    import importlib.metadata as md

    def _raise(_name):
        raise md.PackageNotFoundError()

    monkeypatch.setattr(md, "version", _raise)

    tomllib_stub = types.ModuleType("tomllib")
    tomllib_stub.load = lambda f: (_ for _ in ()).throw(RuntimeError("bad"))  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "tomllib", tomllib_stub)
    monkeypatch.setattr(builtins, "open", lambda *a, **k: BytesIO(b""))

    assert vu.get_sdk_version() == "invalid-version"


def test_get_sdk_version_returns_invalid_version_when_tomllib_missing(monkeypatch):
    import importlib.metadata as md

    def _raise(_name):
        raise md.PackageNotFoundError()

    monkeypatch.setattr(md, "version", _raise)
    monkeypatch.delitem(sys.modules, "tomllib", raising=False)

    # Simulate environments without stdlib tomllib (e.g. Python 3.10) by forcing
    # the import inside `get_sdk_version()` to raise ImportError.
    real_import = builtins.__import__

    def _fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "tomllib":
            raise ImportError("No module named 'tomllib'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _fake_import)

    assert vu.get_sdk_version() == "invalid-version"


def test_is_release_version_flag():
    # In this repo, agb/_release.py exists and sets IS_RELEASE_VERSION.
    assert isinstance(vu.is_release_version(), bool)

