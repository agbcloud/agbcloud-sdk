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

capture_result = session.computer.screen.capture()
if not capture_result.success:
    raise SystemExit(capture_result.error_message)
image_url = capture_result.data
print("Screenshot URL:", image_url)

size_result = session.computer.screen.get_size()
if size_result.success and size_result.data:
    d = size_result.data
    print("Screen:", d["width"], "x", d["height"])
    print("DPI scale:", d.get("dpiScalingFactor"))

agb.delete(session)
```

## Common tasks

### Take a screenshot

```python
result = session.computer.screen.capture()
if not result.success:
    raise SystemExit(result.error_message)
image_url = result.data
print("Screenshot URL:", image_url)
```

### Get screen size

```python
size_result = session.computer.screen.get_size()
if size_result.success and size_result.data:
    d = size_result.data
    print(f"Screen size: {d['width']}x{d['height']}")
    print(f"DPI scaling: {d.get('dpiScalingFactor')}")
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

