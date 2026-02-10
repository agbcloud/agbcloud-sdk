# Mouse operations

## What you’ll do

Perform mouse actions in a computer session: click, move, drag, and scroll.

## Prerequisites

- `AGB_API_KEY`
- A valid computer automation `image_id` (e.g. `agb-computer-use-ubuntu-2204`)

## Quickstart

```python
from agb import AGB, MouseButton, ScrollDirection
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-computer-use-ubuntu-2204"))
if not create_result.success:
    raise SystemExit(create_result.error_message)

session = create_result.session
result = session.computer.mouse.click(x=500, y=300, button=MouseButton.LEFT)
if not result.success:
    raise SystemExit(result.error_message)
result = session.computer.mouse.move(x=600, y=400)
if not result.success:
    raise SystemExit(result.error_message)
result = session.computer.mouse.scroll(x=500, y=500, direction=ScrollDirection.DOWN, amount=3)
if not result.success:
    raise SystemExit(result.error_message)

agb.delete(session)
```

## Common tasks

### Click operations

```python
from agb import MouseButton

result = session.computer.mouse.click(x=500, y=300, button=MouseButton.LEFT)
if not result.success:
    raise SystemExit(result.error_message)
result = session.computer.mouse.click(x=500, y=300, button=MouseButton.RIGHT)
if not result.success:
    raise SystemExit(result.error_message)
result = session.computer.mouse.click(x=500, y=300, button=MouseButton.MIDDLE)
if not result.success:
    raise SystemExit(result.error_message)
```

Supported buttons:

- `MouseButton.LEFT`
- `MouseButton.RIGHT`
- `MouseButton.MIDDLE`

### Move mouse / get cursor position

```python
result = session.computer.mouse.move(x=600, y=400)
if not result.success:
    raise SystemExit(result.error_message)

# Get cursor position
pos_result = session.computer.mouse.get_position()
if pos_result.success and pos_result.data:
    x, y = pos_result.data.get("x", 0), pos_result.data.get("y", 0)
    print(f"Cursor at x={x}, y={y}")
```

### Drag operations

```python
from agb import MouseButton

result = session.computer.mouse.drag(x1=100, y1=100, x2=200, y2=200, button=MouseButton.LEFT)
if not result.success:
    raise SystemExit(result.error_message)
result = session.computer.mouse.drag(x1=300, y1=300, x2=400, y2=400, button=MouseButton.RIGHT)
if not result.success:
    raise SystemExit(result.error_message)
```

Note: `MouseButton.DOUBLE_LEFT` is not supported for drag. Use `LEFT`, `RIGHT`, or `MIDDLE`.

### Scroll operations

```python
from agb import ScrollDirection

result = session.computer.mouse.scroll(x=500, y=500, direction=ScrollDirection.UP, amount=3)
if not result.success:
    raise SystemExit(result.error_message)
result = session.computer.mouse.scroll(x=500, y=500, direction=ScrollDirection.DOWN, amount=5)
if not result.success:
    raise SystemExit(result.error_message)
result = session.computer.mouse.scroll(x=500, y=500, direction=ScrollDirection.LEFT, amount=2)
if not result.success:
    raise SystemExit(result.error_message)
result = session.computer.mouse.scroll(x=500, y=500, direction=ScrollDirection.RIGHT, amount=2)
if not result.success:
    raise SystemExit(result.error_message)
```

Supported directions:

- `ScrollDirection.UP`
- `ScrollDirection.DOWN`
- `ScrollDirection.LEFT`
- `ScrollDirection.RIGHT`

## Best practices

- Validate coordinates against screen size (see [`docs/computer/screen.md`](screen.md)).
- Add small delays between UI operations when needed.

## Troubleshooting

### Clicks don’t land where expected

- **Likely cause**: wrong coordinates, DPI scaling, or the window is not focused.
- **Fix**: check screen size/DPI, activate the target window, and validate coordinates.

## Related

- Screen operations: [`docs/computer/screen.md`](screen.md)
- API reference: [`docs/api-reference/capabilities/computer.md`](../api-reference/capabilities/computer.md)

