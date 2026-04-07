#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket streaming code execution integration tests for AGB SDK.

Covers:
  - stream_beta=True real-time stdout/stderr callback streaming
  - Low-level call_stream cancel via handle.cancel()
"""

import os
import time

import pytest

from agb import AGB
from agb.session_params import CreateSessionParams
from agb.model.response import EnhancedCodeExecutionResult
from agb.modules.ws.exceptions import WsCancelledError

# ---------------------------------------------------------------------------
# Shared session fixture
# ---------------------------------------------------------------------------

_shared_session = None
_shared_agb = None


def _get_shared_session():
    """Lazily create a shared AGB session for all tests in this module."""
    global _shared_session, _shared_agb

    if _shared_session is None:
        api_key = os.getenv("AGB_API_KEY")
        if not api_key:
            pytest.skip("AGB_API_KEY environment variable not set")

        _shared_agb = AGB(api_key=api_key)
        result = _shared_agb.create(CreateSessionParams(image_id="agb-computer-use-ubuntu-2204"))
        assert result.success, f"Failed to create session: {result.error_message}"
        assert result.session is not None
        _shared_session = result.session

    return _shared_session


@pytest.fixture(scope="module", autouse=True)
def _cleanup_session():
    """Delete the shared session after all tests in this module finish."""
    yield
    if _shared_session is not None:
        try:
            _shared_session.delete()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Test 1 – stream_beta streaming E2E
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_run_code_ws_streaming_e2e():
    """Verify stream_beta=True delivers real-time stdout chunks."""
    session = _get_shared_session()

    stdout_chunks: list[str] = []
    stdout_times: list[float] = []
    stderr_chunks: list[str] = []
    errors: list[object] = []

    start_t = time.monotonic()
    result = session.code.run(
        "import time\n"
        "print('hello', flush=True)\n"
        "time.sleep(1.0)\n"
        "print(2, flush=True)\n",
        "python",
        timeout_s=60,
        stream_beta=True,
        on_stdout=lambda chunk: (stdout_chunks.append(chunk), stdout_times.append(time.monotonic())),
        on_stderr=lambda chunk: stderr_chunks.append(chunk),
        on_error=lambda err: errors.append(err),
    )
    end_t = time.monotonic()

    # Basic assertions
    assert isinstance(result, EnhancedCodeExecutionResult)
    assert errors == [], f"errors={errors}, stdout={stdout_chunks}, stderr={stderr_chunks}"
    assert result.success, f"error_message={result.error_message}, stdout={stdout_chunks}, stderr={stderr_chunks}"

    # At least two separate stdout events (one per print)
    assert len(stdout_chunks) >= 2, f"expected >=2 stdout events, got {len(stdout_chunks)}: {stdout_chunks!r}"

    # Total wall-clock time should reflect the sleep(1.0)
    assert end_t - start_t >= 1.0, f"expected duration >=1.0s, got {end_t - start_t:.3f}s"

    # Content check
    joined = "".join(stdout_chunks)
    assert "hello" in joined
    assert "2" in joined

    # Streaming timing: "2" should arrive ≥0.8s after "hello"
    hello_t = next((t for t, c in zip(stdout_times, stdout_chunks) if "hello" in c), None)
    two_t = next((t for t, c in zip(stdout_times, stdout_chunks) if "2" in c), None)
    assert hello_t is not None, f"'hello' not found in stdout chunks: {stdout_chunks!r}"
    assert two_t is not None, f"'2' not found in stdout chunks: {stdout_chunks!r}"
    assert two_t - hello_t >= 0.8, (
        f"stdout callbacks not streaming; delta={two_t - hello_t:.3f}s, chunks={stdout_chunks!r}"
    )


# ---------------------------------------------------------------------------
# Test 2 – call_stream cancel E2E
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_run_code_ws_stream_cancel_e2e():
    """Verify that handle.cancel() aborts a running stream and raises WsCancelledError."""
    session = _get_shared_session()

    assert session.ws_url, "Backend did not return ws_url in CreateSession response"

    ws_client = session._get_ws_client()
    ws_client.connect()

    # Resolve target (mirrors _resolve_stream_target logic)
    target = "wuying_codespace"
    for tool in getattr(session, "tool_list", []) or []:
        try:
            if getattr(tool, "name", "") == "run_code" and getattr(tool, "server", ""):
                target = tool.server
                break
        except Exception:
            continue

    events: list[dict] = []
    ends: list[dict] = []
    errors: list[Exception] = []

    handle = ws_client.call_stream(
        target=target,
        data={
            "method": "run_code",
            "mode": "stream",
            "params": {
                "language": "python",
                "timeoutS": 60,
                "code": (
                    "import time\n"
                    "print(0, flush=True)\n"
                    "time.sleep(10)\n"
                    "print(1, flush=True)\n"
                ),
            },
        },
        on_event=lambda inv, data: events.append(data),
        on_end=lambda inv, data: ends.append(data),
        on_error=lambda inv, err: errors.append(err),
    )

    # Give the server a moment to start, then cancel
    time.sleep(0.5)
    handle.cancel()

    t0 = time.monotonic()
    with pytest.raises(WsCancelledError):
        handle.wait_end()
    assert time.monotonic() - t0 < 2.0, "cancel did not unblock wait_end within 2s"

    assert ends == [], f"unexpected on_end after cancel: ends={ends}, events={events}, errors={errors}"
    assert len(errors) == 1, f"expected exactly 1 on_error, got errors={errors}"
    assert isinstance(errors[0], WsCancelledError), f"expected WsCancelledError, got {errors[0]!r}"
