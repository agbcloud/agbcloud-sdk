"""
Example demonstrating AIBrowser capabilities with AGB SDK.
This example shows how to use AIBrowser to solve captcha automatically, including:
- Create AIBrowser session
- Use playwright to connect to AIBrowser instance through CDP protocol
- Set solve_captchas to be True and goto tongcheng website
- We will encounter a captcha and we will solve it automatically.
"""

import os
import time
import asyncio
import base64

from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser import BrowserOption, BrowserViewport

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
    params = CreateSessionParams(
        image_id="agb-browser-use-1",  # Updated image ID for AGB
    )
    session_result = agb.create(params)

    if session_result.success:
        session = session_result.session
        print(f"Session created with ID: {session.session_id}")

        # Configure browser options
        browser_option = BrowserOption(solve_captchas=True)

        # Initialize browser
        print("🌐 Initializing browser...")
        success = await session.browser.initialize_async(browser_option)
        if not success:
            print("❌ Browser initialization failed")
            return

        print("✅ Browser initialized successfully")
        endpoint_url = session.browser.get_endpoint_url()
        print(f"🔗 CDP endpoint: {endpoint_url}")

        browser = None
        try:
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                context = browser.contexts[0]
                page = await context.new_page()
                print("🌐 Navigating to tongcheng site...")
                url = "https://passport.ly.com/Passport/GetPassword"
                await page.goto(url, wait_until="domcontentloaded")

                # Use selector to locate input field
                input_element = await page.wait_for_selector("#name_in", timeout=10000)
                print("Found login name input field: #name_in")

                # Clear input field and enter phone number
                phone_number = "15011556760"
                print(f"Entering phone number: {phone_number}")

                await input_element.click()
                await input_element.fill("")  # Clear input field
                await input_element.type(phone_number)
                print("Waiting for captcha")

                # Wait a moment to ensure input is complete
                await asyncio.sleep(1)

                print("Clicking next step button...")
                await page.click("#next_step1")

                # Listen for captcha processing messages
                captcha_solving_started = False
                captcha_solving_finished = False

                # Listen for console messages
                def handle_console(msg):
                    nonlocal captcha_solving_started, captcha_solving_finished
                    print(f"🔍 Received console message: {msg.text}")
                    if msg.text == "wuying-captcha-solving-started":
                        captcha_solving_started = True
                        print("🎯 Setting captchaSolvingStarted = true")
                        # Use asyncio.create_task for async execution
                        asyncio.create_task(
                            page.evaluate(
                                "window.captchaSolvingStarted = true; window.captchaSolvingFinished = false;"
                            )
                        )
                    elif msg.text == "wuying-captcha-solving-finished":
                        captcha_solving_finished = True
                        print("✅ Setting captchaSolvingFinished = true")
                        # Use asyncio.create_task for async execution
                        asyncio.create_task(
                            page.evaluate("window.captchaSolvingFinished = true;")
                        )

                page.on("console", handle_console)

                # Wait 1 second first, then check if captcha processing has started
                try:
                    await asyncio.sleep(1)
                    await page.wait_for_function(
                        "() => window.captchaSolvingStarted === true", timeout=1000
                    )
                    print(
                        "🎯 Detected captcha processing started, waiting for completion..."
                    )

                    # If start is detected, wait for completion (max 30 seconds)
                    try:
                        await page.wait_for_function(
                            "() => window.captchaSolvingFinished === true",
                            timeout=30000,
                        )
                        print("✅ Captcha processing completed")
                    except:
                        print("⚠️ Captcha processing timeout, may still be in progress")

                except:
                    print("⏭️ No captcha processing detected, continuing execution")

                await asyncio.sleep(2)
                print("Test completed")

                # Keep browser open for a while to observe results
                await asyncio.sleep(5)

                # Take screenshot and print base64, can be pasted directly into Chrome address bar
                try:
                    screenshot_bytes = await page.screenshot(full_page=False)
                    b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                    print("page_screenshot_base64 = data:image/png;base64,", b64)
                except Exception as e:
                    print("screenshot failed:", e)

                await browser.close()
                print("✅ Browser closed successfully")

        except Exception as e:
            print(f"❌ Error occurred: {e}")
            if browser:
                await browser.close()
            raise

    else:
        print(f"❌ Failed to create session: {session_result.error_message}")
        return

    # Clean up session
    if session_result.success:
        agb.delete(session)
        print("🧹 Session cleaned up")

    print("🎉 Captcha solving example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
