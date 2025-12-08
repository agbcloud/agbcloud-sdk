#!/usr/bin/env python3
"""
Browser Screenshot Capture Example

This example demonstrates browser screenshot functionality:
- Taking viewport screenshots (visible area only)
- Taking full-page screenshots (entire scrollable content)
- Customizing screenshot options (format, quality, timeout)
- Saving screenshots to local files
- Handling screenshot errors

Requirements:
- AGB_API_KEY environment variable set
- Playwright installed: pip install playwright
- Browser image: agb-browser-use-1
"""

import os
import asyncio
from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser import BrowserOption, BrowserViewport
from agb.exceptions import BrowserError
from playwright.async_api import async_playwright


async def main():
    """Main function demonstrating browser screenshot capabilities."""

    # Get API key from environment
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        raise ValueError("AGB_API_KEY environment variable not set")

    print("🚀 Starting browser screenshot example...")

    # Initialize AGB client
    agb = AGB(api_key=api_key)
    session = None
    browser_instance = None
    playwright = None

    try:
        # Create a session with browser support
        print("📦 Creating browser session...")
        params = CreateSessionParams(image_id="agb-browser-use-1")
        result = agb.create(params)

        if not result.success:
            raise RuntimeError(f"Failed to create session: {result.error_message}")

        session = result.session
        print(f"✅ Session created: {session.session_id}")

        # Configure browser options with custom viewport
        option = BrowserOption(
            use_stealth=True,
            viewport=BrowserViewport(width=1920, height=1080)
        )

        # Initialize browser
        print("🌐 Initializing browser...")
        success = await session.browser.initialize_async(option)
        if not success:
            raise RuntimeError("Browser initialization failed")

        print("✅ Browser initialized successfully")

        # Get CDP endpoint and connect Playwright
        endpoint_url = session.browser.get_endpoint_url()
        print(f"🔗 CDP endpoint: {endpoint_url}")

        playwright = await async_playwright().start()
        browser_instance = await playwright.chromium.connect_over_cdp(endpoint_url)
        context = browser_instance.contexts[0]
        page = await context.new_page()

        # Navigate to a test page
        test_url = "https://www.aliyun.com"
        print(f"\n📍 Navigating to: {test_url}")
        await page.goto(test_url, timeout=30000)
        await page.wait_for_load_state("domcontentloaded")
        print("✅ Page loaded successfully")

        # ============================================
        # Example 1: Basic Viewport Screenshot
        # ============================================
        print("\n📸 Example 1: Taking viewport screenshot...")
        screenshot_data = await session.browser.screenshot(page)

        # Save to file
        filename = "/tmp/screenshot_viewport.png"
        with open(filename, "wb") as f:
            f.write(screenshot_data)
        print(f"  ✅ Viewport screenshot saved: {filename}")
        print(f"  📊 Size: {len(screenshot_data):,} bytes")

        # ============================================
        # Example 2: Full Page Screenshot (Long Screenshot)
        # ============================================
        print("\n📸 Example 2: Taking full page screenshot (long screenshot)...")
        full_page_data = await session.browser.screenshot(page, full_page=True)

        filename = "/tmp/screenshot_full_page.png"
        with open(filename, "wb") as f:
            f.write(full_page_data)
        print(f"  ✅ Full page screenshot saved: {filename}")
        print(f"  📊 Size: {len(full_page_data):,} bytes")
        print("  📝 Note: Full page captures entire scrollable content")

        # ============================================
        # Example 3: JPEG Screenshot with Quality
        # ============================================
        print("\n📸 Example 3: Taking JPEG screenshot with quality setting...")
        jpeg_data = await session.browser.screenshot(
            page,
            full_page=False,
            type="jpeg",
            quality=80  # JPEG quality 0-100
        )

        filename = "/tmp/screenshot_quality.jpg"
        with open(filename, "wb") as f:
            f.write(jpeg_data)
        print(f"  ✅ JPEG screenshot saved: {filename}")
        print(f"  📊 Size: {len(jpeg_data):,} bytes")
        print("  📝 Note: JPEG with quality=80 produces smaller file size")

        # ============================================
        # Example 4: Screenshot with Custom Timeout
        # ============================================
        print("\n📸 Example 4: Taking screenshot with custom timeout...")
        timeout_data = await session.browser.screenshot(
            page,
            full_page=True,
            timeout=30000  # 30 seconds timeout
        )

        filename = "/tmp/screenshot_timeout.png"
        with open(filename, "wb") as f:
            f.write(timeout_data)
        print(f"  ✅ Screenshot with timeout saved: {filename}")
        print(f"  📊 Size: {len(timeout_data):,} bytes")

        # ============================================
        # Example 5: Multiple Page Screenshots
        # ============================================
        print("\n📸 Example 5: Taking screenshots of multiple pages...")
        urls = [
            "https://example.com",
            "https://httpbin.org/html"
        ]

        for i, url in enumerate(urls, 1):
            print(f"\n  📍 Navigating to: {url}")
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state("domcontentloaded")

            screenshot = await session.browser.screenshot(page, full_page=True)
            filename = f"/tmp/screenshot_multi_{i}.png"
            with open(filename, "wb") as f:
                f.write(screenshot)
            print(f"  ✅ Screenshot {i} saved: {filename}")
            print(f"  📊 Size: {len(screenshot):,} bytes")

        # ============================================
        # Example 6: Error Handling
        # ============================================
        print("\n📸 Example 6: Demonstrating error handling...")
        try:
            # Create uninitialized browser to test error handling
            from agb.modules.browser.browser import Browser
            uninitialized_browser = Browser(session)

            # This should raise BrowserError
            await uninitialized_browser.screenshot(page)
        except BrowserError as e:
            print(f"  ✅ Correctly caught BrowserError: {e}")
            print("  📝 Note: Browser must be initialized before taking screenshots")

        # Close browser connection
        await browser_instance.close()
        await playwright.stop()
        print("\n✅ Browser connection closed")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        if browser_instance:
            await browser_instance.close()
        if playwright:
            await playwright.stop()
        raise

    finally:
        # Clean up session
        if session:
            agb.delete(session)
            print("🧹 Session cleaned up")

    print("\n🎉 Screenshot example completed successfully!")
    print("\n📋 Summary of screenshots saved:")
    print("  - /tmp/screenshot_viewport.png (viewport only)")
    print("  - /tmp/screenshot_full_page.png (entire page)")
    print("  - /tmp/screenshot_quality.jpg (JPEG with quality)")
    print("  - /tmp/screenshot_timeout.png (with custom timeout)")
    print("  - /tmp/screenshot_multi_1.png (example.com)")
    print("  - /tmp/screenshot_multi_2.png (httpbin.org)")


if __name__ == "__main__":
    asyncio.run(main())
