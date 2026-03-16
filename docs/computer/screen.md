# Screen operations

## What you’ll do

Capture screenshots and read screen information (size/DPI) in a computer session.

## Prerequisites

- `AGB_API_KEY`
- A valid computer automation `image_id` (e.g. `agb-computer-use-ubuntu-2204`)

## Quickstart

::: code-group

```python [Python]
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
result = agb.create(CreateSessionParams(image_id="agb-computer-use-ubuntu-2204"))
session = result.session

capture_result = session.computer.screen.capture()
print("Screenshot URL:", capture_result.data)

size_result = session.computer.screen.get_size()
if size_result.success and size_result.data:
    d = size_result.data
    print("Screen:", d["width"], "x", d["height"])

agb.delete(session)
```

```typescript [TypeScript]
import { AGB, CreateSessionParams } from "agbcloud-sdk";

const agb = new AGB();
const result = await agb.create(
  new CreateSessionParams({ imageId: "agb-computer-use-ubuntu-2204" })
);
const session = result.session!;

const captureResult = await session.computer.screen.capture();
console.log("Screenshot URL:", captureResult.data);

const sizeResult = await session.computer.screen.getSize();
if (sizeResult.success && sizeResult.data) {
  console.log("Screen:", sizeResult.data);
}

await agb.delete(session);
```

:::

## Common tasks

### Take a screenshot

::: code-group

```python [Python]
result = session.computer.screen.capture()
print("Screenshot URL:", result.data)
```

```typescript [TypeScript]
const result = await session.computer.screen.capture();
console.log("Screenshot URL:", result.data);
```

:::

### Get screen size

::: code-group

```python [Python]
size_result = session.computer.screen.get_size()
if size_result.success and size_result.data:
    d = size_result.data
    print(f"Screen size: {d['width']}x{d['height']}")
```

```typescript [TypeScript]
const sizeResult = await session.computer.screen.getSize();
if (sizeResult.success && sizeResult.data) {
  console.log("Screen size:", sizeResult.data);
}
```

:::

## Best practices

- Use screen size to validate coordinates before clicking (see [`docs/computer/mouse.md`](mouse.md)).

## Troubleshooting

### Coordinates look off

- **Likely cause**: DPI scaling or incorrect screen dimensions.
- **Fix**: print `get_screen_size()` and validate coordinates.

## Related

- Mouse operations: [`docs/computer/mouse.md`](mouse.md)
- API reference: [`docs/api-reference/python/capabilities/computer.md`](../api-reference/python/capabilities/computer.md)

