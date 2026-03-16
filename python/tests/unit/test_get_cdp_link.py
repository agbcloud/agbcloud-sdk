# -*- coding: utf-8 -*-
"""
Unit tests for getCdpLink API integration in Browser module.
"""

import unittest
from unittest.mock import MagicMock, patch

from agb.api.models.get_cdp_link_request import GetCdpLinkRequest
from agb.api.models.get_cdp_link_response import GetCdpLinkResponse
from agb.exceptions import BrowserError
from agb.modules.browser.browser import Browser, BrowserOption


class TestGetCdpLinkRequest(unittest.TestCase):
    """Tests for GetCdpLinkRequest model."""

    def test_get_params_with_session_id(self):
        req = GetCdpLinkRequest(
            authorization="Bearer test-key",
            session_id="sess-123",
        )
        params = req.get_params()
        self.assertEqual(params["sessionId"], "sess-123")
        self.assertNotIn("authorization", params)

    def test_get_params_empty(self):
        req = GetCdpLinkRequest()
        params = req.get_params()
        self.assertEqual(params, {})

    def test_get_body_always_empty(self):
        req = GetCdpLinkRequest(
            authorization="Bearer test-key",
            session_id="sess-123",
        )
        self.assertEqual(req.get_body(), {})

    def test_validate_success(self):
        req = GetCdpLinkRequest(
            authorization="Bearer test-key",
            session_id="sess-123",
        )
        self.assertTrue(req.validate())

    def test_validate_missing_auth(self):
        req = GetCdpLinkRequest(session_id="sess-123")
        self.assertFalse(req.validate())

    def test_validate_missing_session(self):
        req = GetCdpLinkRequest(authorization="Bearer test-key")
        self.assertFalse(req.validate())

    def test_to_dict(self):
        req = GetCdpLinkRequest(
            authorization="Bearer test-key",
            session_id="sess-123",
        )
        d = req.to_dict()
        self.assertEqual(d["authorization"], "Bearer test-key")
        self.assertEqual(d["session_id"], "sess-123")


class TestGetCdpLinkResponse(unittest.TestCase):
    """Tests for GetCdpLinkResponse model."""

    def test_successful_response(self):
        resp_dict = {
            "status_code": 200,
            "success": True,
            "json": {
                "success": True,
                "requestId": "req-abc",
                "data": {"url": "ws://localhost:9222/devtools/browser/abc"},
            },
        }
        resp = GetCdpLinkResponse.from_http_response(resp_dict)
        self.assertTrue(resp.is_successful())
        self.assertEqual(resp.get_url(), "ws://localhost:9222/devtools/browser/abc")
        self.assertEqual(resp.request_id, "req-abc")

    def test_api_failure(self):
        resp_dict = {
            "status_code": 200,
            "success": True,
            "json": {
                "success": False,
                "message": "Service unavailable",
                "requestId": "req-err",
            },
        }
        resp = GetCdpLinkResponse.from_http_response(resp_dict)
        self.assertFalse(resp.is_successful())
        self.assertEqual(resp.get_error_message(), "Service unavailable")
        self.assertIsNone(resp.get_url())

    def test_http_failure(self):
        resp_dict = {
            "status_code": 500,
            "success": False,
            "error": "Internal Server Error",
            "json": None,
        }
        resp = GetCdpLinkResponse.from_http_response(resp_dict)
        self.assertFalse(resp.is_successful())
        self.assertEqual(resp.get_error_message(), "Internal Server Error")

    def test_no_url_in_data(self):
        resp_dict = {
            "status_code": 200,
            "success": True,
            "json": {
                "success": True,
                "requestId": "req-nourl",
                "data": {},
            },
        }
        resp = GetCdpLinkResponse.from_http_response(resp_dict)
        self.assertTrue(resp.is_successful())
        self.assertIsNone(resp.get_url())

    def test_no_json(self):
        resp_dict = {
            "status_code": 200,
            "success": True,
            "json": None,
        }
        resp = GetCdpLinkResponse.from_http_response(resp_dict)
        self.assertFalse(resp.is_successful())
        self.assertEqual(resp.get_error_message(), "Unknown error")


