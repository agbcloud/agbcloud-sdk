"""Integration test for SDK idle release timeout.

This test validates that a session created with `idle_release_timeout` will be
automatically released after being idle for long enough.

Notes:
- This is an end-to-end integration test and requires a real AGB_API_KEY.
- It uses `session.get_status()` to observe the session lifecycle.
"""

import os
import time

import pytest

from agb.agb import AGB
from agb.session_params import CreateSessionParams
from agb.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IMAGE_ID = "agb-browser-use-1"
IDLE_RELEASE_TIMEOUT = 60   # seconds – passed to the API
MAX_OVER_SECONDS = 60       # extra grace period after timeout before we fail
POLL_INTERVAL = 2           # seconds between get_status() calls

# ---------------------------------------------------------------------------
# Helpers (封装多次调用的公共逻辑)
# ---------------------------------------------------------------------------

def is_not_found_status(status_result) -> bool:
    """Return True when get_status() indicates the session no longer exists."""
    if getattr(status_result, "success", False):
        return False
    error_message = (getattr(status_result, "error_message", "") or "").lower()
    code = (getattr(status_result, "code", "") or "").lower()
    return ("notfound" in code) or ("not found" in error_message)


def is_released_status(status_result) -> bool:
    """Return True when get_status() shows a terminal release state."""
    if not getattr(status_result, "success", False):
        return False
    return getattr(status_result, "status", "") in {"FINISH", "DELETING", "DELETED"}


def poll_until_released(session, deadline: float, poll_interval: float = POLL_INTERVAL):
    """
    Poll session.get_status() until the session is released or deadline is reached.

    Returns:
        (released: bool, elapsed: float, last_status)
    """
    last_status = None
    while time.monotonic() < deadline:
        status = session.get_status()
        last_status = status
        if is_not_found_status(status) or is_released_status(status):
            return True, time.monotonic(), last_status
        time.sleep(poll_interval)
    return False, time.monotonic(), last_status


def assert_not_released_before_timeout(session, timeout_deadline: float, poll_interval: float = POLL_INTERVAL):
    """
    Poll session.get_status() until timeout_deadline and assert the session is NOT released early.
    """
    while True:
        now = time.monotonic()
        if now >= timeout_deadline:
            break
        status = session.get_status()
        if is_not_found_status(status):
            pytest.fail(
                f"Session was released too early: got NotFound before {IDLE_RELEASE_TIMEOUT}s"
            )
        if is_released_status(status):
            pytest.fail(
                f"Session was released too early: status={status.status} before {IDLE_RELEASE_TIMEOUT}s"
            )
        remaining = timeout_deadline - now
        time.sleep(min(poll_interval, max(0.0, remaining)))


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------

class TestSessionIdleReleaseTimeout:
    """Integration tests for `idle_release_timeout` parameter."""

    @pytest.fixture(scope="class")
    def agb(self):
        api_key = os.getenv("AGB_API_KEY")
        if not api_key:
            pytest.skip("AGB_API_KEY environment variable not set")
        return AGB(api_key=api_key)

    def test_session_releases_after_idle_timeout(self, agb):
        """
        Create a session with idle_release_timeout and verify it is released
        within the expected time window [idle_release_timeout, idle_release_timeout + max_over_seconds].

        We only call get_status() periodically and do not invoke any MCP tools,
        so the environment is considered idle from the SDK side.
        """
        logger.info(
            f"Creating session with image_id={IMAGE_ID}, "
            f"idle_release_timeout={IDLE_RELEASE_TIMEOUT}s"
        )

        session = None
        start_time = time.monotonic()

        try:
            params = CreateSessionParams(
                image_id=IMAGE_ID,
                idle_release_timeout=IDLE_RELEASE_TIMEOUT,
                labels={
                    "test": "idle-release-timeout",
                    "sdk": "python",
                },
            )
            result = agb.create(params)
            assert result.success, f"Create session failed: {result.error_message}"
            assert result.session is not None, "Session should not be None"
            session = result.session
            logger.info(f"✅ Session created: {session.session_id}")

            # Phase 1: assert session is NOT released before the timeout
            timeout_deadline = start_time + IDLE_RELEASE_TIMEOUT
            assert_not_released_before_timeout(session, timeout_deadline)

            # Phase 2: wait for the session to be released within the grace period
            release_deadline = timeout_deadline + MAX_OVER_SECONDS
            released, release_time, last_status = poll_until_released(session, release_deadline)

            if not released:
                details = ""
                if last_status is not None:
                    details = (
                        f"last_success={getattr(last_status, 'success', False)}, "
                        f"last_status={getattr(last_status, 'status', '')}, "
                        f"last_error={getattr(last_status, 'error_message', '')}"
                    )
                pytest.fail(
                    f"Session was not released within expected time window "
                    f"{IDLE_RELEASE_TIMEOUT}s~{IDLE_RELEASE_TIMEOUT + MAX_OVER_SECONDS}s. {details}"
                )

            elapsed = release_time - start_time
            assert elapsed >= IDLE_RELEASE_TIMEOUT, "Session was released too early"
            assert elapsed <= IDLE_RELEASE_TIMEOUT + MAX_OVER_SECONDS, "Session was released too late"

            if is_not_found_status(last_status):
                logger.info(f"✅ Session released: get_status returned NotFound, elapsed={elapsed:.2f}s")
            else:
                logger.info(f"✅ Session released: status={last_status.status}, elapsed={elapsed:.2f}s")

        finally:
            if session is not None:
                try:
                    status_final = session.get_status()
                    if not is_not_found_status(status_final) and not is_released_status(status_final):
                        logger.info("🧹 Cleaning up: deleting session explicitly...")
                        agb.delete(session)
                except Exception:
                    pass
