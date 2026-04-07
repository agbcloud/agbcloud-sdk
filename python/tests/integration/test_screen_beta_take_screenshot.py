"""
Integration tests for screen.beta_take_screenshot functionality.
"""

import os
import time
import unittest

from agb import AGB
from agb.session_params import CreateSessionParams
from agb.exceptions import ScreenError


class TestScreenBetaTakeScreenshot(unittest.TestCase):
    """Test screen.beta_take_screenshot functionality."""

    def setUp(self):
        """Set up test fixtures."""
        api_key = os.environ.get("AGB_API_KEY")
        if not api_key:
            self.skipTest("AGB_API_KEY environment variable not set")

        self.agb_client = AGB(api_key=api_key)
        # Use browser-use image which has link_url
        session_params = CreateSessionParams(
            image_id="agb-computer-use-ubuntu-2204")

        session_result = self.agb_client.create(session_params)
        if not session_result.success or session_result.session is None:
            self.fail(
                f"Session creation failed: {session_result.error_message}")

        self.session = session_result.session
        print(f"Created session: {self.session.session_id}")

        # Wait for session to be ready
        time.sleep(5)

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, "session") and self.session:
            try:
                self.session.delete()
                print(f"Session {self.session.session_id} deleted")
                time.sleep(2)
            except Exception as e:
                print(f"Warning: Failed to delete session: {e}")

    def test_beta_take_screenshot_png(self):
        """Test beta_take_screenshot with PNG format."""
        print("\n=== Testing screen.beta_take_screenshot(format='png') ===")

        result = self.session.computer.screen.beta_take_screenshot(
            format="png")

        print(f"  success: {result.success}")
        print(f"  request_id: {result.request_id}")
        print(f"  type: {result.type}")
        print(f"  mime_type: {result.mime_type}")
        print(f"  width: {result.width}")
        print(f"  height: {result.height}")
        print(f"  data size: {len(result.data) if result.data else 0} bytes")

        self.assertTrue(result.success)
        self.assertIsNotNone(result.request_id)
        self.assertEqual(result.mime_type, "image/png")
        self.assertIsInstance(result.data, bytes)
        self.assertTrue(len(result.data) > 0)
        # Verify PNG magic bytes
        self.assertTrue(result.data.startswith(b"\x89PNG\r\n\x1a\n"))

    def test_beta_take_screenshot_jpeg(self):
        """Test beta_take_screenshot with JPEG format."""
        print("\n=== Testing screen.beta_take_screenshot(format='jpeg') ===")

        result = self.session.computer.screen.beta_take_screenshot(
            format="jpeg")

        print(f"  success: {result.success}")
        print(f"  request_id: {result.request_id}")
        print(f"  type: {result.type}")
        print(f"  mime_type: {result.mime_type}")
        print(f"  width: {result.width}")
        print(f"  height: {result.height}")
        print(f"  data size: {len(result.data) if result.data else 0} bytes")

        self.assertTrue(result.success)
        self.assertIsNotNone(result.request_id)
        self.assertEqual(result.mime_type, "image/jpeg")
        self.assertIsInstance(result.data, bytes)
        self.assertTrue(len(result.data) > 0)
        # Verify JPEG magic bytes
        self.assertTrue(result.data.startswith(b"\xff\xd8\xff"))

    def test_beta_take_screenshot_jpg_alias(self):
        """Test beta_take_screenshot with jpg alias."""
        print("\n=== Testing screen.beta_take_screenshot(format='jpg') ===")

        result = self.session.computer.screen.beta_take_screenshot(
            format="jpg")

        print(f"  success: {result.success}")
        print(f"  mime_type: {result.mime_type}")

        self.assertTrue(result.success)
        self.assertEqual(result.mime_type, "image/jpeg")
        # Verify JPEG magic bytes
        self.assertTrue(result.data.startswith(b"\xff\xd8\xff"))

    def test_beta_take_screenshot_invalid_format(self):
        """Test beta_take_screenshot with invalid format raises ValueError."""
        print("\n=== Testing screen.beta_take_screenshot(format='gif') - should raise ValueError ===")

        with self.assertRaises(ValueError) as context:
            self.session.computer.screen.beta_take_screenshot(format="gif")

        print(f"  Caught expected error: {context.exception}")
        self.assertIn("Invalid format", str(context.exception))

    def test_beta_take_screenshot_dimensions(self):
        """Test that screenshot returns valid dimensions."""
        print("\n=== Testing screenshot dimensions ===")

        result = self.session.computer.screen.beta_take_screenshot()

        print(f"  width: {result.width}")
        print(f"  height: {result.height}")

        self.assertIsNotNone(result.width)
        self.assertIsNotNone(result.height)
        self.assertIsInstance(result.width, int)
        self.assertIsInstance(result.height, int)
        self.assertGreater(result.width, 0)
        self.assertGreater(result.height, 0)


class TestScreenBetaTakeScreenshotComputerUse(unittest.TestCase):
    """Test beta_take_screenshot fails correctly on Computer Use image."""

    def setUp(self):
        """Set up test fixtures."""
        api_key = os.environ.get("AGB_API_KEY")
        if not api_key:
            self.skipTest("AGB_API_KEY environment variable not set")

        self.agb_client = AGB(api_key=api_key)
        # Use computer-use image which does NOT have link_url
        session_params = CreateSessionParams(
            image_id="agb-computer-use-ubuntu-2204")

        session_result = self.agb_client.create(session_params)
        if not session_result.success or session_result.session is None:
            self.fail(
                f"Session creation failed: {session_result.error_message}")

        self.session = session_result.session
        print(f"Created session: {self.session.session_id}")

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

    def test_beta_take_screenshot_not_supported(self):
        """Test beta_take_screenshot raises ScreenError on unsupported environment."""
        print("\n=== Testing beta_take_screenshot on Computer Use image - should raise ScreenError ===")

        # Debug: Check if link_url exists
        link_url = ""
        try:
            link_url = self.session.get_link_url() or ""
        except Exception:
            link_url = getattr(self.session, "link_url", "") or ""
        print(f"  link_url: {link_url[:50] if link_url else '(empty)'}")

        if link_url:
            # If link_url exists, beta_take_screenshot should work
            # This means the environment supports it, so skip this test
            self.skipTest(
                "Environment has link_url, beta_take_screenshot is supported")

        with self.assertRaises(ScreenError) as context:
            self.session.computer.screen.beta_take_screenshot()

        print(f"  Caught expected error: {context.exception}")
        self.assertIn("does not support", str(context.exception))
        self.assertIn("capture()", str(context.exception))


if __name__ == "__main__":
    unittest.main()
