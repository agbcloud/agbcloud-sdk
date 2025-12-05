#!/usr/bin/env python3
"""
Integration test for browser fingerprint persistence functionality.
This test verifies that browser fingerprint can be persisted
across sessions using the same ContextId and FingerprintContextId.
"""

import asyncio
import os
import time
import unittest
from agb import AGB
from agb.session_params import CreateSessionParams, BrowserContext
from agb.modules.browser.browser import BrowserOption, BrowserFingerprint, BrowserFingerprintContext
from playwright.async_api import async_playwright

# Global variables for persistent context and fingerprint context
persistent_context = None
persistent_fingerprint_context = None

def get_test_api_key():
    """Get API key for testing"""
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        raise unittest.SkipTest("AGB_API_KEY environment variable not set")
    return api_key


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


def run_as_first_time():
    """Run as first time"""
    print("="*20)
    print("Run as first time")
    print("="*20)
    global persistent_context, persistent_fingerprint_context
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY environment variable not set")
        return

    agb = AGB(api_key)

    # Create a browser context for first time
    session_context_name = f"test-browser-context-{int(time.time())}"
    context_result = agb.context.get(session_context_name, True)
    if not context_result.success or not context_result.context:
        print("Failed to create browser context")
        return

    persistent_context = context_result.context
    print(f"Created browser context: {persistent_context.name} (ID: {persistent_context.id})")

    # Create a browser fingerprint context for first time
    fingerprint_context_name = f"test-browser-fingerprint-{int(time.time())}"
    fingerprint_context_result = agb.context.get(fingerprint_context_name, True)
    if not fingerprint_context_result.success or not fingerprint_context_result.context:
        print("Failed to create fingerprint context")
        return

    persistent_fingerprint_context = fingerprint_context_result.context
    print(f"Created fingerprint context: {persistent_fingerprint_context.name} (ID: {persistent_fingerprint_context.id})")


    # Create session with BrowserContext and FingerprintContext
    print(f"Creating session with browser context ID: {persistent_context.id} "
            f"and fingerprint context ID: {persistent_fingerprint_context.id}")
    fingerprint_context = BrowserFingerprintContext(persistent_fingerprint_context.id)
    browser_context = BrowserContext(persistent_context.id, auto_upload=True, fingerprint_context=fingerprint_context)
    params = CreateSessionParams(
        image_id="agb-browser-use-1",
        browser_context=browser_context
    )

    session_result = agb.create(params)
    if not session_result.success or not session_result.session:
        print(f"Failed to create first session: {session_result.error_message}")
        return

    session = session_result.session
    print(f"First session created with ID: {session.session_id}")

    # Get browser object and generate fingerprint for persistence
    async def first_session_operations():
        # Initialize browser with fingerprint persistent enabled and set fingerprint generation options
        browser_option = BrowserOption(
            use_stealth=True,
            fingerprint_persistent=True,
            fingerprint=BrowserFingerprint(
                devices=["desktop"],
                operating_systems=["windows"],
                locales=["zh-CN"],
            ),
        )
        init_success = await session.browser.initialize_async(browser_option)
        if not init_success:
            print("Failed to initialize browser")
            return
        print("First session browser initialized successfully")

        # Get endpoint URL
        endpoint_url = session.browser.get_endpoint_url()
        if not endpoint_url:
            print("Failed to get browser endpoint URL")
            return
        print(f"First session browser endpoint URL: {endpoint_url}")

        # Connect with playwright, test first session fingerprint
        print("Opening https://httpbin.org/user-agent and test user agent...")
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            context = browser.contexts[0] if browser.contexts else await browser.new_context()

            page = await context.new_page()
            await page.goto("https://httpbin.org/user-agent", timeout=120000)
            response = await page.evaluate("() => JSON.parse(document.body.textContent)")
            user_agent = response["user-agent"]
            print("user_agent =", user_agent)
            is_windows = is_windows_user_agent(user_agent)
            if not is_windows:
                print("Failed to get windows user agent")
                return

            await context.close()
            print("First session browser fingerprint check completed")

    # Run first session operations
    asyncio.run(first_session_operations())

    # Delete first session with syncContext=True
    print("Deleting first session with syncContext=True...")
    delete_result = agb.delete(session, sync_context=True)
    print(f"First session deleted successfully (RequestID: {delete_result.request_id})")


def run_as_second_time():
    """Run as second time"""
    print("="*20)
    print("Run as second time")
    print("="*20)
    global persistent_context, persistent_fingerprint_context
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY environment variable not set")
        return

    agb = AGB(api_key)

    # Create second session with same browser context and fingerprint context
    print(f"Creating second session with same browser context ID: {persistent_context.id} "
            f"and fingerprint context ID: {persistent_fingerprint_context.id}")
    fingerprint_context = BrowserFingerprintContext(persistent_fingerprint_context.id)
    browser_context = BrowserContext(persistent_context.id, auto_upload=True, fingerprint_context=fingerprint_context)
    params = CreateSessionParams(
        image_id="agb-browser-use-1",
        browser_context=browser_context
    )
    session_result = agb.create(params)
    if not session_result.success or not session_result.session:
        print(f"Failed to create second session: {session_result.error_message}")
        return

    session = session_result.session
    assert session is not None  # Type narrowing for linter
    print(f"Second session created with ID: {session.session_id}")

    # Get browser object and check if second session fingerprint is the same as first session
    async def second_session_operations():
        # Initialize browser with fingerprint persistent enabled but not specific fingerprint generation options
        browser_option = BrowserOption(
            use_stealth=True,
            fingerprint_persistent=True,
        )
        init_success = await session.browser.initialize_async(browser_option)
        if not init_success:
            print("Failed to initialize browser in second session")
            return
        print("Second session browser initialized successfully")

        # Get endpoint URL
        endpoint_url = session.browser.get_endpoint_url()
        if not endpoint_url:
            print("Failed to get browser endpoint URL in second session")
            return
        print(f"Second session browser endpoint URL: {endpoint_url}")

        # Connect with playwright and test second session fingerprint
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = await context.new_page()
            await page.goto("https://httpbin.org/user-agent", timeout=120000)
            response = await page.evaluate("() => JSON.parse(document.body.textContent)")
            user_agent = response["user-agent"]
            print("user_agent =", user_agent)
            is_windows = is_windows_user_agent(user_agent)
            if not is_windows:
                print("Failed to get windows user agent in second session")
                return
            print(f"SUCCESS: fingerprint persisted correctly!")

            await context.close()
            print("Second session browser fingerprint check completed")

    # Run second session operations
    asyncio.run(second_session_operations())

    # Delete second session with syncContext=True
    print("Deleting second session with syncContext=True...")
    delete_result = agb.delete(session, sync_context=True)
    print(f"Second session deleted successfully (RequestID: {delete_result.request_id})")


def main():
    """Test browser fingerprint persist across sessions with the same browser and fingerprint context."""
    run_as_first_time()
    time.sleep(3)
    run_as_second_time()

if __name__ == "__main__":
    main()
