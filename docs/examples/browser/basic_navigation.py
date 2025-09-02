#!/usr/bin/env python3
"""
Basic Browser Navigation Example

This example demonstrates fundamental browser operations:
- Creating and initializing a browser session
- Navigating to web pages
- Getting page information (title, URL, etc.)
- Basic Playwright integration
"""

import os
import asyncio
from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser import BrowserOption, BrowserViewport
from playwright.async_api import async_playwright


async def main():
    """Main function demonstrating basic browser navigation."""

    # Get API key from environment
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        raise ValueError("AGB_API_KEY environment variable not set")

    print("🚀 Starting basic browser navigation example...")

    # Initialize AGB client
    agb = AGB(api_key=api_key)
    session = None
    browser = None

    try:
        # Create a session with browser support
        print("📦 Creating browser session...")
        params = CreateSessionParams(image_id="agb-browser-use-1")
        result = agb.create(params)

        if not result.success:
            raise RuntimeError(f"Failed to create session: {result.error_message}")

        session = result.session
        print(f"✅ Session created: {session.session_id}")

        # Configure browser options
        option = BrowserOption(
            use_stealth=True,
            viewport=BrowserViewport(width=1366, height=768),
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
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

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            page = await browser.new_page()

            # Navigate to different websites
            websites = [
                "https://example.com",
                "https://httpbin.org/html",
                "https://quotes.toscrape.com"
            ]

            for url in websites:
                print(f"\n📍 Navigating to: {url}")

                # Navigate to the page
                await page.goto(url, wait_until="networkidle")

                # Get page information
                title = await page.title()
                current_url = page.url

                print(f"  📄 Title: {title}")
                print(f"  🔗 URL: {current_url}")

                # Get page content info
                body_text = await page.evaluate("document.body.innerText")
                text_length = len(body_text.strip())
                print(f"  📝 Content length: {text_length} characters")

                # Check for common elements
                has_forms = await page.evaluate("document.forms.length > 0")
                has_images = await page.evaluate("document.images.length > 0")
                has_links = await page.evaluate("document.links.length > 0")

                print(f"  🔍 Page analysis:")
                print(f"    - Has forms: {has_forms}")
                print(f"    - Has images: {has_images}")
                print(f"    - Has links: {has_links}")

                # Wait a moment before next navigation
                await asyncio.sleep(2)

            # Demonstrate browser navigation methods
            print(f"\n🔄 Testing browser navigation...")

            try:
                # Go back with minimal wait - just wait for navigation to start
                await page.go_back(timeout=10000, wait_until="commit")  # 10 seconds, wait for navigation to commit
                print(f"  ⬅️  Went back to: {page.url}")

                # Go forward with minimal wait
                await page.go_forward(timeout=10000, wait_until="commit")  # 10 seconds, wait for navigation to commit
                print(f"  ➡️  Went forward to: {page.url}")

            except Exception as nav_error:
                print(f"  ⚠️  Navigation test failed: {nav_error}")
                print(f"  📍 Current URL: {page.url}")

            try:
                # Reload page with shorter timeout
                await page.reload(timeout=10000)  # 10 seconds timeout
                print(f"  🔄 Reloaded page: {page.url}")

                # Take a screenshot
                screenshot_path = "/tmp/navigation_example.png"
                await page.screenshot(path=screenshot_path)
                print(f"  📸 Screenshot saved to: {screenshot_path}")

            except Exception as reload_error:
                print(f"  ⚠️  Reload/screenshot failed: {reload_error}")
                print(f"  📍 Current URL: {page.url}")

            await browser.close()
            print("✅ Browser closed successfully")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        if browser:
            await browser.close()
        raise

    finally:
        # Clean up session
        if session:
            agb.delete(session)
            print("🧹 Session cleaned up")

    print("🎉 Basic navigation example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())