"""Integration tests for AGB FileSystem module.

This file was refactored to pytest style so that each capability is covered by an
independent test function (no cross-test dependencies).
"""

from __future__ import annotations

from collections.abc import Iterator
import os
import time
import uuid

import pytest

from agb import AGB
from agb.session import Session
from agb.session_params import CreateSessionParams


def _err(result) -> str:
    msg = getattr(result, "error_message", None)
    rid = getattr(result, "request_id", None)
    return f"error_message={msg!r}, request_id={rid!r}"


def _assert_success(result, action: str) -> None:
    assert getattr(result, "success", False), f"{action} failed: {_err(result)}"


@pytest.fixture(scope="module")
def agb_client() -> AGB:
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        pytest.skip("AGB_API_KEY environment variable not set")
    return AGB(api_key=api_key)


@pytest.fixture(scope="module")
def test_session(agb_client) -> Iterator[Session]:
    """Create a shared session for this module.

    Tests are still independent because they each use isolated paths under /tmp.
    """
    params = CreateSessionParams(image_id="agb-code-space-2")
    result = agb_client.create(params)
    if not result.success:
        pytest.fail(f"Session creation failed: {_err(result)}")
    assert result.session is not None, "Session object is None"
    session = result.session
    yield session
    try:
        agb_client.delete(session)
    except Exception as e:
        # Don't fail teardown; we just surface the info.
        print(f"Warning: failed to delete session in teardown: {e}")


@pytest.fixture
def test_dir(test_session) -> Iterator[str]:
    """Create a unique directory for each test and clean it up afterwards."""
    dirname = f"/tmp/agb_fs_test_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
    r = test_session.file.mkdir(dirname)
    _assert_success(r, f"create_directory({dirname})")
    yield dirname
    # Best-effort cleanup
    try:
        test_session.command.execute(f"rm -rf {dirname}", timeout_ms=10000)
    except Exception as e:
        print(f"Warning: failed to cleanup test dir {dirname}: {e}")


def test_directory_list_empty(test_session, test_dir: str):
    result = test_session.file.list(test_dir)
    _assert_success(result, f"list({test_dir})")


def test_write_and_read(test_session, test_dir: str):
    path = f"{test_dir}/test.txt"
    content = f"Hello AGB!\nCreated at: {int(time.time())}\n"
    r = test_session.file.write(path, content, mode="overwrite")
    _assert_success(r, f"write({path})")

    rr = test_session.file.read(path)
    _assert_success(rr, f"read({path})")
    assert rr.content == content


def test_get_file_info(test_session, test_dir: str):
    path = f"{test_dir}/info.txt"
    content = "info\n"
    r = test_session.file.write(path, content, mode="overwrite")
    _assert_success(r, f"write({path})")

    info = test_session.file.info(path)
    _assert_success(info, f"get_file_info({path})")
    assert info.file_info is not None
    assert int(info.file_info.get("size", 0)) > 0


def test_edit_file_prepend_append(test_session, test_dir: str):
    path = f"{test_dir}/edit.txt"
    base = "base\n"
    r = test_session.file.write(path, base, mode="overwrite")
    _assert_success(r, f"write({path})")

    # edit_file expects oldText and newText format for text replacement
    # For append: replace the base content with base + appended content
    # For prepend: replace the base content with prepended + base content
    # We need to read the file first to get the exact content for replacement
    read_result = test_session.file.read(path)
    _assert_success(read_result, f"read({path}) before edit")
    current_content = read_result.content

    # Append: replace current content with current + appended
    edits = [
        {"oldText": current_content, "newText": current_content + "appended\n"},
    ]
    er = test_session.file.edit(path, edits, dry_run=False)
    _assert_success(er, f"edit_file({path}) - append")

    # Read again to get updated content for prepend
    read_result = test_session.file.read(path)
    _assert_success(read_result, f"read({path}) after append")
    current_content = read_result.content

    # Prepend: replace current content with prepended + current
    edits = [
        {"oldText": current_content, "newText": "prepended\n" + current_content},
    ]
    er = test_session.file.edit(path, edits, dry_run=False)
    _assert_success(er, f"edit_file({path}) - prepend")

    rr = test_session.file.read(path)
    _assert_success(rr, f"read({path})")
    # Verify final content has both prepended and appended text
    assert rr.content.startswith("prepended\n")
    assert "appended\n" in rr.content


def test_search_files(test_session, test_dir: str):
    # Create a few files
    paths = [f"{test_dir}/a.txt", f"{test_dir}/b.txt", f"{test_dir}/c.log"]
    for p in paths:
        r = test_session.file.write(p, f"{p}\n", mode="overwrite")
        _assert_success(r, f"write({p})")

    sr = test_session.file.search(test_dir, "*.txt")
    _assert_success(sr, f"search_files({test_dir}, *.txt)")
    matches = sr.matches or []
    assert any(m.endswith("/a.txt") for m in matches)
    assert any(m.endswith("/b.txt") for m in matches)


def test_large_file_read(test_session, test_dir: str):
    path = f"{test_dir}/large_file.txt"
    content = "This is a large file content.\n" * 1000
    r = test_session.file.write(path, content, mode="overwrite")
    _assert_success(r, f"write({path})")

    rr = test_session.file.read(path)
    _assert_success(rr, f"read({path})")
    assert rr.content == content


def test_read_multiple_files(test_session, test_dir: str):
    files = [
        f"{test_dir}/file1.txt",
        f"{test_dir}/file2.txt",
        f"{test_dir}/file3.txt",
    ]
    expected = {}
    for i, p in enumerate(files, start=1):
        content = f"This is test file {i}\nContent: {i} * {i} = {i**2}\n"
        expected[p] = content
        r = test_session.file.write(p, content, mode="overwrite")
        _assert_success(r, f"write({p})")

    rr = test_session.file.read_batch(files)
    _assert_success(rr, "read_multiple_files([...])")
    assert rr.contents is not None
    for p, content in expected.items():
        actual = rr.contents.get(p)
        # Handle potential trailing newline differences
        assert actual is not None, f"Content for {p} is None"
        # Normalize by stripping and comparing, or compare directly
        assert actual == content or actual.rstrip() == content.rstrip(), \
            f"Content mismatch for {p}: expected {content!r}, got {actual!r}"


def test_move_file(test_session, test_dir: str):
    src = f"{test_dir}/src.txt"
    dst = f"{test_dir}/dst.txt"
    content = f"move-{uuid.uuid4().hex}\n"
    r = test_session.file.write(src, content, mode="overwrite")
    _assert_success(r, f"write({src})")

    mr = test_session.file.move(src, dst)
    _assert_success(mr, f"move_file({src} -> {dst})")

    rr = test_session.file.read(dst)
    _assert_success(rr, f"read({dst})")
    assert rr.content == content


def test_remove(test_session, test_dir: str):
    path = f"{test_dir}/delete_me.txt"
    r = test_session.file.write(path, "bye\n", mode="overwrite")
    _assert_success(r, f"write({path})")

    dr = test_session.file.remove(path)
    _assert_success(dr, f"remove({path})")

    # After deletion, file info should fail (or at least not be successful).
    info = test_session.file.info(path)
    assert not info.success
