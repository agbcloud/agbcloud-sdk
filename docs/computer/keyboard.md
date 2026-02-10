# Keyboard operations

## What you’ll do

Send text and key combinations to the active window in a computer session.

## Prerequisites

- `AGB_API_KEY`
- A valid computer automation `image_id` (e.g. `agb-computer-use-ubuntu-2204`)

## Quickstart

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-computer-use-ubuntu-2204"))
if not create_result.success:
    raise SystemExit(create_result.error_message)

session = create_result.session
session.computer.keyboard.type("Hello AGB!")
session.computer.keyboard.press(["Ctrl", "a"])

agb.delete(session)
```

## Common tasks

### Text input

```python
result = session.computer.keyboard.type("Hello, World!")
print(result.success, result.error_message)
```

### Key combinations

```python
session.computer.keyboard.press(["Ctrl", "c"])  # copy
session.computer.keyboard.press(["Ctrl", "v"])  # paste
session.computer.keyboard.press(["Ctrl", "a"])  # select all
```

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
- API reference: [`docs/api-reference/capabilities/computer.md`](../api-reference/capabilities/computer.md)

