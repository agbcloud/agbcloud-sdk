"""
Integration test for app start -> get PID -> stop_by_cmd(kill -9) flow.

Tests the flow documented in docs/computer/applications.md:
1. Start an application with app.start(start_cmd)
2. Get PID from start_result.data[0].pid
3. Stop the process with stop_by_cmd(f"kill -9 {pid}")

Requires AGB_API_KEY. Uses Ubuntu computer image (agb-computer-use-ubuntu-2204).
"""

import os
import time
import unittest

from agb import AGB
from agb.session_params import CreateSessionParams


class TestAppStopByCmdFlow(unittest.TestCase):
    """Test start app -> get PID -> stop_by_cmd(kill -9) flow."""

    def setUp(self):
        """Create AGB client and Ubuntu session."""
        api_key = os.environ.get("AGB_API_KEY")
        if not api_key:
            self.skipTest("AGB_API_KEY environment variable not set")

        self.agb_client = AGB(api_key=api_key)
        session_params = CreateSessionParams(image_id="agb-computer-use-ubuntu-2204")
        session_result = self.agb_client.create(session_params)

        if not session_result.success or not session_result.session:
            self.fail(
                f"Session creation failed: {session_result.error_message or 'Unknown error'}"
            )

        self.session = session_result.session
        print(f"Created session: {self.session.session_id}")
        time.sleep(3)

    def tearDown(self):
        """Release session."""
        if hasattr(self, "session") and self.session:
            try:
                self.session.delete()
                time.sleep(2)
            except Exception as e:
                print(f"Error deleting session: {e}")

    def test_start_then_stop_by_cmd_kill_9(self):
        """
        Test flow: start app -> get PID from start result -> stop_by_cmd("kill -9 <pid>").
        """
        # Get an app from list_installed (Ubuntu image has no notepad.exe)
        apps_result = self.session.computer.app.list_installed()
        self.assertTrue(apps_result.success, apps_result.error_message or "list_installed failed")
        self.assertIsNotNone(apps_result.data, "list_installed returned no apps")
        self.assertGreater(len(apps_result.data), 0, "list_installed returned empty list")

        first_app = apps_result.data[3]
        start_cmd = getattr(first_app, "start_cmd", None)
        self.assertIsNotNone(start_cmd, "First app has no start_cmd")
        app_name = getattr(first_app, "name", "Unknown")

        # Start the application
        start_result = self.session.computer.app.start(start_cmd)
        self.assertTrue(start_result.success, start_result.error_message or "start failed")
        self.assertTrue(
            start_result.data,
            f"start returned no processes for {app_name} ({start_cmd})",
        )

        pid = start_result.data[0].pid
        self.assertIsNotNone(pid, "Process has no pid")

        print(f"Started {app_name} (start_cmd={start_cmd}), PID={pid}")

        # Allow process to be visible to kill
        time.sleep(2)

        # Stop by shell command: kill -9 <pid>
        result = self.session.computer.app.stop_by_cmd(f"kill -9 {pid}")
        self.assertTrue(
            result.success,
            f"stop_by_cmd(kill -9 {pid}) failed: {result.error_message}",
        )
        print(f"stop_by_cmd('kill -9 {pid}'): success={result.success}")


if __name__ == "__main__":
    unittest.main()
