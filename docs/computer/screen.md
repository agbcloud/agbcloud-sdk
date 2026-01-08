# Screen operations

## What you’ll do

Capture screenshots and read screen information (size/DPI) in a computer session.

## Prerequisites

- `AGB_API_KEY`
- A valid computer automation `image_id` (e.g. `agb-computer-use-ubuntu-2204`)

## Quickstart

```python
import json
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-computer-use-ubuntu-2204"))
if not create_result.success:
    raise SystemExit(create_result.error_message)

session = create_result.session

screenshot = session.computer.screenshot()
print("Screenshot URL:", screenshot.data)

size_result = session.computer.get_screen_size()
if size_result.success:
    screen = json.loads(size_result.data)
    print("Screen:", screen["width"], "x", screen["height"])
    print("DPI scale:", screen.get("dpiScalingFactor"))

agb.delete(session)
```

## Common tasks

### Take a screenshot

```python
result = session.computer.screenshot()
print(result.success, result.data)
```

### Get screen size

```python
import json

result = session.computer.get_screen_size()
if result.success:
    screen = json.loads(result.data)
    print(f"Screen size: {screen['width']}x{screen['height']}")
    print(f"DPI scaling: {screen.get('dpiScalingFactor')}")
```

## Best practices

- Use screen size to validate coordinates before clicking (see [`docs/computer/mouse.md`](mouse.md)).

## Troubleshooting

### Coordinates look off

- **Likely cause**: DPI scaling or incorrect screen dimensions.
- **Fix**: print `get_screen_size()` and validate coordinates.

## Related

- Mouse operations: [`docs/computer/mouse.md`](mouse.md)
- API reference: [`docs/api-reference/capabilities/computer.md`](../api-reference/capabilities/computer.md)

