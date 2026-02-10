#!/usr/bin/env python3
"""
Integration test: create session with browser image, initialize browser async,
connect via Playwright CDP, open a page and print title, then cleanup.

Run directly:
    python tests/integration/test_browser_playwright_connect.py

Or with pytest (requires AGB_API_KEY in env or .env):
    pytest tests/integration/test_browser_playwright_connect.py -v -s
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from agb import AGB
from agb.modules.browser import BrowserOption
from agb.session_params import CreateSessionParams

load_dotenv()


async def main() -> None:
    agb = AGB()
    create_result = agb.create(CreateSessionParams(image_id="agb-browser-use-1"))
    if not create_result.success:
        raise SystemExit(f"Session creation failed: {create_result.error_message}")

    session = create_result.session
    try:
        ok = await session.browser.initialize_async(BrowserOption())
        if not ok:
            raise SystemExit("Browser initialization failed")

        endpoint_url = session.browser.get_endpoint_url()
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            page = await browser.new_page()
            await page.goto("https://agb.cloud")
            print("Title:", await page.title())
            await browser.close()
    finally:
        agb.delete(session)


def test_browser_playwright_connect():
    """Run the browser + Playwright CDP connect flow (integration test)."""
    if not os.environ.get("AGB_API_KEY"):
        raise SystemExit(
            "AGB_API_KEY not set. Set it in env or .env to run this test."
        )
    asyncio.run(main())


if __name__ == "__main__":
    if not os.environ.get("AGB_API_KEY"):
        print("AGB_API_KEY not set. Set it in env or .env to run this test.")
        sys.exit(1)
    asyncio.run(main())
