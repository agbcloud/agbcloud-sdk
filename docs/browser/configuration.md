# Browser configuration

## What you’ll do

Configure the browser runtime using `BrowserOption`: stealth mode, user agent, viewport/screen, proxies, command args, and default navigation URL.

## Prerequisites

- `AGB_API_KEY`
- A valid browser `image_id` (e.g. `agb-browser-use-1`)

## Quickstart

```python
from agb.modules.browser import BrowserOption, BrowserViewport, BrowserScreen

option = BrowserOption(
    use_stealth=True,
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    viewport=BrowserViewport(width=1366, height=668),
    screen=BrowserScreen(width=1920, height=1080),
)
```

## Common tasks

### Viewport and screen settings

```python
from agb.modules.browser import BrowserOption, BrowserViewport, BrowserScreen

mobile_option = BrowserOption(
    viewport=BrowserViewport(width=375, height=667),
    screen=BrowserScreen(width=375, height=667),
    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
)

desktop_option = BrowserOption(
    viewport=BrowserViewport(width=1920, height=1080),
    screen=BrowserScreen(width=1920, height=1080),
)
```

### Proxy configuration

```python
from agb.modules.browser import BrowserOption, BrowserProxy

custom_proxy = BrowserProxy(
    proxy_type="custom",
    server="127.0.0.1:8080",
    username="proxy_user",
    password="proxy_pass",
)

option = BrowserOption(proxies=[custom_proxy])
```

Built-in proxy:

```python
from agb.modules.browser import BrowserProxy

polling_proxy = BrowserProxy(proxy_type="built-in", strategy="polling", pollsize=10)
restricted_proxy = BrowserProxy(proxy_type="built-in", strategy="restricted")
```

### Browser type selection (computer images only)

```python
from agb.modules.browser import BrowserOption

chrome_option = BrowserOption(browser_type="chrome")
chromium_option = BrowserOption(browser_type="chromium")
default_option = BrowserOption()
```

Note: Chrome is only supported for computer-use images.

### Custom command arguments

```python
from agb.modules.browser import BrowserOption

option = BrowserOption(
    cmd_args=[
        "--disable-features=PrivacySandboxSettings4",
        "--disable-notifications",
        "--no-first-run",
    ]
)
```

### Default navigation URL (debugging)

```python
from agb.modules.browser import BrowserOption

debug_option = BrowserOption(default_navigate_url="chrome://version/")
```

Recommendation: during browser initialization, prefer Chrome internal pages (e.g. `chrome://version/`, `chrome://settings/`) or extension pages. Navigating to internet URLs during initialization may cause timeouts.

## Best practices

- Keep initialization fast; avoid remote internet navigation during startup.
- Prefer setting stealth/fingerprint intentionally for sites that enforce bot detection.

## Troubleshooting

### Browser initialization times out

- **Likely cause**: the browser navigated to a slow/blocked URL during initialization.
- **Fix**: use internal pages via `default_navigate_url` and navigate after initialization.

## Related

- Main guide: [`docs/browser/overview.md`](overview.md)
- Fingerprint: [`docs/browser/fingerprint.md`](fingerprint.md)

