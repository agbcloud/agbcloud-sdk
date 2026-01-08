# Best practices

## What you’ll do

Make browser automation reliable: clean up resources, choose timeouts, write robust agent instructions, and add retries where needed.

## Prerequisites

- `AGB_API_KEY`
- A valid browser `image_id` (e.g. `agb-browser-use-1`)

## Quickstart

Always clean up Playwright and the AGB session:

```python
try:
    # Your automation code here
    pass
finally:
    if "browser" in locals():
        await browser.close()
    if "session" in locals():
        agb.delete(session)
```

## Common tasks

### Use internal pages during initialization

During browser initialization, prefer Chrome internal pages (e.g. `chrome://version/`) or extension pages. Navigating to internet URLs during initialization may cause startup timeouts.

See: [`docs/browser/configuration.md`](configuration.md)

### Make agent instructions robust

```python
from agb.modules.browser import ActOptions

await session.browser.agent.act_async(
    ActOptions(action="Wait for the page to load, then click the button with text 'Submit'"),
    page,
)
```

### Retry critical actions

```python
import asyncio

async def retry_action(agent, page, action_options, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            result = await agent.act_async(action_options, page)
            if result.success:
                return result
            print(f"Attempt {attempt + 1} failed: {result.message}")
        except Exception as e:
            print(f"Attempt {attempt + 1} error: {e}")

        if attempt < max_retries - 1:
            await asyncio.sleep(2)

    return None
```

## Troubleshooting

### Slow or flaky pages

- **Likely cause**: dynamic content and timing issues.
- **Fix**: add waiting steps, use observe before act, increase timeouts, and add retries.

## Related

- Main guide: [`docs/browser/overview.md`](overview.md)
- Agent: [`docs/browser/agent.md`](agent.md)

