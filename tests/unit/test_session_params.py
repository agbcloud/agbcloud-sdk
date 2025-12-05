#!/usr/bin/env python3
"""
Unit tests for SessionParams module in AGB SDK.
Tests CreateSessionParams and BrowserContext with success and failure scenarios.
"""

import unittest
from unittest.mock import MagicMock

from agb.session_params import CreateSessionParams, BrowserContext
from agb.context_sync import ContextSync, SyncPolicy, UploadPolicy, DownloadPolicy
from agb.extension import ExtensionOption


class TestBrowserContext(unittest.TestCase):
    """Test BrowserContext class."""

    def test_browser_context_initialization_basic(self):
        """Test BrowserContext initialization without extensions."""
        browser_ctx = BrowserContext(
            context_id="browser-ctx-1",
            auto_upload=True,
        )

        self.assertEqual(browser_ctx.context_id, "browser-ctx-1")
        self.assertTrue(browser_ctx.auto_upload)
        self.assertIsNone(browser_ctx.extension_option)
        self.assertIsNone(browser_ctx.extension_context_id)
        self.assertEqual(browser_ctx.extension_ids, [])
        self.assertIsNone(browser_ctx.extension_context_syncs)

    def test_browser_context_with_extensions(self):
        """Test BrowserContext initialization with extensions."""
        ext_option = ExtensionOption(
            context_id="ext-ctx-1",
            extension_ids=["ext-1", "ext-2"],
        )

        browser_ctx = BrowserContext(
            context_id="browser-ctx-2",
            auto_upload=True,
            extension_option=ext_option,
        )

        self.assertEqual(browser_ctx.context_id, "browser-ctx-2")
        self.assertTrue(browser_ctx.auto_upload)
        self.assertEqual(browser_ctx.extension_option, ext_option)
        self.assertEqual(browser_ctx.extension_context_id, "ext-ctx-1")
        self.assertEqual(browser_ctx.extension_ids, ["ext-1", "ext-2"])
        self.assertIsNotNone(browser_ctx.extension_context_syncs)
        self.assertEqual(len(browser_ctx.extension_context_syncs), 1)

    def test_browser_context_get_extension_context_syncs_with_extensions(self):
        """Test get_extension_context_syncs with extensions."""
        ext_option = ExtensionOption(
            context_id="ext-ctx-1",
            extension_ids=["ext-1"],
        )

        browser_ctx = BrowserContext(
            context_id="browser-ctx-3",
            auto_upload=True,
            extension_option=ext_option,
        )

        syncs = browser_ctx.get_extension_context_syncs()
        self.assertEqual(len(syncs), 1)
        self.assertEqual(syncs[0].context_id, "ext-ctx-1")
        self.assertEqual(syncs[0].path, "/tmp/extensions/")

    def test_browser_context_get_extension_context_syncs_without_extensions(self):
        """Test get_extension_context_syncs without extensions."""
        browser_ctx = BrowserContext(
            context_id="browser-ctx-4",
            auto_upload=False,
        )

        syncs = browser_ctx.get_extension_context_syncs()
        self.assertEqual(len(syncs), 0)

    def test_browser_context_auto_upload_false(self):
        """Test BrowserContext with auto_upload=False."""
        browser_ctx = BrowserContext(
            context_id="browser-ctx-5",
            auto_upload=False,
        )

        self.assertFalse(browser_ctx.auto_upload)


