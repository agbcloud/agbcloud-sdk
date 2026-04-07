#!/usr/bin/env python3
"""
Browser Network Debug Script

Diagnoses why Playwright page.goto() returns net::ERR_EMPTY_RESPONSE
when shell-level network (curl) works fine.

Checks:
- Shell-level HTTP/HTTPS connectivity
- SSL/TLS certificate chain
- Chrome browser network stack
- JavaScript fetch API
"""

import asyncio
import os
import sys
from dataclasses import dataclass, field
from typing import Dict

from playwright.async_api import async_playwright

from agb import AGB
from agb.modules.browser.browser import BrowserOption, BrowserViewport
from agb.session_params import CreateSessionParams


@dataclass
class DiagnosticReport:
    """Diagnostic report for browser network issues."""
    checks: Dict[str, Dict] = field(default_factory=dict)

    def add(self, name: str, passed: bool, details: str = ""):
        self.checks[name] = {"passed": passed, "details": details}

    def print_summary(self):
        print("\n" + "=" * 70)
        print("DIAGNOSTIC SUMMARY REPORT")
        print("=" * 70)

        # Categorize results
        passed = [(k, v) for k, v in self.checks.items() if v["passed"]]
        failed = [(k, v) for k, v in self.checks.items() if not v["passed"]]

        print(f"\n✅ PASSED: {len(passed)} / {len(self.checks)}")
        for name, info in passed:
            print(f"   • {name}")

        if failed:
            print(f"\n❌ FAILED: {len(failed)} / {len(self.checks)}")
            for name, info in failed:
                print(f"   • {name}")
                if info["details"]:
                    print(f"     └─ {info['details']}")

        # Root cause analysis
        print("\n" + "-" * 70)
        print("ROOT CAUSE ANALYSIS:")
        print("-" * 70)

        shell_http = self.checks.get(
            "Shell HTTP (curl)", {}).get("passed", False)
        shell_https = self.checks.get(
            "Shell HTTPS (curl)", {}).get("passed", False)
        shell_https_insecure = self.checks.get(
            "Shell HTTPS -k (insecure)", {}).get("passed", False)
        ca_certs = self.checks.get("CA Certificates", {}).get("passed", False)
        browser_http = self.checks.get("Browser HTTP", {}).get("passed", False)
        browser_https = self.checks.get(
            "Browser HTTPS", {}).get("passed", False)
        js_http = self.checks.get("JS fetch() HTTP", {}).get("passed", False)
        js_https = self.checks.get("JS fetch() HTTPS", {}).get("passed", False)

        if not shell_http:
            print("🔴 Basic network unreachable: sandbox cannot access external network")
            print("   → Check sandbox network configuration, firewall rules")
        elif shell_http and not shell_https and shell_https_insecure:
            print(
                "🟡 SSL certificate verification issue: shell-level HTTPS certificate verification failed")
            print(
                "   → Sandbox missing CA root certificates or incomplete certificate chain")
        elif shell_http and shell_https and not browser_http:
            print("🔴 Chrome network stack issue: Shell works but browser doesn't")
            print(
                "   → Chrome may have invalid proxy configuration or sandbox mode conflicts")
        elif browser_http and not browser_https:
            print("🟡 Chrome SSL issue: HTTP works but HTTPS doesn't")
            print(
                "   → Chrome cannot verify SSL certificates, check NSS certificate database")
            if not ca_certs:
                print("   → CA certificate directory is empty or does not exist")
        elif js_http and not js_https:
            print("🟡 JavaScript SSL issue: fetch HTTP works but HTTPS fails")
            print("   → Same root cause as Browser HTTPS issue: SSL certificates")
        elif all([shell_http, shell_https, browser_http, browser_https]):
            print("✅ All checks passed, network is normal")
        else:
            print("⚠️  Further analysis needed for specific failure items")

        print("\n" + "=" * 70)


