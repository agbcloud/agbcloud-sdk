# Mouse operations

## What you’ll do

Perform mouse actions in a computer session: click, move, drag, and scroll.

## Prerequisites

- `AGB_API_KEY`
- A valid computer automation `image_id` (e.g. `agb-computer-use-ubuntu-2204`)

## Quickstart

::: code-group

```python [Python]
from agb import AGB, MouseButton, ScrollDirection
from agb.session_params import CreateSessionParams

agb = AGB()
result = agb.create(CreateSessionParams(image_id="agb-computer-use-ubuntu-2204"))
session = result.session

session.computer.mouse.click(x=500, y=300, button=MouseButton.LEFT)
session.computer.mouse.move(x=600, y=400)
session.computer.mouse.scroll(x=500, y=500, direction=ScrollDirection.DOWN, amount=3)

agb.delete(session)
```

```typescript [TypeScript]
import { AGB, CreateSessionParams } from "agbcloud-sdk";
import { MouseButton, ScrollDirection } from "agbcloud-sdk/modules/computer/computer";

const agb = new AGB();
const result = await agb.create(
  new CreateSessionParams({ imageId: "agb-computer-use-ubuntu-2204" })
);
const session = result.session!;

await session.computer.mouse.click(500, 300, MouseButton.LEFT);
await session.computer.mouse.move(600, 400);
await session.computer.mouse.scroll(500, 500, ScrollDirection.DOWN, 3);

await agb.delete(session);
```

:::

## Common tasks

### Click operations

::: code-group

```python [Python]
from agb import MouseButton

session.computer.mouse.click(x=500, y=300, button=MouseButton.LEFT)
session.computer.mouse.click(x=500, y=300, button=MouseButton.RIGHT)
session.computer.mouse.click(x=500, y=300, button=MouseButton.MIDDLE)
```

```typescript [TypeScript]
await session.computer.mouse.click(500, 300, MouseButton.LEFT);
await session.computer.mouse.click(500, 300, MouseButton.RIGHT);
await session.computer.mouse.click(500, 300, MouseButton.MIDDLE);
```

:::

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
- API reference: [`docs/api-reference/python/capabilities/computer.md`](../api-reference/python/capabilities/computer.md)

