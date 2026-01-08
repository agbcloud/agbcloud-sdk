# Browser automation

## What you’ll do

Create a browser session in AGB, connect via CDP (Playwright/Puppeteer), and automate pages using either code-driven automation or AGB’s AI Agent (Act/Observe/Extract).

## Prerequisites

- `AGB_API_KEY`
- A valid browser `image_id` (e.g. `agb-browser-use-1`)
- Python 3.10+ (for the examples below)
- Playwright installed locally (to connect over CDP):
  - `pip install playwright && python -m playwright install chromium`

## Quickstart

Minimal runnable example: create a browser session, initialize browser, connect via CDP, open a page, then clean up.

```python
import os
import asyncio
from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser import BrowserOption
from playwright.async_api import async_playwright


async def main() -> None:
    agb = AGB(api_key=os.getenv("AGB_API_KEY"))
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
            await page.goto("https://example.com")
            print("Title:", await page.title())
            await browser.close()
    finally:
        agb.delete(session)


if __name__ == "__main__":
    asyncio.run(main())
```

## Common tasks

This topic is large. The detailed content has been split into smaller pages:

- Browser configuration (`BrowserOption`, proxy, viewport, cmd args): [`docs/browser/configuration.md`](configuration.md)
- AI Agent operations (Act/Observe/Extract): [`docs/browser/agent.md`](agent.md)
- Advanced features (stealth/fingerprint/extensions): [`docs/browser/advanced.md`](advanced.md)

## Best practices

See: [`docs/browser/best-practices.md`](best-practices.md)

## Troubleshooting

See: [`docs/browser/troubleshooting.md`](troubleshooting.md)

## Related

- API reference: [`docs/api-reference/capabilities/browser.md`](../api-reference/capabilities/browser.md)
- Fingerprint: [`docs/browser/fingerprint.md`](fingerprint.md)
- Extensions: [`docs/browser/extension.md`](extension.md)
- Examples: [`docs/examples/browser/README.md`](../examples/browser/README.md)
