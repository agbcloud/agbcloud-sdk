"""Integration test: write a large file (12 000 chars, repeating a-z) on a browser image."""

from __future__ import annotations

from collections.abc import Iterator
import os
import string
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
    assert getattr(result, "success",
                   False), f"{action} failed: {_err(result)}"


@pytest.fixture(scope="module")
def agb_client() -> AGB:
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        pytest.skip("AGB_API_KEY environment variable not set")
    return AGB(api_key=api_key)


@pytest.fixture(scope="module")
def browser_session(agb_client) -> Iterator[Session]:
    """Create a browser-image session (agb-browser-use-1)."""
    params = CreateSessionParams(image_id="agb-code-space-2")
    result = agb_client.create(params)
    if not result.success:
        pytest.fail(f"Browser session creation failed: {_err(result)}")
    assert result.session is not None, "Session object is None"
    session = result.session
    yield session
    try:
        agb_client.delete(session)
    except Exception as e:
        print(f"Warning: failed to delete browser session in teardown: {e}")


def test_write_large_file_on_browser_image(browser_session):
    """Write a 12 000-char file (repeating a-z) on a browser image and read it back."""
    alphabet = string.ascii_lowercase  # 'abcdefghijklmnopqrstuvwxyz'
    target_len = 12000
    # Build content: repeat 26 letters until we reach 12000 chars
    full_repeats, remainder = divmod(target_len, len(alphabet))
    content = alphabet * full_repeats + alphabet[:remainder]
    assert len(content) == target_len

    path = f"/tmp/large_abc_{int(time.time())}_{uuid.uuid4().hex[:8]}.txt"

    # Write
    wr = browser_session.file.write(path, content, mode="overwrite")
    _assert_success(wr, f"write({path})")

    # Read back and verify
    rr = browser_session.file.read(path)
    _assert_success(rr, f"read({path})")
    assert rr.content == content, (
        f"Content mismatch: expected {target_len} chars, got {len(rr.content)} chars"
    )
