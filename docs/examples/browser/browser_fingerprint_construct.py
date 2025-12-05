"""
Example demonstrating Browser Fingerprint local sync feature with AGB SDK.

This example shows how to sync local browser fingerprint to remote browser fingerprint.
BrowserFingerprintGenerator has ability to dump local installed chrome browser fingerprint,
and then you can sync it to remote browser fingerprint by using BrowserOption.fingerprint_format.

This example will:
1. Generate local chrome browser fingerprint by BrowserFingerprintGenerator
2. Sync local browser fingerprint to remote browser fingerprint
3. Verify remote browser fingerprint
4. Clean up session
"""

import os
import asyncio

from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser.browser import BrowserOption
from agb.modules.browser.fingerprint import BrowserFingerprintGenerator, FingerprintFormat

from playwright.async_api import async_playwright

async def generate_fingerprint_by_file() -> FingerprintFormat:
    """Generate fingerprint by file."""
    with open(os.path.join(os.path.dirname(__file__), "../../../resource/fingerprint.example.json"), "r") as f:
        fingerprint_format = FingerprintFormat.load(f.read())
    return fingerprint_format

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

        # You can generate fingerprint by file or construct FingerprintFormat by yourself totally.
        fingerprint_format = await generate_fingerprint_by_file()

        # Create browser option with fingerprint format.
        # Fingerprint format is dumped from file by generate_fingerprint_by_file()
        # automatically, you can use it to sync to remote browser fingerprint.
        browser_option = BrowserOption(
            use_stealth=True,
            fingerprint_format=fingerprint_format
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
                assert user_agent == fingerprint_format.fingerprint.navigator.userAgent
                print("User Agent constructed correctly")

                await page.wait_for_timeout(3000)
                await browser.close()

        # Clean up session
        agb.delete(session)

if __name__ == "__main__":
    asyncio.run(main())