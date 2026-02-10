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

start_result = session.computer.app.start("notepad.exe")
if not start_result.success:
    raise SystemExit(start_result.error_message)
time.sleep(2)

windows = session.computer.window.list_root_windows(timeout_ms=5000)
if windows:
    window_id = windows[0].window_id
    result = session.computer.window.activate(window_id)
    if not result.success:
        raise SystemExit(result.error_message)

agb.delete(session)
```

## Common tasks

### List root windows

```python
windows = session.computer.window.list_root_windows(timeout_ms=5000)
for w in windows:
    print(w.title, w.window_id, w.pname, w.pid)
```

### Get active window

```python
active_window = session.computer.window.get_active_window()
if active_window:
    print(active_window.title, active_window.window_id, active_window.width, active_window.height)
```

### Control windows

Activate:

```python
result = session.computer.window.activate(window_id)
if not result.success:
    raise SystemExit(result.error_message)
```

Maximize / minimize / restore:

```python
result = session.computer.window.maximize(window_id)
if not result.success:
    raise SystemExit(result.error_message)
result = session.computer.window.minimize(window_id)
if not result.success:
    raise SystemExit(result.error_message)
result = session.computer.window.restore(window_id)
if not result.success:
    raise SystemExit(result.error_message)
```

Resize:

```python
result = session.computer.window.resize(window_id, 800, 600)
if not result.success:
    raise SystemExit(result.error_message)
```

Fullscreen:

```python
result = session.computer.window.fullscreen(window_id)
if not result.success:
    raise SystemExit(result.error_message)
```

Close (use with caution):

```python
result = session.computer.window.close(window_id)
if not result.success:
    raise SystemExit(result.error_message)
```

Focus mode:

```python
result = session.computer.window.focus_mode(on=True)
if not result.success:
    raise SystemExit(result.error_message)
result = session.computer.window.focus_mode(on=False)
if not result.success:
    raise SystemExit(result.error_message)
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

