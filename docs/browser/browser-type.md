# Browser type selection

Choose between Chromium and Chrome browser engines for your automation sessions.

## What you'll do

Select the browser engine type (Chromium or Chrome) when initializing browser sessions on computer use images.

## Prerequisites

- `AGB_API_KEY`
- A valid **computer use** `image_id` (e.g. `agb-computer-use-1`)

> **Note:** The `browser_type` / `browserType` option is only available for **computer use images**. For standard browser images, Chromium is used by default.

## Quickstart

::: code-group

```python [Python]
from agb.modules.browser import BrowserOption

# Use Chrome (computer use images only)
option = BrowserOption(browser_type="chrome")
```

```typescript [TypeScript]
import type { BrowserOption } from "agbcloud-sdk";

// Use Chrome (computer use images only)
const option: BrowserOption = { browserType: "chrome" };
```

:::

## Common tasks

### Use Chrome browser

When you need specific Chrome features or want to match a particular browser environment:

::: code-group

```python [Python]
from agb.modules.browser import BrowserOption

chrome_option = BrowserOption(browser_type="chrome")
```

```typescript [TypeScript]
import type { BrowserOption } from "agbcloud-sdk";

const chromeOption: BrowserOption = { browserType: "chrome" };
```

:::

### Use Chromium browser (default)

Explicitly specify Chromium, or use the default:

::: code-group

```python [Python]
from agb.modules.browser import BrowserOption

# Explicitly use Chromium
chromium_option = BrowserOption(browser_type="chromium")

# Or use default (Chromium)
default_option = BrowserOption()
```

```typescript [TypeScript]
import type { BrowserOption } from "agbcloud-sdk";

// Explicitly use Chromium
const chromiumOption: BrowserOption = { browserType: "chromium" };

// Or use default (Chromium)
const defaultOption: BrowserOption = {};
```

:::

### Browser type comparison

| Browser | Description | Use Case |
|---------|-------------|----------|
| `chromium` | Open-source browser engine (default) | General automation, testing |
| `chrome` | Google Chrome with additional features | Chrome-specific features, production parity |

## Best practices

- Use Chromium (default) for most automation tasks.
- Choose Chrome when you need Chrome-specific APIs or behaviors.
- Only use `browser_type` with computer use images.

## Troubleshooting

### Browser type option ignored

- **Likely cause**: Using `browser_type` with a standard browser image.
- **Fix**: Ensure you're using a computer use image (e.g., `agb-computer-use-1`).

### Chrome not available

- **Likely cause**: Chrome is not installed in the image.
- **Fix**: Verify the image supports Chrome, or use `chromium` instead.

## Related

- Main guide: [`docs/browser/overview.md`](overview.md)
- Configuration: [Browser overview](overview.md)
- Computer use: [`docs/computer/overview.md`](../computer/overview.md)
