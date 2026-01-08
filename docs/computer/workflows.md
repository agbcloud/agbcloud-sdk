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

session.computer.start_app("notepad.exe")
time.sleep(2)
session.computer.input_text("Hello from an automated workflow!")

agb.delete(session)
```

## Common tasks

### Window management workflow

```python
import time

def manage_application_window(session, app_name: str) -> bool:
    start_result = session.computer.start_app(app_name)
    if not start_result.success:
        print(f"Failed to start {app_name}")
        return False

    time.sleep(3)
    windows_result = session.computer.list_root_windows()
    if not windows_result.success:
        print("Failed to list windows")
        return False

    target_window = None
    for window in windows_result.windows:
        if app_name.lower().replace(".exe", "") in window.title.lower():
            target_window = window
            break

    if not target_window:
        print(f"Window for {app_name} not found")
        return False

    window_id = target_window.window_id
    session.computer.activate_window(window_id)
    time.sleep(1)
    session.computer.maximize_window(window_id)
    time.sleep(1)
    session.computer.resize_window(window_id, 1024, 768)
    time.sleep(1)
    session.computer.restore_window(window_id)
    return True
```

### Automated text editing workflow (example)

```python
import time

def automated_text_editing_workflow(session) -> bool:
    apps_result = session.computer.get_installed_apps()
    if not apps_result.success:
        print("Failed to get installed applications")
        return False

    first_app = None
    for app in apps_result.data:
        if "google chrome" in app.name.lower():
            first_app = app
            break

    if not first_app:
        print("No suitable application found")
        return False

    start_result = session.computer.start_app(first_app.start_cmd)
    if not start_result.success:
        print(f"Failed to start {first_app.name}")
        return False

    time.sleep(2)
    session.computer.input_text("Hello from AGB Computer Automation!")
    time.sleep(1)
    session.computer.press_keys(["Ctrl", "a"])
    time.sleep(0.5)
    session.computer.press_keys(["Ctrl", "c"])
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

