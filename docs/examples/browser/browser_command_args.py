"""
Example demonstrating Browser Launch with Custom Command Arguments and
go to Default Navigation URL with AGB SDK.

This example shows how to configure browser with custom command arguments
and go to default navigation URL:
- Create AIBrowser session with custom command arguments and go to default navigation URL
- Use playwright to connect to AIBrowser instance through CDP protocol
- Verify the browser navigated to the default URL
- Test custom command arguments effects
"""

import os
import asyncio

from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser.browser import BrowserOption, BrowserFingerprint
from playwright.async_api import async_playwright


async def main():
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
    params = CreateSessionParams(image_id="agb-browser-use-1")
    session_result = agb.create(params)

    if session_result.success:
        session = session_result.session
        print(f"Session created with ID: {session.session_id}")

        # Create browser option with user defined cmd args and default navigate url
        browser_option = BrowserOption(
            cmd_args=["--disable-features=PrivacySandboxSettings4"],
            default_navigate_url="chrome://version/",
        )

        print("Browser configuration:")
        print("- Command arguments:", browser_option.cmd_args)
        print("- Default navigate URL:", browser_option.default_navigate_url)

        if await session.browser.initialize_async(browser_option):
            print("Browser initialized successfully")

            # Get browser endpoint URL
            endpoint_url = session.browser.get_endpoint_url()
            print(f"endpoint_url = {endpoint_url}")

            # Use Playwright to connect and validate
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                context = browser.contexts[0]
                page = context.pages[0]

                try:
                    # Check if browser navigated to default URL
                    print("\n--- Check Default Navigation ---")
                    await asyncio.sleep(2)  # Wait for navigation
                    current_url = page.url
                    print(f"Current URL: {current_url}")

                    if "chrome://version/" in current_url:
                        print("✓ Browser successfully navigated to default URL")
                    else:
                        print("✗ Browser did not navigate to default URL")

                    # Test command arguments effect by checking Chrome version page
                    if "chrome://version/" in current_url:
                        print("\n--- Check Chrome Version Info ---")
                        version_info = await page.evaluate(
                            """
                            () => {
                                const versionElement = document.querySelector('#version');
                                const commandLineElement = document.querySelector('#command_line');
                                return {
                                    version: versionElement ? versionElement.textContent : 'Not found',
                                    commandLine: commandLineElement ? commandLineElement.textContent : 'Not found'
                                };
                            }
                        """
                        )

                        print(f"Chrome Version: {version_info['version']}")
                        print(f"Command Line: {version_info['commandLine']}")

                        if (
                            "--disable-features=PrivacySandboxSettings4"
                            in version_info["commandLine"]
                        ):
                            print("✓ Custom command argument found in browser")
                        else:
                            print("✗ Custom command argument not found in browser")

                    await asyncio.sleep(3)
                finally:
                    await browser.close()
                    session.browser.destroy()
        else:
            print("Failed to initialize browser")

        # Clean up session
        agb.delete(session)
    else:
        print("Failed to create session", session_result.error_message)


if __name__ == "__main__":
    asyncio.run(main())
