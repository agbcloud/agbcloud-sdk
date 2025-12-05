"""
Example demonstrating Browser Fingerprint basic usage with AGB SDK.

This example shows how to use browser fingerprint to avoid detection by anti-bot services.
It will generate a random, realistic browser fingerprint and make the browser behave more like a real user.

This example will:
1. Create AIBrowser session with random fingerprint and simulate a Windows desktop browser.
2. Use playwright to connect to AIBrowser instance through CDP protocol
3. Verify user agent and navigator properties
"""

import os
import asyncio

from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser.browser import BrowserOption, BrowserFingerprint

from playwright.async_api import async_playwright


async def main():
    """Main function demonstrating browser fingerprint basic usage."""
    # Get API key from environment variable
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY environment variable not set")
        return

    # Initialize AGB client
    print("Initializing AGB client...")
    agb = AGB(api_key=api_key)

    # Create a session
    print("Creating a new session...")
    params = CreateSessionParams(
        image_id="agb-browser-use-1",
    )
    session_result = agb.create(params)

    if session_result.success:
        session = session_result.session
        print(f"Session created with ID: {session.session_id}")

        """Create browser fingerprint option
        - devices: desktop or mobile
        - operating_systems: windows, macos, linux, android, ios

        You can specify one or multiple values for each parameter.
        But if you specify devices as desktop and operating_systems as android/ios,
        the fingerprint feature will not work.
        """
        browser_fingerprint = BrowserFingerprint(
            devices=["desktop"],
            operating_systems=["windows"],
            locales=["zh-CN", "zh"]
        )

        # Create browser option with stealth mode and fingerprint option limit.
        # This will help to avoid detection by anti-bot services. It will
        # generate a random, realistic browser fingerprint and make the browser
        # behave more like a real user.
        browser_option = BrowserOption(
            use_stealth=True,
            fingerprint=browser_fingerprint
        )

        if await session.browser.initialize_async(browser_option):
            endpoint_url = session.browser.get_endpoint_url()
            print("endpoint_url =", endpoint_url)

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                context = browser.contexts[0]
                page = await context.new_page()

                # Check user agent.
                print("\n--- Check User Agent ---")
                await page.goto("https://httpbin.org/user-agent", timeout=120000)

                response = await page.evaluate("() => JSON.parse(document.body.textContent)")
                user_agent = response.get("user-agent", "")
                print(f"User Agent: {user_agent}")

                # Check navigator properties.
                print("\n--- Check Navigator Properties ---")
                nav_info = await page.evaluate("""
                    () => ({
                        platform: navigator.platform,
                        language: navigator.language,
                        languages: navigator.languages,
                        webdriver: navigator.webdriver
                    })
                """)
                print(f"Platform: {nav_info.get('platform')}")
                print(f"Language: {nav_info.get('language')}")
                print(f"Languages: {nav_info.get('languages')}")
                print(f"WebDriver: {nav_info.get('webdriver')}")

                await page.wait_for_timeout(3000)
                await browser.close()

        # Clean up session
        agb.delete(session)

if __name__ == "__main__":
    asyncio.run(main())