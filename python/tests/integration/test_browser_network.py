#!/usr/bin/env python3
"""
Browser Network Connectivity Test

This script verifies that the sandbox browser can access the internet.
Tests page.goto and returns detailed network response info.
"""

import asyncio
import os
import sys

from playwright.async_api import async_playwright

from agb import AGB
from agb.modules.browser.browser import BrowserOption, BrowserViewport
from agb.session_params import CreateSessionParams


async def main():
    """Test browser network connectivity in sandbox."""
    # Get credentials from environment
    api_key = os.environ.get("AGB_API_KEY")
    endpoint = os.environ.get("AGB_ENDPOINT")

    if not api_key:
        print("Error: AGB_API_KEY environment variable not set")
        sys.exit(1)

    print(f"Using endpoint: {endpoint or 'default'}")

    # Create AGB instance
    agb = AGB(api_key=api_key)
    print("AGB client initialized")

    session = None
    try:
        # Create browser session
        print("Creating browser session...")
        params = CreateSessionParams(image_id="agb-browser-use-1")
        result = agb.create(params)

        if not result.success or not result.session:
            print(f"Failed to create session: {result.error_message}")
            sys.exit(1)

        session = result.session
        print(f"Session created: {session.session_id}")

        # Initialize browser
        print("Initializing browser...")
        browser_option = BrowserOption(
            use_stealth=True,
            viewport=BrowserViewport(width=1280, height=720),
        )

        init_ok = await session.browser.initialize_async(browser_option)
        if not init_ok:
            print("Failed to initialize browser")
            sys.exit(1)

        print("Browser initialized successfully")

        # Get CDP endpoint
        endpoint_url = session.browser.get_endpoint_url()
        if not endpoint_url:
            print("Failed to get browser endpoint URL")
            sys.exit(1)

        print(f"CDP endpoint: {endpoint_url[:80]}...")

        # ========== Network Diagnostics (before browser test) ==========
        print("\n" + "=" * 60)
        print("Network Diagnostics (Shell Commands)")
        print("=" * 60)

        # Test 1: DNS resolution
        print("\n[1] DNS Resolution Test:")
        dns_result = session.command.execute(
            "nslookup www.baidu.com 2>&1 | head -10")
        print(dns_result.output if dns_result.output else "No output")

        # Test 2: curl test (bypass SSL issues)
        print("\n[2] curl Test (HTTP):")
        curl_result = session.command.execute(
            "curl -v --connect-timeout 10 http://www.baidu.com 2>&1 | head -30")
        print(curl_result.output if curl_result.output else "No output")

        # Test 3: curl HTTPS
        print("\n[3] curl Test (HTTPS):")
        curl_https = session.command.execute(
            "curl -v --connect-timeout 10 https://www.baidu.com 2>&1 | head -30")
        print(curl_https.output if curl_https.output else "No output")

        # Test 4: Check proxy settings
        print("\n[4] Proxy Environment Variables:")
        proxy_result = session.command.execute("env | grep -i proxy")
        print(proxy_result.output if proxy_result.output else "(No proxy env vars set)")

        # Test 5: Check network interfaces
        print("\n[5] Network Interfaces:")
        net_result = session.command.execute(
            "ip addr show 2>/dev/null || ifconfig 2>/dev/null | head -20")
        print(net_result.output if net_result.output else "No output")

        # Test 6: Route table
        print("\n[6] Default Route:")
        route_result = session.command.execute(
            "ip route show default 2>/dev/null || netstat -rn 2>/dev/null | head -5")
        print(route_result.output if route_result.output else "No output")

        print("\n" + "=" * 60)
        print("End of Network Diagnostics")
        print("=" * 60)

        # Wait for browser ready
        await asyncio.sleep(3)

        # Connect with Playwright
        print("\nConnecting to browser via Playwright...")
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(
                endpoint_url,
                timeout=60000
            )
            print("Connected to browser")

            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = await context.new_page()

            # Test URLs
            test_urls = [
                ("https://httpbin.org/ip", "HTTPBin IP"),
                ("https://www.baidu.com", "Baidu"),
                ("https://www.google.com", "Google"),
            ]

            print("\n" + "=" * 60)
            print("Network Connectivity Test Results")
            print("=" * 60)

            all_passed = True
            for url, name in test_urls:
                print(f"\n[{name}] {url}")
                try:
                    response = await page.goto(url, timeout=30000)
                    if response:
                        status = response.status
                        ok = response.ok
                        print(f"  Status: {status}")
                        print(f"  OK: {ok}")

                        # For httpbin, print the response body
                        if "httpbin" in url:
                            try:
                                body = await page.content()
                                # Extract IP from response
                                import re
                                ip_match = re.search(
                                    r'"origin":\s*"([^"]+)"', body)
                                if ip_match:
                                    print(f"  Sandbox IP: {ip_match.group(1)}")
                            except Exception:
                                pass

                        if ok:
                            print(f"  ✅ PASS")
                        else:
                            print(f"  ⚠️ Response not OK")
                            all_passed = False
                    else:
                        print(f"  ❌ FAIL - No response")
                        all_passed = False

                except Exception as e:
                    print(f"  ❌ FAIL - {type(e).__name__}: {e}")
                    all_passed = False

            print("\n" + "=" * 60)
            if all_passed:
                print("✅ All network tests PASSED - Sandbox network is accessible")
            else:
                print("⚠️ Some network tests FAILED")
            print("=" * 60)

            await browser.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # Clean up
        if session:
            print("\nCleaning up session...")
            delete_result = agb.delete(session)
            if delete_result.success:
                print(f"Session deleted: {delete_result.request_id}")
            else:
                print(
                    f"Failed to delete session: {delete_result.error_message}")

    print("\nTest completed!")


if __name__ == "__main__":
    asyncio.run(main())
