# Workflows

## What you’ll do

Build end-to-end desktop automation workflows by combining app start/stop, window management, mouse clicks, and keyboard input.

## Prerequisites

- `AGB_API_KEY`
- A valid computer automation `image_id` (e.g. `agb-computer-use-ubuntu-2204`)

## Quickstart

Example: start an app, wait for a window, type text, and close.

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
type_result = session.computer.keyboard.type("Hello from an automated workflow!")
if not type_result.success:
    raise SystemExit(type_result.error_message)

agb.delete(session)
```

## Common tasks

### Window management workflow

```python
import time

def manage_application_window(session, app_name: str) -> bool:
    try:
        start_result = session.computer.app.start(app_name)
        if not start_result.success or not start_result.data:
            print(f"Failed to start {app_name}")
            return False
    except Exception as e:
        print(f"Failed to start {app_name}: {e}")
        return False

    time.sleep(3)
    try:
        windows = session.computer.window.list_root_windows()
    except Exception as e:
        print(f"Failed to list windows: {e}")
        return False

    target_window = None
    for window in windows:
        if app_name.lower().replace(".exe", "") in window.title.lower():
            target_window = window
            break

    if not target_window:
        print(f"Window for {app_name} not found")
        return False

    window_id = target_window.window_id
    session.computer.window.activate(window_id)
    time.sleep(1)
    session.computer.window.maximize(window_id)
    time.sleep(1)
    session.computer.window.resize(window_id, 1024, 768)
    time.sleep(1)
    session.computer.window.restore(window_id)
    return True
```

### Automated text editing workflow (example)

```python
import time

def automated_text_editing_workflow(session) -> bool:
    try:
        apps = session.computer.app.list_installed()
    except Exception as e:
        print(f"Failed to get installed applications: {e}")
        return False

    first_app = None
    for app in apps:
        if "google chrome" in app.name.lower():
            first_app = app
            break

    if not first_app:
        print("No suitable application found")
        return False

    try:
        start_result = session.computer.app.start(first_app.start_cmd)
        if not start_result.success or not start_result.data:
            print(f"Failed to start {first_app.name}")
            return False
    except Exception as e:
        print(f"Failed to start {first_app.name}: {e}")
        return False

    time.sleep(2)
    session.computer.keyboard.type("Hello from AGB Computer Automation!")
    time.sleep(1)
    session.computer.keyboard.press(["Ctrl", "a"])
    time.sleep(0.5)
    session.computer.keyboard.press(["Ctrl", "c"])
    time.sleep(0.5)
    return True
```

## Best practices

- Add timeouts and retry logic around flaky UI actions.\n+- Insert delays between dependent operations.\n+
## Troubleshooting

### Timing issues

- **Likely cause**: the UI has not finished updating.
- **Fix**: add `sleep` between steps and verify state via window listing/screenshot.

## Related

- Best practices: [`docs/computer/best-practices.md`](best-practices.md)
- Troubleshooting: [`docs/computer/troubleshooting.md`](troubleshooting.md)

