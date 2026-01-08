# Window management

## What you’ll do

List, activate, resize, maximize/minimize, fullscreen, and close windows in a computer session.

## Prerequisites

- `AGB_API_KEY`
- A valid computer automation `image_id` (e.g. `agb-computer-use-ubuntu-2204`)
- An application running (window management requires windows to exist)

## Quickstart

Minimal runnable example: start an app, list root windows, activate the first window.

```python
import time
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-computer-use-ubuntu-2204"))
if not create_result.success:
    raise SystemExit(create_result.error_message)

session = create_result.session

start_result = session.computer.start_app("notepad.exe")
if start_result.success:
    time.sleep(2)

windows_result = session.computer.list_root_windows(timeout_ms=5000)
if windows_result.success and windows_result.windows:
    window_id = windows_result.windows[0].window_id
    session.computer.activate_window(window_id)

agb.delete(session)
```

## Common tasks

### List root windows

```python
result = session.computer.list_root_windows(timeout_ms=5000)
if result.success:
    for w in result.windows:
        print(w.title, w.window_id, w.pname, w.pid)
```

### Get active window

```python
result = session.computer.get_active_window()
if result.success and result.window:
    w = result.window
    print(w.title, w.window_id, w.width, w.height)
```

### Control windows

Activate:

```python
session.computer.activate_window(window_id)
```

Maximize / minimize / restore:

```python
session.computer.maximize_window(window_id)
session.computer.minimize_window(window_id)
session.computer.restore_window(window_id)
```

Resize:

```python
session.computer.resize_window(window_id, 800, 600)
```

Fullscreen:

```python
session.computer.fullscreen_window(window_id)
```

Close (use with caution):

```python
session.computer.close_window(window_id)
```

Focus mode:

```python
session.computer.focus_mode(on=True)
session.computer.focus_mode(on=False)
```

## Best practices

- Start the app first, then wait a bit before listing windows.\n+- Validate `window_id` exists before operating.\n+
## Troubleshooting

### Window not found

- **Likely cause**: app has not started yet, or needs more time.
- **Fix**: add `sleep`, list windows and print titles, then match by title/process.

## Related

- Application management: [`docs/computer/applications.md`](applications.md)
- Workflows: [`docs/computer/workflows.md`](workflows.md)
- API reference: [`docs/api-reference/capabilities/computer.md`](../api-reference/capabilities/computer.md)

