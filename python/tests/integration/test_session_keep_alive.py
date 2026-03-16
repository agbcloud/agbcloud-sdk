"""Integration test for Session.keep_alive.

This test validates that calling keep_alive refreshes the backend idle timer.

Strategy (no mocks, end-to-end):
- Create 2 sessions with the same idle_release_timeout.
- Call keep_alive on one session halfway through.
- Wait until the control session is released.
- Assert the refreshed session is still alive at that moment.

Notes:
- Requires a real AGB_API_KEY environment variable.
- Uses get_status polling to observe lifecycle.
"""

import os
import time
import unittest

import pytest

from agb import AGB, CreateSessionParams


def _mask_secret(secret: str, visible: int = 4) -> str:
    """Mask a secret value, keeping only the last `visible` characters."""
    if not secret:
        return ""
    if len(secret) <= visible:
        return "*" * len(secret)
    return ("*" * (len(secret) - visible)) + secret[-visible:]


def _is_not_found_status_result(status_result) -> bool:
    """Return True if get_status result indicates session is gone."""
    if getattr(status_result, "success", False):
        return False
    error_message = (getattr(status_result, "error_message", "") or "").lower()
    code = (getattr(status_result, "code", "") or "").lower()
    return ("notfound" in code) or ("not found" in error_message)


def _is_terminal_status(status_result) -> bool:
    """Return True if session is in a terminal state."""
    if not getattr(status_result, "success", False):
        return _is_not_found_status_result(status_result)
    return getattr(status_result, "status", "") in ["FINISH", "DELETING", "DELETED"]


class TestSessionKeepAliveIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        api_key = os.environ.get("AGB_API_KEY")
        if not api_key:
            raise unittest.SkipTest("AGB_API_KEY environment variable not set")
        cls.api_key = api_key
        cls.agb = AGB(api_key=api_key)

    def test_keep_alive_resets_idle_timer(self):
        """Test that keep_alive extends session lifetime."""
        idle_release_timeout = 60  # seconds
        max_over_seconds = 60  # control session must be released within timeout + 60s
        poll_interval = 15  # seconds
        image_id = "agb-browser-use-1"

        print("api_key =", _mask_secret(self.api_key))
        print(
            f"Creating 2 sessions with "
            f"image_id={image_id}, idle_release_timeout={idle_release_timeout}s"
        )

        control_session = None
        refreshed_session = None

        start_time = time.monotonic()
        try:
            common_labels = {"test": "session-keep-alive", "sdk": "python"}

            # Create control session
            control_params = CreateSessionParams(
                image_id=image_id,
                idle_release_timeout=idle_release_timeout,
                labels={**common_labels, "role": "control"},
            )
            control_result = self.agb.create(control_params)
            self.assertTrue(
                control_result.success,
                f"Create control session failed: {control_result.error_message}",
            )
            self.assertIsNotNone(control_result.session)
            control_session = control_result.session

            # Create refreshed session
            refreshed_params = CreateSessionParams(
                image_id=image_id,
                idle_release_timeout=idle_release_timeout,
                labels={**common_labels, "role": "refreshed"},
            )
            refreshed_result = self.agb.create(refreshed_params)
            self.assertTrue(
                refreshed_result.success,
                f"Create refreshed session failed: {refreshed_result.error_message}",
            )
            self.assertIsNotNone(refreshed_result.session)
            refreshed_session = refreshed_result.session

            print(f"✅ Control session: {control_session.session_id}")
            print(f"✅ Refreshed session: {refreshed_session.session_id}")

            # Wait until halfway through, then refresh the idle timer for refreshed session
            time.sleep(idle_release_timeout / 2 + 15)
            keep_alive_result = refreshed_session.keep_alive()
            self.assertTrue(
                keep_alive_result.success,
                f"keep_alive failed: {getattr(keep_alive_result, 'error_message', '')}",
            )
            print(f"✅ Called keep_alive on refreshed session at {idle_release_timeout / 2}s")

            deadline = start_time + idle_release_timeout + max_over_seconds
            control_released_at = None

            # Poll until control session is released
            while time.monotonic() < deadline:
                control_status = control_session.get_status()
                refreshed_status = refreshed_session.get_status()

                # Check if control session is released
                if _is_terminal_status(control_status):
                    control_released_at = time.monotonic()
                    # At this point, refreshed session should still be alive
                    self.assertFalse(
                        _is_terminal_status(refreshed_status),
                        "Refreshed session was released no later than control session; "
                        "keep_alive did not extend idle timer as expected",
                    )
                    elapsed = control_released_at - start_time
                    print(
                        f"✅ Control session released while refreshed session still alive, "
                        f"elapsed={elapsed:.2f}s"
                    )
                    return

                # Check if refreshed session was released before control session (unexpected)
                if _is_terminal_status(refreshed_status):
                    self.fail(
                        "Refreshed session was released before control session; "
                        "keep_alive may have failed"
                    )

                time.sleep(poll_interval)

            # If we reach here, test failed due to timeout
            self.fail(
                f"Timeout after {max_over_seconds}s: control session was not released"
            )

        finally:
            # Best-effort cleanup
            for s in [refreshed_session, control_session]:
                if s is None:
                    continue
                try:
                    status_final = s.get_status()
                    if not _is_terminal_status(status_final):
                        self.agb.delete(s)
                except Exception:
                    pass


if __name__ == "__main__":
    unittest.main()