async def main():
    """Debug browser network issues."""
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY not set")
        sys.exit(1)

    agb = AGB(api_key=api_key)
    print("AGB client initialized")

    report = DiagnosticReport()
    session = None

    try:
        # ========== [1] Create Session ==========
        print("\n" + "=" * 60)
        print("[1] Creating browser session...")
        print("=" * 60)
        params = CreateSessionParams(image_id="agb-browser-use-1")
        result = agb.create(params)

        if not result.success or not result.session:
            print(f"Failed: {result.error_message}")
            sys.exit(1)

        session = result.session
        print(f"Session: {session.session_id}")
        report.add("Session Creation", True)

        # ========== [2] Shell Network Tests ==========
        print("\n" + "=" * 60)
        print("[2] Shell Network Tests")
        print("=" * 60)

        # Test HTTP
        print("\n[2.1] Shell HTTP Test:")
        curl_http = session.command.execute(
            "curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10 http://httpbin.org/ip"
        )
        http_code = curl_http.output.strip() if curl_http.output else ""
        http_ok = http_code in ["200", "301", "302"]
        print(f"  http://httpbin.org/ip → {http_code}")
        report.add("Shell HTTP (curl)", http_ok, f"Status: {http_code}")

        # Test HTTPS
        print("\n[2.2] Shell HTTPS Test:")
        curl_https = session.command.execute(
            "curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10 https://httpbin.org/ip"
        )
        https_code = curl_https.output.strip() if curl_https.output else ""
        https_ok = https_code == "200"
        print(f"  https://httpbin.org/ip → {https_code}")
        report.add("Shell HTTPS (curl)", https_ok, f"Status: {https_code}")

        # Test HTTPS with -k (ignore cert)
        print("\n[2.3] Shell HTTPS -k (ignore cert):")
        curl_https_k = session.command.execute(
            "curl -s -k -o /dev/null -w '%{http_code}' --connect-timeout 10 https://httpbin.org/ip"
        )
        https_k_code = curl_https_k.output.strip() if curl_https_k.output else ""
        https_k_ok = https_k_code == "200"
        print(f"  https://httpbin.org/ip (insecure) → {https_k_code}")
        report.add("Shell HTTPS -k (insecure)",
                   https_k_ok, f"Status: {https_k_code}")

        # ========== [3] SSL Certificate Check ==========
        print("\n" + "=" * 60)
        print("[3] SSL/TLS Certificate Check")
        print("=" * 60)

        # Check CA certificates
        print("\n[3.1] CA Certificates:")
        ca_check = session.command.execute(
            "ls /etc/ssl/certs/ 2>/dev/null | wc -l"
        )
        ca_count = ca_check.output.strip() if ca_check.output else "0"
        try:
            ca_ok = int(ca_count) > 10
        except ValueError:
            ca_ok = False
        print(f"  /etc/ssl/certs/ file count: {ca_count}")
        report.add("CA Certificates", ca_ok, f"{ca_count} files")

        # Check NSS database (Chrome uses this)
        print("\n[3.2] NSS Certificate Database (Chrome):")
        nss_check = session.command.execute(
            "ls -la /etc/pki/nss-shared-db/ 2>/dev/null || ls -la ~/.pki/nssdb/ 2>/dev/null || echo 'NSS_NOT_FOUND'"
        )
        nss_output = nss_check.output.strip() if nss_check.output else ""
        nss_ok = "NSS_NOT_FOUND" not in nss_output and len(nss_output) > 0
        print(f"  {nss_output[:200] if nss_output else '(empty)'}")
        report.add("NSS Database", nss_ok, "Found" if nss_ok else "Not found")

        # Check SSL handshake detail
        print("\n[3.3] SSL Handshake Test:")
        ssl_test = session.command.execute(
            "curl -v --connect-timeout 10 https://httpbin.org/ip 2>&1 | grep -iE 'SSL|TLS|certificate|error' | head -5"
        )
        ssl_output = ssl_test.output.strip() if ssl_test.output else ""
        print(f"  {ssl_output[:300] if ssl_output else '(no SSL info)'}")

        # ========== [4] Initialize Browser ==========
        print("\n" + "=" * 60)
        print("[4] Initialize Browser (with --ignore-certificate-errors)")
        print("=" * 60)

        browser_option = BrowserOption(
            use_stealth=False,
            viewport=BrowserViewport(width=1280, height=720),
            cmd_args=[
                "--ignore-certificate-errors",
                "--ignore-ssl-errors=yes",
                "--ignore-certificate-errors-spki-list",
            ]
        )

        init_ok = await session.browser.initialize_async(browser_option)
        if not init_ok:
            print("Browser init failed")
            report.add("Browser Init", False, "Failed to initialize")
            report.print_summary()
            sys.exit(1)
        print("Browser initialized")
        report.add("Browser Init", True)

        # ========== [5] Chrome Process Info ==========
        print("\n" + "=" * 60)
        print("[5] Chrome Process Info")
        print("=" * 60)

        chrome_args = session.command.execute(
            "ps aux | grep -E 'chrome|chromium' | grep -v grep | tr ' ' '\\n' | grep -iE 'proxy|sandbox|dns|ssl|cert' | head -10"
        )
        args_output = chrome_args.output.strip() if chrome_args.output else "(none)"
        print(f"Chrome args (proxy/sandbox/dns/ssl):\n  {args_output}")

        # ========== [6] CDP Connection ==========
        print("\n" + "=" * 60)
        print("[6] CDP Connection")
        print("=" * 60)

        endpoint_url = session.browser.get_endpoint_url()
        if not endpoint_url:
            print("Failed to get CDP endpoint")
            report.add("CDP Connection", False, "No endpoint URL")
            report.print_summary()
            sys.exit(1)
        print(f"CDP: {endpoint_url[:80]}...")
        report.add("CDP Connection", True)

        await asyncio.sleep(2)

        # ========== [7] Playwright Tests ==========
        print("\n" + "=" * 60)
        print("[7] Playwright page.goto() Test")
        print("=" * 60)

        browser_http_ok = False
        browser_https_ok = False
        request_failures = []

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url, timeout=30000)
            print("Connected to browser")

            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = await context.new_page()
            page.on("requestfailed", lambda req: request_failures.append(
                f"{req.url}: {req.failure}"))

            # Test HTTP
            print("\n[7.1] Browser HTTP Test:")
            try:
                response = await page.goto("http://httpbin.org/ip", timeout=15000, wait_until="domcontentloaded")
                if response and response.ok:
                    print(f"  ✅ http://httpbin.org/ip → {response.status}")
                    browser_http_ok = True
                else:
                    status = response.status if response else "No response"
                    print(f"  ❌ http://httpbin.org/ip → {status}")
            except Exception as e:
                print(f"  ❌ http://httpbin.org/ip → {type(e).__name__}: {e}")
            report.add("Browser HTTP", browser_http_ok)

            # Test HTTPS
            print("\n[7.2] Browser HTTPS Test:")
            try:
                response = await page.goto("https://httpbin.org/ip", timeout=15000, wait_until="domcontentloaded")
                if response and response.ok:
                    print(f"  ✅ https://httpbin.org/ip → {response.status}")
                    browser_https_ok = True
                else:
                    status = response.status if response else "No response"
                    print(f"  ❌ https://httpbin.org/ip → {status}")
            except Exception as e:
                print(f"  ❌ https://httpbin.org/ip → {type(e).__name__}: {e}")
            report.add("Browser HTTPS", browser_https_ok,
                       request_failures[-1] if request_failures else "")

            # ========== [8] JavaScript fetch() Test ==========
            print("\n" + "=" * 60)
            print("[8] JavaScript fetch() Test")
            print("=" * 60)

            js_http_ok = False
            js_https_ok = False

            await page.goto("about:blank")

            # Test HTTP fetch
            print("\n[8.1] JS fetch() HTTP:")
            try:
                result = await page.evaluate('''
                    async () => {
                        try {
                            const res = await fetch("http://httpbin.org/ip");
                            const data = await res.json();
                            return { ok: res.ok, status: res.status, ip: data.origin };
                        } catch (e) {
                            return { error: e.message };
                        }
                    }
                ''')
                if result.get("ok"):
                    print(f"  ✅ fetch(http://httpbin.org/ip) → {result}")
                    js_http_ok = True
                else:
                    print(f"  ❌ fetch(http://httpbin.org/ip) → {result}")
            except Exception as e:
                print(f"  ❌ fetch error: {e}")
            report.add("JS fetch() HTTP", js_http_ok)

            # Test HTTPS fetch
            print("\n[8.2] JS fetch() HTTPS:")
            try:
                result = await page.evaluate('''
                    async () => {
                        try {
                            const res = await fetch("https://httpbin.org/ip");
                            const data = await res.json();
                            return { ok: res.ok, status: res.status, ip: data.origin };
                        } catch (e) {
                            return { error: e.message };
                        }
                    }
                ''')
                if result.get("ok"):
                    print(f"  ✅ fetch(https://httpbin.org/ip) → {result}")
                    js_https_ok = True
                else:
                    print(f"  ❌ fetch(https://httpbin.org/ip) → {result}")
            except Exception as e:
                print(f"  ❌ fetch error: {e}")
            report.add("JS fetch() HTTPS", js_https_ok)

            await browser.close()

        # ========== Print Summary Report ==========
        report.print_summary()

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        report.print_summary()
        sys.exit(1)

    finally:
        if session:
            print("\nCleaning up...")
            agb.delete(session)
            print("Done")


if __name__ == "__main__":
    asyncio.run(main())
