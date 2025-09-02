#!/usr/bin/env python3
"""
Natural Language Actions Example

This example demonstrates AI-powered browser control using natural language:
- Using natural language to describe actions
- Complex multi-step operations
- Handling dynamic page content
- Error recovery with AI assistance
"""

import os
import asyncio
from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser import BrowserOption, BrowserViewport, ActOptions
from agb.exceptions import BrowserError
from playwright.async_api import async_playwright


async def main():
    """Main function demonstrating natural language browser actions."""

    # Get API key from environment
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        raise ValueError("AGB_API_KEY environment variable not set")

    print("🤖 Starting natural language actions example...")

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

        # Configure browser with stealth mode
        option = BrowserOption(
            use_stealth=True,
            viewport=BrowserViewport(width=1366, height=768)
        )

        # Initialize browser
        print("🌐 Initializing browser...")
        success = await session.browser.initialize_async(option)
        if not success:
            raise RuntimeError("Browser initialization failed")

        print("✅ Browser initialized successfully")

        # Get CDP endpoint and connect Playwright
        endpoint_url = session.browser.get_endpoint_url()

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            page = await browser.new_page()

            # Example 1: Search on a more reliable site
            print("\n🔍 Example 1: Search and Navigation")
            try:
                await page.goto("https://httpbin.org/html", wait_until="domcontentloaded", timeout=15000)

                # Use natural language to interact with the page
                search_result = await session.browser.agent.act_async(page, ActOptions(
                    action="Find and click on any link on this page",
                    timeoutMS=15000
                ))

                print(f"  Link click result: {search_result.success}")
                if search_result.success:
                    print(f"  Message: {search_result.message}")
                    print(f"  Current URL: {page.url}")
                else:
                    print(f"  Error: {search_result.message}")

            except Exception as e:
                print(f"  ⚠️  Search example failed: {e}")
                print(f"  📍 Current URL: {page.url}")

            # Example 2: Form Interaction
            print("\n📝 Example 2: Form Interaction")
            await page.goto("https://httpbin.org/forms/post", wait_until="domcontentloaded", timeout=15000)

            # Fill out a form using natural language
            form_actions = [
                "Fill the 'custname' field with 'John Doe'",
                "Fill the 'custtel' field with '123-456-7890'",
                "Fill the 'custemail' field with 'john.doe@example.com'",
                "Select 'Large' from the size dropdown",
                "Check the 'Bacon' checkbox",
                "Fill the delivery instructions with 'Please ring the doorbell'"
            ]

            for action_text in form_actions:
                result = await session.browser.agent.act_async(page, ActOptions(
                    action=action_text,
                    timeoutMS=10000
                ))

                print(f"  Action: {action_text}")
                print(f"  Result: {'✅' if result.success else '❌'} {result.message}")

                if not result.success:
                    print(f"    Retrying with more specific instruction...")
                    # Retry with more specific instruction
                    retry_result = await session.browser.agent.act_async(page, ActOptions(
                        action=f"Find and {action_text.lower()}",
                        timeoutMS=15000,
                        dom_settle_timeout_ms=2000
                    ))
                    print(f"    Retry result: {'✅' if retry_result.success else '❌'} {retry_result.message}")

            # Submit the form
            submit_result = await session.browser.agent.act_async(page, ActOptions(
                action="Click the submit button to submit the form",
                timeoutMS=10000
            ))

            print(f"  Form submission: {'✅' if submit_result.success else '❌'} {submit_result.message}")

            # Example 3: Dynamic Content Interaction
            print("\n🔄 Example 3: Dynamic Content")
            await page.goto("https://quotes.toscrape.com", wait_until="domcontentloaded", timeout=15000)

            # Scroll and interact with dynamic content
            scroll_result = await session.browser.agent.act_async(page, ActOptions(
                action="Scroll down to see more quotes on the page",
                timeoutMS=10000
            ))

            print(f"  Scroll result: {'✅' if scroll_result.success else '❌'} {scroll_result.message}")

            # Click on a tag to filter quotes
            tag_result = await session.browser.agent.act_async(page, ActOptions(
                action="Click on any tag link to filter quotes by that tag",
                timeoutMS=10000
            ))

            print(f"  Tag click result: {'✅' if tag_result.success else '❌'} {tag_result.message}")
            if tag_result.success:
                print(f"  Current URL after tag click: {page.url}")

            # Example 4: Complex Multi-Step Workflow
            print("\n🔗 Example 4: Multi-Step Workflow")
            await page.goto("https://quotes.toscrape.com", wait_until="domcontentloaded", timeout=15000)

            # Multi-step workflow with error handling
            workflow_steps = [
                {
                    "action": "Find and click on the 'Next' button to go to the next page",
                    "description": "Navigate to next page"
                },
                {
                    "action": "Click on the author name of the first quote to view author details",
                    "description": "View author details"
                },
                {
                    "action": "Go back to the previous page using browser navigation",
                    "description": "Return to quotes page"
                }
            ]

            for i, step in enumerate(workflow_steps, 1):
                print(f"  Step {i}: {step['description']}")

                result = await session.browser.agent.act_async(page, ActOptions(
                    action=step['action'],
                    timeoutMS=15000,
                    dom_settle_timeout_ms=2000
                ))

                print(f"    Result: {'✅' if result.success else '❌'} {result.message}")

                if result.success:
                    print(f"    Current URL: {page.url}")
                    await asyncio.sleep(2)  # Wait between steps
                else:
                    print(f"    Step failed, continuing with next step...")

            # Example 5: Conditional Actions
            print("\n🤔 Example 5: Conditional Actions")
            await page.goto("https://httpbin.org/html", wait_until="domcontentloaded", timeout=15000)

            # Perform conditional actions based on page content
            conditional_result = await session.browser.agent.act_async(page, ActOptions(
                action="If there is a link that says 'Herman Melville', click on it. Otherwise, just scroll down the page",
                timeoutMS=15000
            ))

            print(f"  Conditional action result: {'✅' if conditional_result.success else '❌'} {conditional_result.message}")

            await browser.close()
            print("✅ Browser closed successfully")

    except BrowserError as e:
        print(f"❌ Browser error occurred: {e}")
        if browser:
            await browser.close()
    except Exception as e:
        print(f"❌ Unexpected error occurred: {e}")
        if browser:
            await browser.close()
        raise

    finally:
        # Clean up session
        if session:
            agb.delete(session)
            print("🧹 Session cleaned up")

    print("🎉 Natural language actions example completed!")


async def demonstrate_error_recovery():
    """Demonstrate error recovery patterns with natural language actions."""

    print("\n🔧 Demonstrating error recovery patterns...")

    # This would be part of a larger session, shown here for educational purposes
    # In practice, you would integrate this into your main workflow

    async def retry_action_with_fallback(agent, page, primary_action, fallback_action, max_retries=3):
        """Retry an action with a fallback if it fails."""

        for attempt in range(max_retries):
            try:
                action_text = primary_action if attempt == 0 else fallback_action
                result = await agent.act_async(page, ActOptions(
                    action=action_text,
                    timeoutMS=10000 + (attempt * 5000)  # Increase timeout with retries
                ))

                if result.success:
                    return result

                print(f"    Attempt {attempt + 1} failed: {result.message}")

            except Exception as e:
                print(f"    Attempt {attempt + 1} error: {e}")

            if attempt < max_retries - 1:
                await asyncio.sleep(2)  # Wait before retry

        raise BrowserError(f"Action failed after {max_retries} attempts")

    print("  This pattern can be used to make your automation more robust!")


if __name__ == "__main__":
    asyncio.run(main())