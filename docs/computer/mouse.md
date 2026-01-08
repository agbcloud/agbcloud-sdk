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
session.computer.click_mouse(x=500, y=300, button=MouseButton.LEFT)
session.computer.move_mouse(x=600, y=400)
session.computer.scroll(x=500, y=500, direction=ScrollDirection.DOWN, amount=3)

agb.delete(session)
```

## Common tasks

### Click operations

```python
from agb import MouseButton

session.computer.click_mouse(x=500, y=300, button=MouseButton.LEFT)
session.computer.click_mouse(x=500, y=300, button=MouseButton.RIGHT)
session.computer.click_mouse(x=500, y=300, button=MouseButton.MIDDLE)
session.computer.click_mouse(x=500, y=300, button=MouseButton.DOUBLE_LEFT)
```

Supported buttons:

- `MouseButton.LEFT`
- `MouseButton.RIGHT`
- `MouseButton.MIDDLE`
- `MouseButton.DOUBLE_LEFT`

### Move mouse / get cursor position

```python
import json

session.computer.move_mouse(x=600, y=400)

cursor_result = session.computer.get_cursor_position()
if cursor_result.success:
    cursor_data = json.loads(cursor_result.data)
    print(f"Cursor at x={cursor_data['x']}, y={cursor_data['y']}")
```

### Drag operations

```python
from agb import MouseButton

session.computer.drag_mouse(from_x=100, from_y=100, to_x=200, to_y=200, button=MouseButton.LEFT)
session.computer.drag_mouse(from_x=300, from_y=300, to_x=400, to_y=400, button=MouseButton.RIGHT)
```

Note: `MouseButton.DOUBLE_LEFT` is not supported for drag. Use `LEFT`, `RIGHT`, or `MIDDLE`.

### Scroll operations

```python
from agb import ScrollDirection

session.computer.scroll(x=500, y=500, direction=ScrollDirection.UP, amount=3)
session.computer.scroll(x=500, y=500, direction=ScrollDirection.DOWN, amount=5)
session.computer.scroll(x=500, y=500, direction=ScrollDirection.LEFT, amount=2)
session.computer.scroll(x=500, y=500, direction=ScrollDirection.RIGHT, amount=2)
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