def _create_mock_session():
    """Create a mock Session for Browser tests."""
    mock_session = MagicMock()
    mock_session.get_api_key.return_value = "test-api-key"
    mock_session.get_session_id.return_value = "test-session-id"
    return mock_session


def _mock_init_browser_response(success=True, port=9222, error_msg=None):
    resp = MagicMock()
    resp.is_successful.return_value = success
    resp.get_port.return_value = port if success else None
    resp.get_error_message.return_value = error_msg or "init failed"
    resp.request_id = "req-init"
    return resp


def _mock_cdp_link_response(success=True, url=None, error_msg=None):
    resp = MagicMock()
    resp.is_successful.return_value = success
    resp.get_url.return_value = url
    resp.get_error_message.return_value = error_msg or "Unknown error"
    resp.request_id = "req-cdp"
    return resp


class TestBrowserGetEndpointUrl(unittest.TestCase):
    """Tests for Browser.get_endpoint_url using getCdpLink API."""

    def _init_browser(self, session):
        """Helper to initialize browser with mocked init_browser."""
        session.get_client.return_value.init_browser.return_value = (
            _mock_init_browser_response()
        )
        browser = Browser(session)
        option = BrowserOption()
        result = browser.initialize(option)
        self.assertTrue(result)
        self.assertTrue(browser.is_initialized())
        return browser

    def test_get_endpoint_url_not_initialized_raises(self):
        session = _create_mock_session()
        browser = Browser(session)
        with self.assertRaises(BrowserError) as ctx:
            browser.get_endpoint_url()
        self.assertIn("not initialized", str(ctx.exception))

    def test_get_endpoint_url_success(self):
        session = _create_mock_session()
        session.get_client.return_value.get_cdp_link.return_value = (
            _mock_cdp_link_response(
                success=True,
                url="ws://localhost:9222/devtools/browser/abc",
            )
        )
        browser = self._init_browser(session)
        url = browser.get_endpoint_url()
        self.assertEqual(url, "ws://localhost:9222/devtools/browser/abc")
        session.get_client.return_value.get_cdp_link.assert_called_once()

    def test_get_endpoint_url_api_failure(self):
        session = _create_mock_session()
        session.get_client.return_value.get_cdp_link.return_value = (
            _mock_cdp_link_response(
                success=False,
                error_msg="Service unavailable",
            )
        )
        browser = self._init_browser(session)
        with self.assertRaises(BrowserError) as ctx:
            browser.get_endpoint_url()
        self.assertIn("Service unavailable", str(ctx.exception))

    def test_get_endpoint_url_no_url_in_response(self):
        session = _create_mock_session()
        session.get_client.return_value.get_cdp_link.return_value = (
            _mock_cdp_link_response(success=True, url=None)
        )
        browser = self._init_browser(session)
        with self.assertRaises(BrowserError) as ctx:
            browser.get_endpoint_url()
        self.assertIn("No URL", str(ctx.exception))

    def test_get_endpoint_url_network_error(self):
        session = _create_mock_session()
        session.get_client.return_value.get_cdp_link.side_effect = (
            ConnectionError("Network down")
        )
        browser = self._init_browser(session)
        with self.assertRaises(BrowserError) as ctx:
            browser.get_endpoint_url()
        self.assertIn("Network down", str(ctx.exception))

    def test_get_endpoint_url_request_params(self):
        """Verify the request is constructed with correct authorization and session_id."""
        session = _create_mock_session()
        session.get_client.return_value.get_cdp_link.return_value = (
            _mock_cdp_link_response(
                success=True,
                url="ws://localhost:9222/devtools/browser/xyz",
            )
        )
        browser = self._init_browser(session)
        browser.get_endpoint_url()

        call_args = session.get_client.return_value.get_cdp_link.call_args
        request_arg = call_args[0][0]
        self.assertEqual(request_arg.authorization, "Bearer test-api-key")
        self.assertEqual(request_arg.session_id, "test-session-id")


if __name__ == "__main__":
    unittest.main()
