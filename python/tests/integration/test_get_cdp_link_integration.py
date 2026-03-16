# -*- coding: utf-8 -*-
"""
Integration tests for getCdpLink API.

Run with:
    pytest tests/integration/test_get_cdp_link_integration.py -v
    pytest -k test_get_cdp_link -v
"""

import os
import unittest

from agb.agb import AGB
from agb.api.models.get_cdp_link_request import GetCdpLinkRequest
from agb.modules.browser.browser import BrowserOption
from agb.session_params import CreateSessionParams


def get_test_api_key() -> str:
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        raise unittest.SkipTest("AGB_API_KEY environment variable not set")
    return api_key


class TestGetCdpLinkIntegration(unittest.TestCase):
    """Integration tests for getCdpLink API with real browser session."""

    @classmethod
    def setUpClass(cls):
        api_key = get_test_api_key()
        cls.agb = AGB(api_key=api_key)
        result = cls.agb.create(
            CreateSessionParams(image_id="agb-browser-use-1")
        )
        if not result.success or result.session is None:
            raise RuntimeError(
                f"Failed to create session: {result.error_message}"
            )
        cls.session = result.session
        cls.api_key = api_key

        if not cls.session.browser.initialize(BrowserOption(use_stealth=True)):
            raise RuntimeError("Failed to initialize browser")

        print(f"Session created: {cls.session.session_id}")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "agb") and hasattr(cls, "session"):
            try:
                cls.agb.delete(cls.session)
                print(f"Session deleted: {cls.session.session_id}")
            except Exception as e:
                print(f"Warning: failed to delete session: {e}")

    def test_get_cdp_link_api_call(self):
        """Test direct getCdpLink API call returns a response."""
        request = GetCdpLinkRequest(
            authorization=f"Bearer {self.api_key}",
            session_id=self.session.get_session_id(),
        )
        response = self.session.get_client().get_cdp_link(request)

        self.assertIsNotNone(response)
        self.assertIsNotNone(response.status_code)
        print(f"getCdpLink status: {response.status_code}")

        if response.status_code == 404:
            self.fail("getCdpLink API not deployed (404)")

        self.assertTrue(
            response.is_successful(),
            f"getCdpLink failed: {response.get_error_message()}",
        )
        url = response.get_url()
        self.assertIsNotNone(url)
        self.assertGreater(len(url), 0)
        print(f"CDP URL: {url}")

    def test_get_cdp_link_request_params(self):
        """Test that request carries correct sessionId as query param."""
        request = GetCdpLinkRequest(
            authorization=f"Bearer {self.api_key}",
            session_id=self.session.get_session_id(),
        )
        params = request.get_params()
        self.assertEqual(params["sessionId"], self.session.get_session_id())
        self.assertEqual(request.get_body(), {})

    def test_get_endpoint_url_via_browser(self):
        """Test Browser.get_endpoint_url() which uses getCdpLink internally."""
        try:
            url = self.session.browser.get_endpoint_url()
            self.assertIsNotNone(url)
            self.assertGreater(len(url), 0)
            print(f"Endpoint URL: {url}")
        except Exception as e:
            if "404" in str(e) or "Unknown error" in str(e):
                self.fail(f"getCdpLink API not available: {e}")
            raise


if __name__ == "__main__":
    unittest.main()
