"""
FileTransfer integration tests (real sessions + real file transfers).

Notes:
- These tests require a real AGB account and network access.
- The API key is read ONLY from the `AGB_API_KEY` environment variable (do not hardcode secrets).
"""

from __future__ import annotations

import os
import tempfile
import time

import pytest

from agb import AGB
from agb.session_params import CreateSessionParams


def _require_agb_api_key() -> str:
    """Read AGB_API_KEY from environment; fail fast if missing."""
    api_key = os.environ.get("AGB_API_KEY", "").strip()
    if not api_key or os.environ.get("CI"):
        pytest.fail("Integration test prerequisite not met: AGB_API_KEY is not set or running in CI")
    return api_key


def _safe_join_dir_file(dir_path: str, file_name: str) -> str:
    """Join a directory path and a file name, avoiding duplicate slashes."""
    base = (dir_path or "").rstrip("/")
    return f"{base}/{file_name}" if base else f"/{file_name}"


def _sleep_for_session_ready() -> None:
    """
    Heuristic wait for session initialization (including internal context readiness).
    Backend can be flaky in integration environments, so use a conservative delay.
    """
    time.sleep(6)


def test_file_transfer_upload_integration() -> None:
    """
    Verify the full upload workflow:
    1) Resolve file_transfer context_path
    2) Upload host -> OSS via presigned PUT
    3) Trigger session.context.sync(download) to pull into the session filesystem
    4) Verify file existence and content inside the session
    """
    api_key = _require_agb_api_key()
    agb = AGB(api_key)

    params = CreateSessionParams(image_id="agb-code-space-2")
    session_result = agb.create(params)
    if not session_result.success or not session_result.session:
        pytest.fail(f"Failed to create session: {session_result.error_message}")

    session = session_result.session

    try:
        _sleep_for_session_ready()

        context_path = session.file_system.get_file_transfer_context_path()
        if not context_path:
            pytest.fail("Failed to get file_transfer context_path (backend may not return internal context)")

        remote_path = _safe_join_dir_file(context_path, "upload_test.txt")

        test_content = ("This is AGB FileTransfer upload integration test content.\n" * 10)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(test_content)
            f.flush()
            local_path = f.name

        try:
            upload_result = session.file_system.upload_file(
                local_path=local_path,
                remote_path=remote_path,
                wait=True,
                wait_timeout=300.0,
                poll_interval=2.0,
            )

            assert upload_result.success, f"Upload failed: {upload_result.error_message}"
            assert upload_result.bytes_sent > 0
            assert upload_result.request_id_upload_url
            assert upload_result.request_id_sync

            # Verify the directory exists
            ls = session.command.execute_command(
                f"ls -la {context_path.rstrip('/')}/",
                timeout_ms=10_000,
            )
            assert ls.success, f"Remote directory does not exist or is not accessible: {ls.error_message}"

            # Verify the file exists
            list_result = session.file_system.list_directory(f"{context_path.rstrip('/')}/")
            assert list_result.success, f"list_directory failed: {list_result.error_message}"
            assert any(
                (it.get("name") == "upload_test.txt" and not it.get("isDirectory", False))
                for it in list_result.entries
            ), "Uploaded file is not present in directory listing"

            # Verify content matches
            read_result = session.file_system.read_file(remote_path)
            assert read_result.success, f"read_file failed: {read_result.error_message}"
            # Normalize line endings to handle \r\n vs \n differences
            expected_content = test_content.replace('\r\n', '\n').replace('\r', '\n').strip()
            actual_content = read_result.content.replace('\r\n', '\n').replace('\r', '\n').strip()
            assert actual_content == expected_content

        finally:
            try:
                os.unlink(local_path)
            except OSError:
                pass
    finally:
        try:
            agb.delete(session, sync_context=False)
        except Exception:
            # Do not fail the test on cleanup errors in integration environment.
            pass


def test_file_transfer_download_integration() -> None:
    """
    Verify the full download workflow:
    1) Create a file inside the session filesystem
    2) Trigger session.context.sync(upload) to push to OSS
    3) Download to a local host path via presigned URL
    4) Verify the downloaded content matches
    """
    api_key = _require_agb_api_key()
    agb = AGB(api_key)

    params = CreateSessionParams(image_id="agb-code-space-2")
    session_result = agb.create(params)
    if not session_result.success or not session_result.session:
        pytest.fail(f"Failed to create session: {session_result.error_message}")

    session = session_result.session

    try:
        _sleep_for_session_ready()

        context_path = session.file_system.get_file_transfer_context_path()
        if not context_path:
            pytest.fail("Failed to get file_transfer context_path (backend may not return internal context)")

        remote_path = _safe_join_dir_file(context_path, "download_test.txt")
        test_content = ("This is AGB FileTransfer download integration test content.\n" * 15)

        # Ensure directory exists, then write the remote file
        mkdir_res = session.file_system.create_directory(f"{context_path.rstrip('/')}/")
        assert mkdir_res.success, f"create_directory failed: {mkdir_res.error_message}"

        write_res = session.file_system.write_file(remote_path, test_content, "overwrite")
        assert write_res.success, f"write_file failed: {write_res.error_message}"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            local_path = f.name

        try:
            download_result = session.file_system.download_file(
                remote_path=remote_path,
                local_path=local_path,
                overwrite=True,
                wait=True,
                wait_timeout=300.0,
                poll_interval=2.0,
            )

            assert download_result.success, f"Download failed: {download_result.error_message}"
            assert download_result.bytes_received > 0
            assert download_result.request_id_download_url
            assert download_result.request_id_sync
            assert download_result.local_path == local_path

            with open(local_path, "r", encoding="utf-8") as rf:
                downloaded = rf.read()
            assert downloaded == test_content

        finally:
            try:
                os.unlink(local_path)
            except OSError:
                pass

    finally:
        try:
            agb.delete(session, sync_context=False)
        except Exception:
            pass


