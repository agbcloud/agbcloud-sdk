# Troubleshooting

## What you’ll do

Diagnose common browser automation failures: initialization, CDP connection, and agent action errors.

## Prerequisites

- `AGB_API_KEY`
- A valid browser `image_id` (e.g. `agb-browser-use-1`)

## Quickstart

Start by verifying session creation and browser initialization:

```python
create_result = agb.create(CreateSessionParams(image_id="agb-browser-use-1"))
if not create_result.success:
    print("Session creation failed:", create_result.error_message)
    raise SystemExit(1)

session = create_result.session
ok = await session.browser.initialize_async(BrowserOption())
print("Browser initialized:", ok)
```

## Common issues

### Browser initialization fails

- **Likely cause**: wrong `image_id`, missing permissions, or slow/blocked navigation during init.
- **Fix**: use a valid browser image and prefer internal pages during initialization (see [`docs/browser/configuration.md`](configuration.md)).

### CDP connection issues

```python
try:
    endpoint_url = session.browser.get_endpoint_url()
    browser = await p.chromium.connect_over_cdp(endpoint_url)
except Exception as e:
    print("CDP connection failed:", e)
    await session.browser.initialize_async(BrowserOption())
```

- **Likely cause**: browser not initialized or endpoint is stale.
- **Fix**: re-initialize and re-connect.

### Agent actions fail

```python
from agb.modules.browser import ActOptions, ObserveOptions

act_result = await session.browser.agent.act_async(
    ActOptions(action="Look for a button with text 'Submit' and click it"),
    page,
)

success, elements = await session.browser.agent.observe_async(
    ObserveOptions(instruction="Check if the page finished loading and show all interactive elements"),
    page,
)
print(act_result.success, act_result.message, success, len(elements) if elements else 0)
```

- **Likely cause**: ambiguous instructions or dynamic page state.
- **Fix**: be specific and observe page state before acting.

## Debug mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance tips

1. Reuse sessions for multiple operations when possible.
2. Use shorter timeouts for simple operations; increase for navigation and downloads.
3. Batch actions when possible.
4. Monitor session health/resources.

## Related

- Main guide: [`docs/browser/overview.md`](overview.md)
- Best practices: [`docs/browser/best-practices.md`](best-practices.md)

