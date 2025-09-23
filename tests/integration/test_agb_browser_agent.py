#!/usr/bin/env python3
"""
Browser Cookie Persistence Example

This example demonstrates how to test browser cookie functionality
across multiple sessions. It shows the complete workflow of:
1. Creating a session
2. Setting cookies in the browser
3. Deleting the session
4. Creating a new session
5. Verifying that cookies persist across sessions
"""

import asyncio
import os
import time

from playwright.async_api import async_playwright

from agb import AGB
from agb.config import Config
from agb.modules.browser.browser import BrowserOption, BrowserViewport
from agb.session_params import CreateSessionParams


async def main():
    """Demonstrate browser cookie persistence."""
    # Get API key from environment
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY environment variable not set")
        return

    # Initialize AGB client
    config = Config(
        endpoint=os.getenv("AGB_ENDPOINT", "sdk-api.agb.cloud"), timeout_ms=60000
    )

    # Create AGB instance
    agb = AGB(api_key=api_key, cfg=config)
    print("AGB client initialized")

    try:
        # Step 1: Create first session
        print("Step 1: Creating first session.")
        params = CreateSessionParams(
            image_id="agb-browser-use-1",  # Browser image ID
        )

        session_result = agb.create(params)
        if not session_result.success or not session_result.session:
            print(f"Failed to create first session: {session_result.error_message}")
            return

        session1 = session_result.session
        print(f"First session created with ID: {session1.session_id}")

        # Step 2: Initialize browser and set cookies
        print("Step 2: Initializing browser and setting test cookies...")

        browser_option = BrowserOption(
            use_stealth=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport=BrowserViewport(width=1366, height=768),
        )
        # Initialize browser
        init_success = await session1.browser.initialize_async(browser_option)
        if not init_success:
            print("Failed to initialize browser")
            return

        print("Browser initialized successfully")

        # Get endpoint URL
        endpoint_url = session1.browser.get_endpoint_url()
        if not endpoint_url:
            print("Failed to get browser endpoint URL")
            return

        print(f"Browser endpoint URL: {endpoint_url}")

        # Test data
        test_url = "https://www.github.com"
        test_domain = "github.com"

        # Define test cookies
        test_cookies = [
            {
                "name": "demo_cookie_1",
                "value": "demo_value_1",
                "domain": test_domain,
                "path": "/",
                "httpOnly": False,
                "secure": False,
                "expires": int(time.time()) + 3600,  # 1 hour from now
            },
            {
                "name": "demo_cookie_2",
                "value": "demo_value_2",
                "domain": test_domain,
                "path": "/",
                "httpOnly": False,
                "secure": False,
                "expires": int(time.time()) + 3600,  # 1 hour from now
            },
        ]

        # Connect with Playwright and set cookies
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            context_p = (
                browser.contexts[0] if browser.contexts else await browser.new_context()
            )
            page = await context_p.new_page()

            # Navigate to test URL first (required before setting cookies)
            await page.goto(test_url)
            print(f"Navigated to {test_url}")
            await page.wait_for_timeout(2000)

            # Add test cookies
            await context_p.add_cookies(test_cookies)
            print(f"Added {len(test_cookies)} test cookies")

            # Verify cookies were set
            cookies = await context_p.cookies()
            cookie_dict = {
                cookie.get("name", ""): cookie.get("value", "") for cookie in cookies
            }
            print(f"Total cookies in first session: {len(cookies)}")

            # Check our test cookies
            for test_cookie in test_cookies:
                cookie_name = test_cookie["name"]
                if cookie_name in cookie_dict:
                    print(
                        f"✓ Test cookie '{cookie_name}' set successfully: {cookie_dict[cookie_name]}"
                    )
                else:
                    print(f"✗ Test cookie '{cookie_name}' not found")

            await browser.close()
            print("First session browser operations completed")

        # Step 4: Delete first session
        print("Step 4: Deleting first session...")
        delete_result = agb.delete(session1)

        if not delete_result.success:
            print(f"Failed to delete first session: {delete_result.error_message}")
            return

        print(
            f"First session deleted successfully (RequestID: {delete_result.request_id})"
        )

        # Wait a moment for cleanup
        print("Waiting for cleanup to complete...")
        time.sleep(3)

        # Step 5: Create second session
        print("Step 5: Creating second session...")
        session_result2 = agb.create(params)

        if not session_result2.success or not session_result2.session:
            print(f"Failed to create second session: {session_result2.error_message}")
            return

        session2 = session_result2.session
        print(f"Second session created with ID: {session2.session_id}")

        # Step 6: Verify cookie persistence
        print("Step 6: Verifying cookie persistence in second session...")

        # Initialize browser in second session
        init_success2 = await session2.browser.initialize_async(browser_option)
        if not init_success2:
            print("Failed to initialize browser in second session")
            return

        print("Second session browser initialized successfully")

        # Get endpoint URL for second session
        endpoint_url2 = session2.browser.get_endpoint_url()
        if not endpoint_url2:
            print("Failed to get browser endpoint URL for second session")
            return

        print(f"Second session browser endpoint URL: {endpoint_url2}")

        # Check cookies in second session
        async with async_playwright() as p:
            browser2 = await p.chromium.connect_over_cdp(endpoint_url2)
            context2 = (
                browser2.contexts[0]
                if browser2.contexts
                else await browser2.new_context()
            )

            # Read cookies directly from context (without opening any page)
            cookies2 = await context2.cookies()
            cookie_dict2 = {
                cookie.get("name", ""): cookie.get("value", "") for cookie in cookies2
            }

            print(f"Total cookies in second session: {len(cookies2)}")

            # Check if our test cookies persisted
            expected_cookie_names = {"demo_cookie_1", "demo_cookie_2"}
            found_cookie_names = set(cookie_dict2.keys())

            print("Checking cookie persistence...")
            missing_cookies = expected_cookie_names - found_cookie_names

            if missing_cookies:
                print(f"✗ Missing test cookies: {missing_cookies}")
                print("Cookie persistence test FAILED")
            else:
                # Verify cookie values
                all_values_match = True
                for test_cookie in test_cookies:
                    cookie_name = test_cookie["name"]
                    expected_value = test_cookie["value"]
                    actual_value = cookie_dict2.get(cookie_name, "")

                    if expected_value == actual_value:
                        print(
                            f"✓ Cookie '{cookie_name}' persisted correctly: {actual_value}"
                        )
                    else:
                        print(
                            f"✗ Cookie '{cookie_name}' value mismatch. Expected: {expected_value}, Actual: {actual_value}"
                        )
                        all_values_match = False

                if all_values_match:
                    print(
                        "🎉 Cookie persistence test PASSED! All cookies persisted correctly across sessions."
                    )
                else:
                    print("Cookie persistence test FAILED due to value mismatches")

            await browser2.close()
            print("Second session browser operations completed")

        # Step 7: Clean up second session
        print("Step 7: Cleaning up second session...")
        delete_result2 = agb.delete(session2)

        if delete_result2.success:
            print(
                f"Second session deleted successfully (RequestID: {delete_result2.request_id})"
            )
        else:
            print(f"Failed to delete second session: {delete_result2.error_message}")

    except Exception as e:
        print(f"Error during demo: {e}")

    finally:
        # Clean up completed
        print("Cleanup completed")

    print("\nBrowser Cookie Persistence Demo completed!")


if __name__ == "__main__":
    asyncio.run(main())
