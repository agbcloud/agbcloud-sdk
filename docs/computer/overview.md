# Computer automation

## What you’ll do

Automate a desktop environment in an AGB session: mouse/keyboard actions, screenshots, application lifecycle, and window management.

## Prerequisites

- `AGB_API_KEY`
- A valid computer automation `image_id` (e.g. `agb-computer-use-ubuntu-2204`)
- Permission to create sessions in your account

## Quickstart

Minimal runnable example: create a computer session, click, type, take a screenshot, then clean up.

```python
from agb import AGB
from agb.session_params import CreateSessionParams
from agb import MouseButton

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-computer-use-ubuntu-2204"))
if not create_result.success:
    raise SystemExit(f"Session creation failed: {create_result.error_message}")

session = create_result.session

session.computer.mouse.click(x=500, y=300, button=MouseButton.LEFT)
session.computer.keyboard.type("Hello from AGB!")
image_url = session.computer.screen.capture()
print("Screenshot URL:", image_url)

agb.delete(session)
```

## Common tasks

This topic is large; the detailed API usage has been split into smaller pages:

- Mouse operations: [`docs/computer/mouse.md`](mouse.md)
- Keyboard operations: [`docs/computer/keyboard.md`](keyboard.md)
- Screen operations (screenshot, screen size): [`docs/computer/screen.md`](screen.md)
- Application management (installed apps, start/stop, running apps): [`docs/computer/applications.md`](applications.md)
- Window management (list/activate/resize/focus/close): [`docs/computer/windows.md`](windows.md)
- End-to-end workflows: [`docs/computer/workflows.md`](workflows.md)

## Best practices

See: [`docs/computer/best-practices.md`](best-practices.md)

## Troubleshooting

See: [`docs/computer/troubleshooting.md`](troubleshooting.md)

## Related

- API reference: [`docs/api-reference/capabilities/computer.md`](../api-reference/capabilities/computer.md)
- Examples: `docs/examples/computer/` (Python scripts)