class TestCreateSessionParams(unittest.TestCase):
    """Test CreateSessionParams class."""

    def test_create_session_params_minimal(self):
        """Test CreateSessionParams with minimal parameters."""
        params = CreateSessionParams()

        self.assertEqual(params.labels, {})
        self.assertIsNone(params.image_id)
        self.assertEqual(params.context_syncs, [])
        self.assertIsNone(params.browser_context)

    def test_create_session_params_with_labels(self):
        """Test CreateSessionParams with labels."""
        labels = {"env": "test", "version": "1.0"}
        params = CreateSessionParams(labels=labels)

        self.assertEqual(params.labels, labels)
        self.assertIsNone(params.image_id)

    def test_create_session_params_with_image_id(self):
        """Test CreateSessionParams with image_id."""
        params = CreateSessionParams(image_id="image-123")

        self.assertEqual(params.image_id, "image-123")
        self.assertEqual(params.labels, {})

    def test_create_session_params_with_context_syncs(self):
        """Test CreateSessionParams with context syncs."""
        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy(auto_upload=True),
        )
        context_sync = ContextSync(
            context_id="ctx-1",
            path="/tmp/test",
            policy=sync_policy,
        )

        params = CreateSessionParams(context_syncs=[context_sync])

        self.assertEqual(len(params.context_syncs), 1)
        self.assertEqual(params.context_syncs[0].context_id, "ctx-1")

    def test_create_session_params_with_browser_context_no_extensions(self):
        """Test CreateSessionParams with BrowserContext without extensions."""
        browser_ctx = BrowserContext(
            context_id="browser-ctx-1",
            auto_upload=True,
        )

        params = CreateSessionParams(browser_context=browser_ctx)

        self.assertEqual(params.browser_context, browser_ctx)
        self.assertEqual(len(params.context_syncs), 0)

    def test_create_session_params_with_browser_context_with_extensions(self):
        """Test CreateSessionParams with BrowserContext with extensions."""
        ext_option = ExtensionOption(
            context_id="ext-ctx-1",
            extension_ids=["ext-1"],
        )
        browser_ctx = BrowserContext(
            context_id="browser-ctx-2",
            auto_upload=True,
            extension_option=ext_option,
        )

        params = CreateSessionParams(browser_context=browser_ctx)

        self.assertEqual(params.browser_context, browser_ctx)
        # Extension context syncs should be added automatically
        self.assertEqual(len(params.context_syncs), 1)
        self.assertEqual(params.context_syncs[0].context_id, "ext-ctx-1")

    def test_create_session_params_with_both_context_syncs_and_browser_context(self):
        """Test CreateSessionParams with both context_syncs and browser_context."""
        # Create a regular context sync
        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy(auto_upload=True),
        )
        context_sync = ContextSync(
            context_id="ctx-regular",
            path="/tmp/regular",
            policy=sync_policy,
        )

        # Create browser context with extensions
        ext_option = ExtensionOption(
            context_id="ext-ctx-1",
            extension_ids=["ext-1"],
        )
        browser_ctx = BrowserContext(
            context_id="browser-ctx-1",
            auto_upload=True,
            extension_option=ext_option,
        )

        params = CreateSessionParams(
            context_syncs=[context_sync],
            browser_context=browser_ctx,
        )

        # Both should be present
        self.assertEqual(len(params.context_syncs), 2)
        # First should be the regular context sync
        self.assertEqual(params.context_syncs[0].context_id, "ctx-regular")
        # Second should be the extension context sync
        self.assertEqual(params.context_syncs[1].context_id, "ext-ctx-1")

    def test_create_session_params_all_parameters(self):
        """Test CreateSessionParams with all parameters."""
        labels = {"env": "prod", "team": "backend"}
        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy(auto_upload=True),
        )
        context_sync = ContextSync(
            context_id="ctx-full",
            path="/tmp/full",
            policy=sync_policy,
        )
        browser_ctx = BrowserContext(
            context_id="browser-full",
            auto_upload=True,
        )

        params = CreateSessionParams(
            labels=labels,
            image_id="image-full",
            context_syncs=[context_sync],
            browser_context=browser_ctx,
        )

        self.assertEqual(params.labels, labels)
        self.assertEqual(params.image_id, "image-full")
        self.assertEqual(len(params.context_syncs), 1)
        self.assertEqual(params.browser_context, browser_ctx)

    def test_create_session_params_empty_labels(self):
        """Test CreateSessionParams with empty labels dict."""
        params = CreateSessionParams(labels={})

        self.assertEqual(params.labels, {})

    def test_create_session_params_none_labels(self):
        """Test CreateSessionParams with None labels (should default to empty dict)."""
        params = CreateSessionParams(labels=None)

        self.assertEqual(params.labels, {})

    def test_create_session_params_multiple_context_syncs(self):
        """Test CreateSessionParams with multiple context syncs."""
        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy(auto_upload=True),
        )
        sync1 = ContextSync(context_id="ctx-1", path="/tmp/1", policy=sync_policy)
        sync2 = ContextSync(context_id="ctx-2", path="/tmp/2", policy=sync_policy)

        params = CreateSessionParams(context_syncs=[sync1, sync2])

        self.assertEqual(len(params.context_syncs), 2)
        self.assertEqual(params.context_syncs[0].context_id, "ctx-1")
        self.assertEqual(params.context_syncs[1].context_id, "ctx-2")


if __name__ == "__main__":
    unittest.main()

