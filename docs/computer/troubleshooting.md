# Troubleshooting

## What you’ll do

Diagnose common failures in computer automation (coordinates, application startup, window discovery, timing, session health).

## Prerequisites

- `AGB_API_KEY`
- A valid computer automation `image_id` (e.g. `agb-computer-use-ubuntu-2204`)

## Quickstart

Start by checking screen size and taking a screenshot:

```python
import json

size_result = session.computer.screen.get_size()
if size_result.success and size_result.data:
    d = size_result.data
    print("Screen:", d["width"], "x", d["height"], "DPI:", d.get("dpiScalingFactor"))

capture_result = session.computer.screen.capture()
if not capture_result.success:
    raise SystemExit(capture_result.error_message)
image_url = capture_result.data
print("Screenshot URL:", image_url)
```

## Common issues

### Coordinate issues

Symptoms: clicks miss the target or land offset.

- **Likely cause**: wrong coordinates, DPI scaling, wrong active window.
- **Fix**: print screen size/DPI, activate the target window, validate coordinates.

### Application not starting

```python
apps = session.computer.app.list_installed()
print("Available applications:", [app.name for app in apps])
```

- **Likely cause**: app isn’t installed or `start_cmd` is invalid for this image.
- **Fix**: get `start_cmd` from installed apps list and retry.

### Window not found

```python
def debug_windows(session):
    try:
        windows = session.computer.window.list_root_windows()
        print(f"Found {len(windows)} windows:")
        for i, window in enumerate(windows):
            print(f\"{i+1}. Title: '{window.title}'  ID: {window.window_id}  Process: {window.pname}\")
    except Exception as e:
        print(f\"Failed to list windows: {e}\")

debug_windows(session)
```

- **Likely cause**: the app needs more time to create windows.
- **Fix**: add delays after `start_app()`, then re-list windows.

### Timing issues

```python
import time

session.computer.app.start("notepad.exe")
time.sleep(3)
session.computer.mouse.click(500, 300)
time.sleep(0.5)
session.computer.keyboard.type("Hello")
time.sleep(1)
```

### Session health check

```python
def check_session_health(session) -> bool:
    try:
        size_result = session.computer.screen.get_size()
        return size_result.success
    except Exception as e:
        print(f\"Session issue: {e}\")
        return False

print(\"Healthy:\", check_session_health(session))
```

## Related

- Best practices: [`docs/computer/best-practices.md`](best-practices.md)
- API reference: [`docs/api-reference/capabilities/computer.md`](../api-reference/capabilities/computer.md)

