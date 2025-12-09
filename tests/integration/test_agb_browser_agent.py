#!/usr/bin/env python3
"""
Browser Cookie Persistence Example

This example demonstrates how to use Browser Context to persist cookies
across multiple sessions. It shows the complete workflow of:
1. Creating a session with Browser Context
2. Setting cookies in the browser
3. Deleting the session with context synchronization
4. Creating a new session with the same Browser Context
5. Verifying that cookies persist across sessions
"""

import asyncio
import os
import sys
import time

from playwright.async_api import async_playwright

from agb import AGB
from agb.config import Config, BROWSER_DATA_PATH
from agb.modules.browser.browser import BrowserOption, BrowserViewport
from agb.session_params import CreateSessionParams, BrowserContext


async def main():
    """Demonstrate browser context cookie persistence."""
    # Get API key from environment
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY environment variable not set")
        sys.exit(1)

    # Initialize AGB client
    config = Config(
        endpoint=os.getenv("AGB_ENDPOINT", "sdk-api.agb.cloud"), timeout_ms=60000
    )

    # Create AGB instance
    agb = AGB(api_key=api_key, cfg=config)
    print("AGB client initialized")

    # Create a unique context name for this demo
    context_name = f"browser-cookie-demo-{int(time.time())}"

    try:
        # Step 1: Create or get a persistent context for browser data
        print(f"Step 1: Creating context '{context_name}'...")
        context_result = agb.context.get(context_name, create=True)

        if not context_result.success or not context_result.context:
            print(f"Failed to create context: {context_result.error_message}")
            sys.exit(1)

        context = context_result.context
        print(f"Context created with ID: {context.id}")

        # Step 2: Create first session with Browser Context
        print("Step 2: Creating first session with Browser Context...")

        params = CreateSessionParams(
            image_id="agb-browser-use-1",  # Browser image ID
            browser_context=BrowserContext(
                context_id=context.id,
                auto_upload=True,
            )
        )

        session_result = agb.create(params)
        if not session_result.success or not session_result.session:
            print(f"Failed to create first session: {session_result.error_message}")
            sys.exit(1)

        session1 = session_result.session
        print(f"First session created with ID: {session1.session_id}")

        # Test data
        test_url = "https://www.baidu.com"
        test_domain = "baidu.com"

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

        # Step 3: Initialize browser and set cookies
        print("Step 3: Initializing browser and setting test cookies...")

        browser_option = BrowserOption(
            use_stealth=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport=BrowserViewport(width=1366, height=768),
        )

        # Initialize browser
        init_success = await session1.browser.initialize_async(browser_option)
        if not init_success:
            print("Failed to initialize browser")
            sys.exit(1)

        print("Browser initialized successfully")

        # Get endpoint URL
        endpoint_url = session1.browser.get_endpoint_url()
        if not endpoint_url:
            print("Failed to get browser endpoint URL")
            sys.exit(1)

        print(f"Browser endpoint URL: {endpoint_url}")

        # Connect with Playwright and set cookies
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            context_p = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = await context_p.new_page()

            # Navigate to test URL first (required before setting cookies)
            await page.goto(test_url)
            print(f"Navigated to {test_url}")
            await page.wait_for_timeout(2000)

            # Add test cookies
            await context_p.add_cookies(test_cookies)  # type: ignore
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

            # Wait for browser to save cookies to file
            print("Waiting for browser to save cookies to file...")
            await asyncio.sleep(20)
            print("Wait completed")

        # Step 4: Manually sync context before deleting session
        print("Step 4: Manually syncing context...")
        sync_result = await session1.context.sync()
        if not sync_result.success:
            print(f"Failed to sync context: {sync_result.error_message}")
            sys.exit(1)
        print(f"Context sync completed successfully (RequestID: {sync_result.request_id})")

        # Wait a bit for sync to complete
        print("Waiting for sync to complete...")
        await asyncio.sleep(2)

        # Step 5: Check context files for cookie file
        print("Step 5: Checking context files for cookie file...")

        # List files in the browser data path
        # First, try listing the root browser data path
        list_result = agb.context.list_files(
            context_id=context.id,
            parent_folder_path=BROWSER_DATA_PATH,
            page_number=1,
            page_size=100
        )

        if not list_result.success:
            print(f"Failed to list context files: {list_result.error_message}")
            sys.exit(1)

        print(f"Found {len(list_result.entries)} files/directories in context at {BROWSER_DATA_PATH}:")
        cookie_file_found = False
        cookie_journal_file_found = False
        local_state_found = False

        # Check for cookie files - they should be in Default/Cookies or Default/Cookies-journal
        for file_entry in list_result.entries:
            file_path = file_entry.file_path
            file_name = getattr(file_entry, 'file_name', file_path.split('/')[-1])
            file_size = getattr(file_entry, 'size', 0)
            print(f"  - {file_path} (Size: {file_size} bytes, Name: {file_name})")

            # Normalize path for comparison
            normalized_path = file_path.lower().replace('\\', '/')

            # Check for cookie file (should be in Default/Cookies)
            if "/default/cookies" in normalized_path and "journal" not in normalized_path:
                cookie_file_found = True
                print(f"  ✓ Cookie file found: {file_path}")
            # Check for cookie journal file
            elif "/default/cookies-journal" in normalized_path or "/default/cookies_journal" in normalized_path:
                cookie_journal_file_found = True
                print(f"  ✓ Cookie journal file found: {file_path}")
            # Check for Local State file
            elif "/local state" in normalized_path or file_name.lower() == "local state":
                local_state_found = True
                print(f"  ✓ Local State file found: {file_path}")

        # Also try listing the Default directory if it exists
        default_path = f"{BROWSER_DATA_PATH}/Default"
        print(f"\nChecking Default directory: {default_path}")
        default_list_result = agb.context.list_files(
            context_id=context.id,
            parent_folder_path=default_path,
            page_number=1,
            page_size=100
        )

        if default_list_result.success and default_list_result.entries:
            print(f"Found {len(default_list_result.entries)} files in Default directory:")
            for file_entry in default_list_result.entries:
                file_path = file_entry.file_path
                file_name = getattr(file_entry, 'file_name', file_path.split('/')[-1])
                file_size = getattr(file_entry, 'size', 0)
                print(f"  - {file_path} (Size: {file_size} bytes, Name: {file_name})")

                normalized_path = file_path.lower().replace('\\', '/')
                if "/default/cookies" in normalized_path and "journal" not in normalized_path:
                    cookie_file_found = True
                    print(f"  ✓ Cookie file found: {file_path}")
                elif "/default/cookies-journal" in normalized_path or "/default/cookies_journal" in normalized_path:
                    cookie_journal_file_found = True
                    print(f"  ✓ Cookie journal file found: {file_path}")

        # Summary
        print("\n=== Context File Check Summary ===")
        if cookie_file_found:
            print("✅ Cookie file found in context!")
        else:
            print("⚠️  Cookie file not found in context.")
            print("    Expected path: /tmp/agb_browser_data/Default/Cookies")
            print("    This may indicate a sync issue, but continuing with test...")

        if cookie_journal_file_found:
            print("✅ Cookie journal file found in context!")
        else:
            print("ℹ️  Cookie journal file not found (this is optional)")

        if local_state_found:
            print("✅ Local State file found in context!")

        # Step 6: Delete first session with context synchronization
        print("Step 6: Deleting first session with context synchronization...")
        delete_result = agb.delete(session1, sync_context=True)

        if not delete_result.success:
            print(f"Failed to delete first session: {delete_result.error_message}")
            sys.exit(1)

        print(
            f"First session deleted successfully (RequestID: {delete_result.request_id})"
        )

        # Wait for context sync to complete
        print("Waiting for session to be released...")
        time.sleep(30)

        # Step 7: Create second session with same Browser Context
        print("Step 7: Creating second session with same Browser Context...")
        session_result2 = agb.create(params)

        if not session_result2.success or not session_result2.session:
            print(f"Failed to create second session: {session_result2.error_message}")
            sys.exit(1)

        session2 = session_result2.session
        print(f"Second session created with ID: {session2.session_id}")

        # Step 8: Verify cookie persistence
        print("Step 8: Verifying cookie persistence in second session...")

        # Initialize browser in second session
        init_success2 = await session2.browser.initialize_async(browser_option)
        if not init_success2:
            print("Failed to initialize browser in second session")
            sys.exit(1)

        print("Second session browser initialized successfully")

        # Get endpoint URL for second session
        endpoint_url2 = session2.browser.get_endpoint_url()
        if not endpoint_url2:
            print("Failed to get browser endpoint URL for second session")
            sys.exit(1)

        print(f"Second session browser endpoint URL: {endpoint_url2}")

        # Check cookies in second session
        async with async_playwright() as p2:
            browser2 = await p2.chromium.connect_over_cdp(endpoint_url2)
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

            print("Checking test cookie persistence...")
            missing_cookies = expected_cookie_names - found_cookie_names

            if missing_cookies:
                print(f"✗ Missing test cookies: {missing_cookies}")
                print("Cookie persistence test FAILED")
                test_passed = False
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
                    test_passed = True
                else:
                    print("Cookie persistence test FAILED due to value mismatches")
                    test_passed = False

            await browser2.close()
            print("Second session browser operations completed")

        # Step 9: Clean up second session
        print("Step 9: Cleaning up second session...")
        delete_result2 = agb.delete(session2)
        print("Waiting for session to be released...")
        time.sleep(30)

        if delete_result2.success:
            print(
                f"Second session deleted successfully (RequestID: {delete_result2.request_id})"
            )
        else:
            print(f"Failed to delete second session: {delete_result2.error_message}")

        if not test_passed:
            sys.exit(1)

    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # Clean up context
        if 'context' in locals() and context:
            try:
                agb.context.delete(context)
                print(f"Context '{context_name}' deleted")
            except Exception as e:
                print(f"Warning: Failed to delete context: {e}")

    print("\nBrowser Context Cookie Persistence Demo completed!")


if __name__ == "__main__":
    asyncio.run(main())
