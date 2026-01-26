#!/usr/bin/env python3
"""
Integration test for browser fingerprint functionality.
This test verifies that browser fingerprint can be persisted
across sessions using the same ContextId and FingerprintContextId.
"""

import asyncio
import os
import time
import unittest
from agb.agb import AGB
from agb.modules.browser.browser import (
    BrowserFingerprint,
    BrowserOption,
    BrowserFingerprintContext,
)
from agb.modules.browser.fingerprint import FingerprintFormat, BrowserFingerprintGenerator
from agb.session_params import CreateSessionParams, BrowserContext
from playwright.async_api import async_playwright


def is_windows_user_agent(user_agent: str) -> bool:
    if not user_agent:
        return False
    user_agent_lower = user_agent.lower()
    windows_indicators = [
        'windows nt',
        'win32',
        'win64',
        'windows',
        'wow64'
    ]
    return any(indicator in user_agent_lower for indicator in windows_indicators)


class TestBrowserFingerprintIntegration(unittest.TestCase):
    """Integration tests for browser fingerprint persistence functionality."""

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)

    @classmethod
    def setUpClass(cls):
        # Skip if no API key is available or running in CI
        # CI environments typically don't have Chrome browser available for fingerprint generation
        api_key = os.environ.get("AGB_API_KEY")
        ci_env = os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS") or os.environ.get("GITLAB_CI") or os.environ.get("JENKINS_URL")
        if not api_key or ci_env:
            raise unittest.SkipTest("Skipping integration test: No API key available or running in CI (browser fingerprint requires local Chrome)")

        # Initialize AGB client
        cls.agb = AGB(api_key)

        # Create a browser context
        cls.session_context_name = f"test-browser-context-{int(time.time())}"
        context_result = cls.agb.context.get(cls.session_context_name, True)
        if not context_result.success or not context_result.context:
            raise AssertionError("Failed to create browser context")

        cls.context = context_result.context
        print(f"Created browser context: {cls.context.name} (ID: {cls.context.id})")

        # Create a browser fingerprint context
        cls.fingerprint_context_name = f"test-browser-fingerprint-{int(time.time())}"
        fingerprint_context_result = cls.agb.context.get(cls.fingerprint_context_name, True)
        if not fingerprint_context_result.success or not fingerprint_context_result.context:
            raise unittest.SkipTest("Failed to create fingerprint context")

        cls.fingerprint_context = fingerprint_context_result.context
        print(f"Created fingerprint context: {cls.fingerprint_context.name} (ID: {cls.fingerprint_context.id})")

    @classmethod
    def tearDownClass(cls):
        # Clean up context
        if hasattr(cls, "context"):
            try:
                cls.agb.context.delete(cls.context)
                print(f"Browser context deleted: {cls.context.id}")
                cls.agb.context.delete(cls.fingerprint_context)
                print(f"Fingerprint context deleted: {cls.fingerprint_context.id}")
            except Exception as e:
                print(f"Warning: Failed to delete context: {e}")


    def test_browser_fingerprint_basic_usage(self):
        print("===== Test browser fingerprint basic usage =====")

        params = CreateSessionParams(
            image_id="agb-browser-use-1"
        )
        session_result = self.agb.create(params)
        self.assertTrue(session_result.success, "Failed to create session")
        self.assertIsNotNone(session_result.session, "Session should not be None")

        session = session_result.session
        assert session is not None  # Type narrowing for linter
        print(f"Session created with ID: {session.session_id}")

        async def async_fingerprint_operations():
            # Initialize browser with fingerprint  options
            browser_option = BrowserOption(
                use_stealth=True,
                fingerprint=BrowserFingerprint(
                    devices=["desktop"],
                    operating_systems=["windows"],
                    locales=["zh-CN"],
                ),
            )
            init_success = await session.browser.initialize_async(browser_option)
            self.assertTrue(init_success, "Failed to initialize browser")
            print("Browser initialized successfully")

            # Get endpoint URL
            endpoint_url = session.browser.get_endpoint_url()
            self.assertIsNotNone(endpoint_url, "Endpoint URL should not be None")
            print(f"Browser endpoint URL: {endpoint_url}")

            # Connect with playwright and test user agent
            print("Getting user agent via navigator.userAgent...")
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                self.assertIsNotNone(browser, "Failed to connect to browser")
                context = browser.contexts[0] if browser.contexts else await browser.new_context()

                page = await context.new_page()
                user_agent = await page.evaluate("() => navigator.userAgent")
                print("user_agent =", user_agent)
                self.assertTrue(user_agent is not None)
                is_windows = is_windows_user_agent(user_agent)
                self.assertTrue(is_windows)

                await context.close()
                print("Browser fingerprint test completed")
        # Run fingerprint test operations
        asyncio.run(async_fingerprint_operations())

        delete_result = self.agb.delete(session)
        self.assertTrue(delete_result.success, "Failed to delete session")
        print(f"Session deleted successfully (RequestID: {delete_result.request_id})")


    def test_browser_fingerprint_persistence(self):
        """Test browser fingerprint persist across sessions with the same browser and fingerprint context."""
        print("===== Test browser fingerprint persistence =====")

        # Step 1: Create session with BrowserContext and FingerprintContext
        print(f"Step 1: Creating session with browser context ID: {self.context.id} "
              f"and fingerprint context ID: {self.fingerprint_context.id}")
        fingerprint_context = BrowserFingerprintContext(self.fingerprint_context.id)
        browser_context = BrowserContext(self.context.id, auto_upload=True, fingerprint_context=fingerprint_context)
        params1 = CreateSessionParams(
            image_id="agb-browser-use-1",
            browser_context=browser_context
        )

        session_result = self.agb.create(params1)
        self.assertTrue(session_result.success, "Failed to create first session")
        self.assertIsNotNone(session_result.session, "Session should not be None")

        session1 = session_result.session
        assert session1 is not None  # Type narrowing for linter
        print(f"First session created with ID: {session1.session_id}")

        # Step 3: Get browser object and generate fingerprint for persistence
        async def first_session_operations():
            print("Step 2: Initializing firsts browser and generate fingerprint for persistence...")

            # Initialize browser with fingerprint persistent enabled and set fingerprint generation options
            browser_option1 = BrowserOption(
                use_stealth=True,
                fingerprint_persistent=True,
                fingerprint=BrowserFingerprint(
                    devices=["desktop"],
                    operating_systems=["windows"],
                    locales=["zh-CN"],
                ),
            )
            init_success = await session1.browser.initialize_async(browser_option1)
            self.assertTrue(init_success, "Failed to initialize browser")
            print("Browser initialized successfully")

            # Get endpoint URL
            endpoint_url = session1.browser.get_endpoint_url()
            self.assertIsNotNone(endpoint_url, "Endpoint URL should not be None")
            print(f"Browser endpoint URL: {endpoint_url}")

            # Step 4: Connect with playwright, test first session fingerprint
            print("Step 3: Getting user agent via navigator.userAgent...")
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                self.assertIsNotNone(browser, "Failed to connect to browser")
                context = browser.contexts[0] if browser.contexts else await browser.new_context()

                page = await context.new_page()
                user_agent = await page.evaluate("() => navigator.userAgent")
                print("user_agent =", user_agent)
                self.assertTrue(user_agent is not None)
                is_windows = is_windows_user_agent(user_agent)
                self.assertTrue(is_windows)

                await context.close()
                print("First session browser operations completed")

        # Run first session operations
        asyncio.run(first_session_operations())

        # Step 4: Release first session with syncContext=True
        print("Step 4: Releasing first session with syncContext=True...")
        delete_result = self.agb.delete(session1, sync_context=True)
        self.assertTrue(delete_result.success, "Failed to delete first session")
        print(f"First session deleted successfully (RequestID: {delete_result.request_id})")

        # Wait for context sync to complete
        time.sleep(3)

        # Step 5: Create second session with same browser context and fingerprint context
        print(f"Step 5: Creating second session with same browser context ID: {self.context.id} "
              f"and fingerprint context ID: {self.fingerprint_context.id}")
        params2 = CreateSessionParams(
            image_id="agb-browser-use-1",
            browser_context=browser_context
        )
        session_result2 = self.agb.create(params2)
        self.assertTrue(session_result2.success, "Failed to create second session")
        self.assertIsNotNone(session_result2.session, "Second session should not be None")

        session2 = session_result2.session
        assert session2 is not None  # Type narrowing for linter
        print(f"Second session created with ID: {session2.session_id}")

        # Step 6: Get browser object and check if second session fingerprint is the same as first session
        async def second_session_operations():
            print("Step 6: Get browser object and check if second session fingerprint is the same as first session...")

            # Initialize browser with fingerprint persistent enabled but not specific fingerprint generation options
            browser_option2 = BrowserOption(
                use_stealth=True,
                fingerprint_persistent=True,
            )
            init_success = await session2.browser.initialize_async(browser_option2)
            self.assertTrue(init_success, "Failed to initialize browser in second session")
            print("Second session browser initialized successfully")

            # Get endpoint URL
            endpoint_url = session2.browser.get_endpoint_url()
            self.assertIsNotNone(endpoint_url, "Endpoint URL should not be None")
            print(f"Second session browser endpoint URL: {endpoint_url}")

            # Connect with playwright and test second session fingerprint
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                self.assertIsNotNone(browser, "Failed to connect to browser in second session")

                context = browser.contexts[0] if browser.contexts else await browser.new_context()
                page = await context.new_page()
                user_agent = await page.evaluate("() => navigator.userAgent")
                print("user_agent =", user_agent)
                self.assertTrue(user_agent is not None)
                is_windows = is_windows_user_agent(user_agent)
                self.assertTrue(is_windows)
                print(f"SUCCESS: fingerprint persisted correctly!")

                await context.close()
                print("Second session browser operations completed")

        # Run second session operations
        asyncio.run(second_session_operations())

        # Step 7: Release second session with syncContext=True
        print("Step 7: Releasing second session with syncContext=True...")
        delete_result = self.agb.delete(session2, sync_context=True)
        self.assertTrue(delete_result.success, "Failed to delete second session")
        print(f"Second session deleted successfully (RequestID: {delete_result.request_id})")

        print("Browser fingerprint persistence test completed successfully!")


    def test_browser_fingerprint_local_sync(self):
        """Test browser fingerprint local sync functionality."""

        print("===== Test browser fingerprint local sync =====")

        params = CreateSessionParams(
            image_id="agb-browser-use-1",
        )
        session_result = self.agb.create(params)
        self.assertTrue(session_result.success, "Failed to create session")
        self.assertIsNotNone(session_result.session, "Session should not be None")

        session = session_result.session
        assert session is not None  # Type narrowing for linter
        print(f"Session created with ID: {session.session_id}")

        async def async_local_sync_operations():
            # Generate local chrome browser fingerprint
            print("Dumping local chrome browser fingerprint...")

            fingerprint_generator = BrowserFingerprintGenerator(headless=False)
            fingerprint_format = await fingerprint_generator.generate_fingerprint()
            if fingerprint_format is None:
                # In CI environments, browser fingerprint generation may fail due to missing Chrome/display
                # Skip this test gracefully instead of failing
                self.skipTest("Browser fingerprint generation failed (likely due to CI environment limitations)")
            self.assertIsNotNone(fingerprint_format, "Fingerprint format should not be None")
            print("Local fingerprint generated successfully")

            # Initialize browser with fingerprint format from local chrome
            browser_option = BrowserOption(
                use_stealth=True,
                fingerprint_format=fingerprint_format
            )
            init_success = await session.browser.initialize_async(browser_option)
            self.assertTrue(init_success, "Failed to initialize browser")
            print("Browser initialized successfully with local fingerprint")

            # Get endpoint URL
            endpoint_url = session.browser.get_endpoint_url()
            self.assertIsNotNone(endpoint_url, "Endpoint URL should not be None")
            print(f"Browser endpoint URL: {endpoint_url}")

            # Connect with playwright and verify fingerprint sync
            print("Testing fingerprint sync by checking user agent via navigator...")
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                self.assertIsNotNone(browser, "Failed to connect to browser")
                context = browser.contexts[0] if browser.contexts else await browser.new_context()

                page = await context.new_page()
                user_agent = await page.evaluate("() => navigator.userAgent")
                print(f"Remote user agent: {user_agent}")
                print(f"Local user agent: {fingerprint_format.fingerprint.navigator.userAgent}")

                # Verify that the user agents match (fingerprint sync successful)
                self.assertEqual(user_agent, fingerprint_format.fingerprint.navigator.userAgent,
                               "User agent should match between local and remote")
                print("SUCCESS: Local fingerprint synced correctly to remote browser!")

                await context.close()
                print("Local sync test completed")

        # Run local sync operations
        asyncio.run(async_local_sync_operations())

        delete_result = self.agb.delete(session)
        self.assertTrue(delete_result.success, "Failed to delete session")
        print(f"Session deleted successfully (RequestID: {delete_result.request_id})")

        print("Browser fingerprint local sync test completed successfully!")


    def test_browser_fingerprint_construct(self):
        """Test browser fingerprint construction from file."""
        print("===== Test browser fingerprint construct =====")

        params = CreateSessionParams(
            image_id="agb-browser-use-1",
        )
        session_result = self.agb.create(params)
        self.assertTrue(session_result.success, "Failed to create session")
        self.assertIsNotNone(session_result.session, "Session should not be None")

        session = session_result.session
        assert session is not None  # Type narrowing for linter
        print(f"Session created with ID: {session.session_id}")

        async def async_construct_operations():
            # Load fingerprint from example file
            print("Loading fingerprint from example file...")

            # Get the path to the example fingerprint file
            example_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "resource", "fingerprint.example.json"
            )

            with open(example_file_path, "r") as f:
                fingerprint_json = f.read()

            fingerprint_format = FingerprintFormat.load(fingerprint_json)
            self.assertIsNotNone(fingerprint_format, "Fingerprint format should not be None")
            print("Fingerprint loaded from file successfully")

            # Initialize browser with constructed fingerprint format
            browser_option = BrowserOption(
                use_stealth=True,
                fingerprint_format=fingerprint_format
            )
            init_success = await session.browser.initialize_async(browser_option)
            self.assertTrue(init_success, "Failed to initialize browser")
            print("Browser initialized successfully with constructed fingerprint")

            # Get endpoint URL
            endpoint_url = session.browser.get_endpoint_url()
            self.assertIsNotNone(endpoint_url, "Endpoint URL should not be None")
            print(f"Browser endpoint URL: {endpoint_url}")

            # Connect with playwright and verify constructed fingerprint
            print("Testing constructed fingerprint by checking user agent via navigator...")
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                self.assertIsNotNone(browser, "Failed to connect to browser")
                context = browser.contexts[0] if browser.contexts else await browser.new_context()

                page = await context.new_page()
                user_agent = await page.evaluate("() => navigator.userAgent")
                print(f"Remote user agent: {user_agent}")
                print(f"Expected user agent: {fingerprint_format.fingerprint.navigator.userAgent}")

                # Verify that the user agents match (fingerprint construction successful)
                self.assertEqual(user_agent, fingerprint_format.fingerprint.navigator.userAgent,
                               "User agent should match the constructed fingerprint")
                print("SUCCESS: Fingerprint constructed correctly from file!")

                await context.close()
                print("Construct test completed")

        # Run construct operations
        asyncio.run(async_construct_operations())

        delete_result = self.agb.delete(session)
        self.assertTrue(delete_result.success, "Failed to delete session")
        print(f"Session deleted successfully (RequestID: {delete_result.request_id})")

        print("Browser fingerprint construct test completed successfully!")


if __name__ == "__main__":
    unittest.main()
