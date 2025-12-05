"""
Browser Type Selection Example

This example demonstrates how to select between Chrome and Chromium browsers
when using computer use images in AGB.

Features demonstrated:
- Chrome browser selection
- Chromium browser selection
- Default browser (None)
- Browser type verification
- Configuration comparison

Note: The browser_type option is only available for computer use images.
"""

import os
import asyncio
from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser.browser import BrowserOption, BrowserViewport
from playwright.async_api import async_playwright


async def test_browser_type(browser_type: str | None, description: str):
    """Test a specific browser type configuration."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"{'='*60}")

    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        raise RuntimeError("AGB_API_KEY environment variable not set")

    agb = AGB(api_key=api_key)

    # Create session with computer use image
    print("\n1. Creating session with computer use image...")
    params = CreateSessionParams(image_id="agb-linux-test-5")
    result = agb.create(params)

    if not result.success:
        raise RuntimeError(f"Failed to create session: {result.error_message}")

    session = result.session
    print(f"   ✓ Session created: {session.session_id}")

    try:
        # Initialize browser with specified type
        print(f"\n2. Initializing browser with type: {browser_type or 'default (None)'}")
        option = BrowserOption(
            browser_type=browser_type,
        )

        success = await session.browser.initialize_async(option)
        if not success:
            raise RuntimeError("Browser initialization failed")

        print(f"   ✓ Browser initialized successfully")

        # Get endpoint URL
        endpoint_url = session.browser.get_endpoint_url()
        print(f"\n3. CDP endpoint: {endpoint_url[:50]}...")

        # Connect Playwright and verify browser
        print("\n4. Connecting to browser via CDP...")
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            context = browser.contexts[0]
            page = await context.new_page()

            # Navigate to a page that shows browser info
            print("   ✓ Connected successfully")
            print("\n5. Verifying browser configuration...")

            await page.goto("https://www.whatismybrowser.com/")
            await page.wait_for_load_state("networkidle")

            # Get browser information
            user_agent = await page.evaluate("navigator.userAgent")
            viewport_width = await page.evaluate("window.innerWidth")
            viewport_height = await page.evaluate("window.innerHeight")

            print(f"\n   Browser Information:")
            print(f"   - User Agent: {user_agent[:80]}...")
            print(f"   - Viewport: {viewport_width} x {viewport_height}")
            print(f"   - Configured Type: {browser_type or 'default'}")

            # Check if Chrome or Chromium is in user agent
            if "Chrome" in user_agent:
                if "Chromium" in user_agent:
                    detected = "Chromium"
                else:
                    detected = "Chrome"
                print(f"   - Detected Browser: {detected}")

            await browser.close()

        print(f"\n   ✓ Test completed successfully for {description}")

    finally:
        print("\n6. Cleaning up...")
        session.delete()
        print("   ✓ Session deleted")


async def main():
    """Run browser type examples."""
    print("Browser Type Selection Example")
    print("=" * 60)
    print("\nThis example demonstrates browser type selection in AGB.")
    print("Note: browser_type is only available for computer use images.")

    # Test 1: Chrome browser
    await test_browser_type(
        browser_type="chrome",
        description="Chrome Browser (Google Chrome)"
    )

    await asyncio.sleep(2)  # Brief pause between tests

    # Test 2: Chromium browser
    await test_browser_type(
        browser_type="chromium",
        description="Chromium Browser (Open Source)"
    )

    await asyncio.sleep(2)  # Brief pause between tests

    # Test 3: Default (None)
    await test_browser_type(
        browser_type=None,
        description="Default Browser (Platform decides)"
    )

    print("\n" + "=" * 60)
    print("All browser type tests completed successfully!")
    print("=" * 60)

    # Summary
    print("\nSummary:")
    print("- Chrome: Use when you need Google Chrome specific features")
    print("- Chromium: Use for open-source, lighter resource usage")
    print("- Default (None): Let the platform choose the optimal browser")
    print("\nBest Practice: Use None unless you have a specific requirement")


async def quick_example():
    """Quick example showing the most common usage."""
    print("\n" + "=" * 60)
    print("Quick Example: Using Chrome Browser")
    print("=" * 60)

    api_key = os.getenv("AGB_API_KEY")
    agb = AGB(api_key=api_key)

    # Create session
    params = CreateSessionParams(image_id="agb-linux-test-5")
    result = agb.create(params)
    session = result.session

    try:
        # Simply specify browser_type in BrowserOption
        option = BrowserOption(browser_type="chrome")
        success = await session.browser.initialize_async(option)

        if success:
            print("✓ Chrome browser initialized successfully")

            # Get endpoint and use with Playwright
            endpoint_url = session.browser.get_endpoint_url()
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                page = await browser.contexts[0].new_page()

                await page.goto("https://example.com")
                title = await page.title()
                print(f"✓ Page title: {title}")

                await browser.close()
    finally:
        session.delete()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Browser Type Selection Example")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick example only"
    )

    args = parser.parse_args()

    if args.quick:
        asyncio.run(quick_example())
    else:
        asyncio.run(main())