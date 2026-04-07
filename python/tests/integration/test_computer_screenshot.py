"""
Integration tests for computer.screenshot and computer.screen.capture functionality.
"""

import os
import time
import unittest

from agb import AGB
from agb.session_params import CreateSessionParams


class TestComputerScreenshot(unittest.TestCase):
    """Test computer screenshot functionality."""

    def setUp(self):
        """Set up test fixtures."""
        api_key = os.environ.get("AGB_API_KEY")
        if not api_key:
            self.skipTest("AGB_API_KEY environment variable not set")

        self.agb_client = AGB(api_key=api_key)
        session_params = CreateSessionParams(image_id="agb-computer-use-ubuntu-2204")

        session_result = self.agb_client.create(session_params)
        if not session_result.success or session_result.session is None:
            self.fail(f"Session creation failed: {session_result.error_message}")

        self.session = session_result.session
        print(f"Created session: {self.session.session_id}")

        # Wait for session to be ready
        time.sleep(3)

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, "session") and self.session:
            try:
                self.session.delete()
                print(f"Session {self.session.session_id} deleted")
                time.sleep(2)
            except Exception as e:
                print(f"Warning: Failed to delete session: {e}")

    def test_screen_capture_basic(self):
        """Test basic screen capture functionality."""
        print("\n=== Testing screen.capture() ===")

        result = self.session.computer.screen.capture()

        print(f"  success: {result.success}")
        print(f"  request_id: {result.request_id}")
        if result.data:
            print(f"  data: {result.data[:100]}...")

        self.assertTrue(result.success, f"Screen capture failed: {result.error_message}")
        self.assertIsNotNone(result.request_id)
        self.assertTrue(len(result.request_id) > 0)

        # Verify data is a URL string
        self.assertIsInstance(result.data, str)
        self.assertTrue(
            result.data.startswith("http"),
            f"Expected URL, got: {result.data[:50]}"
        )

    def test_screen_get_size(self):
        """Test screen size retrieval."""
        print("\n=== Testing screen.get_size() ===")

        result = self.session.computer.screen.get_size()

        print(f"  success: {result.success}")
        print(f"  request_id: {result.request_id}")
        print(f"  data: {result.data}")

        self.assertTrue(result.success, f"Get screen size failed: {result.error_message}")
        self.assertIsNotNone(result.request_id)

        # Verify data contains screen dimensions
        self.assertIsNotNone(result.data)
        if isinstance(result.data, dict):
            self.assertIn("width", result.data)
            self.assertIn("height", result.data)
            print(f"  Screen: {result.data['width']}x{result.data['height']}")

    def test_screenshot_deprecated(self):
        """Test deprecated computer.screenshot() method still works."""
        print("\n=== Testing deprecated computer.screenshot() ===")

        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = self.session.computer.screenshot()

            # Verify deprecation warning was issued
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("screen.capture", str(w[0].message))

        print(f"  success: {result.success}")
        print(f"  request_id: {result.request_id}")

        self.assertFalse(result.success, f"Screenshot failed: {result.error_message}")
        self.assertIsNone(result.data)


if __name__ == "__main__":
    unittest.main()
