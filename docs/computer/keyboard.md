# Keyboard operations

## What you’ll do

Send text and key combinations to the active window in a computer session.

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

session.computer.keyboard.type("Hello AGB!")
session.computer.keyboard.press(["Ctrl", "a"])
agb.delete(session)
```

```typescript [TypeScript]
import { AGB, CreateSessionParams } from "agbcloud-sdk";

const agb = new AGB();
const result = await agb.create(
  new CreateSessionParams({ imageId: "agb-computer-use-ubuntu-2204" })
);
const session = result.session!;

await session.computer.keyboard.type("Hello AGB!");
await session.computer.keyboard.press(["Ctrl", "a"]);
await agb.delete(session);
```

:::

## Common tasks

### Text input

::: code-group

```python [Python]
result = session.computer.keyboard.type("Hello, World!")
print(result.success, result.error_message)
```

```typescript [TypeScript]
const result = await session.computer.keyboard.type("Hello, World!");
console.log(result.success, result.errorMessage);
```

:::

### Key combinations

::: code-group

```python [Python]
session.computer.keyboard.press(["Ctrl", "c"])  # copy
session.computer.keyboard.press(["Ctrl", "v"])  # paste
session.computer.keyboard.press(["Ctrl", "a"])  # select all
```

```typescript [TypeScript]
await session.computer.keyboard.press(["Ctrl", "c"]);  // copy
await session.computer.keyboard.press(["Ctrl", "v"]);  // paste
await session.computer.keyboard.press(["Ctrl", "a"]);  // select all
```

:::

### Press and release keys

```python
# Press keys normally (releases immediately)
session.computer.keyboard.press(["Ctrl", "a"])

# Press and hold keys (must manually release)
session.computer.keyboard.press(["Shift"], hold=True)
# ... perform other operations while Shift is held ...
session.computer.keyboard.release(["Shift"])  # Remember to release!
```

## Best practices

- Ensure the right window is active before typing (see [`docs/computer/windows.md`](windows.md)).
- Add delays if the app needs time to process inputs.

## Troubleshooting

### Text goes to the wrong place

- **Likely cause**: wrong window is active, or focus is not on a text field.
- **Fix**: activate the target window and click the input field before typing.

## Related

- Window management: [`docs/computer/windows.md`](windows.md)
- API reference: [`docs/api-reference/python/capabilities/computer.md`](../api-reference/python/capabilities/computer.md)

