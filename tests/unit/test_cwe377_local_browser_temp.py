"""
PoC test for CWE-377: Insecure fixed-path temporary file write in LocalBrowser.

Demonstrates that LocalBrowser.initialize_async() writes CDP port config to
a hardcoded /tmp/chrome_cdp_ports.json path without symlink protection or
restrictive permissions, and uses a hardcoded world-readable user data dir.
"""

import inspect
import json
import os
import stat
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch


class TestCWE377LocalBrowserInsecureTempFile(unittest.TestCase):
    """Test that LocalBrowser does NOT write to predictable /tmp paths."""

    @classmethod
    def setUpClass(cls):
        try:
            import importlib
            cls.mod = importlib.import_module("agb.modules.browser.eval.local_page_agent")
        except ImportError:
            cls.mod = None

    def test_cdp_ports_path_not_hardcoded(self):
        """The CDP ports file path should not be the hardcoded /tmp/chrome_cdp_ports.json."""
        if self.mod is None:
            self.skipTest("Cannot import local_page_agent module")

        source = inspect.getsource(self.mod.LocalBrowser)
        # The fix should remove the hardcoded /tmp/chrome_cdp_ports.json path
        self.assertNotIn(
            '"/tmp/chrome_cdp_ports.json"',
            source,
            "CDP ports file should not use a hardcoded /tmp path (CWE-377 symlink attack vector)",
        )
        self.assertNotIn(
            "'/tmp/chrome_cdp_ports.json'",
            source,
            "CDP ports file should not use a hardcoded /tmp path (CWE-377 symlink attack vector)",
        )

    def test_user_data_dir_not_hardcoded_tmp(self):
        """The browser user data dir should not be hardcoded to /tmp/browser_user_data."""
        if self.mod is None:
            self.skipTest("Cannot import local_page_agent module")

        source = inspect.getsource(self.mod.LocalBrowser)
        self.assertNotIn(
            '"/tmp/browser_user_data"',
            source,
            "Browser user data dir should not use a hardcoded /tmp path (world-readable)",
        )
        self.assertNotIn(
            "'/tmp/browser_user_data'",
            source,
            "Browser user data dir should not use a hardcoded /tmp path (world-readable)",
        )

    def test_module_uses_tempfile(self):
        """
        After the fix, the module should use Python's tempfile module
        for secure temporary file/directory creation.
        """
        if self.mod is None:
            self.skipTest("Cannot import local_page_agent module")

        source = inspect.getsource(self.mod)
        self.assertIn(
            "tempfile",
            source,
            "Module should use tempfile for secure temporary file creation",
        )


if __name__ == "__main__":
    unittest.main()
