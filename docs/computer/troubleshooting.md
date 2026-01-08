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

screen_result = session.computer.get_screen_size()
if screen_result.success:
    screen = json.loads(screen_result.data)
    print("Screen:", screen["width"], "x", screen["height"], "DPI:", screen.get("dpiScalingFactor"))

screenshot = session.computer.screenshot()
print("Screenshot URL:", screenshot.data)
```

## Common issues

### Coordinate issues

Symptoms: clicks miss the target or land offset.

- **Likely cause**: wrong coordinates, DPI scaling, wrong active window.
- **Fix**: print screen size/DPI, activate the target window, validate coordinates.

### Application not starting

```python
apps_result = session.computer.get_installed_apps()
if apps_result.success:
    print("Available applications:", [app.name for app in apps_result.data])
```

- **Likely cause**: app isn’t installed or `start_cmd` is invalid for this image.
- **Fix**: get `start_cmd` from installed apps list and retry.

### Window not found

```python
def debug_windows(session):
    result = session.computer.list_root_windows()
    if result.success:
        print(f"Found {len(result.windows)} windows:")
        for i, window in enumerate(result.windows):
            print(f\"{i+1}. Title: '{window.title}'  ID: {window.window_id}  Process: {window.pname}\")
    else:
        print(f\"Failed to list windows: {result.error_message}\")

debug_windows(session)
```

- **Likely cause**: the app needs more time to create windows.
- **Fix**: add delays after `start_app()`, then re-list windows.

### Timing issues

```python
import time

session.computer.start_app("notepad.exe")
time.sleep(3)
session.computer.click_mouse(500, 300)
time.sleep(0.5)
session.computer.input_text("Hello")
time.sleep(1)
```

### Session health check

```python
def check_session_health(session) -> bool:
    result = session.computer.get_screen_size()
    if result.success:
        return True
    print(f\"Session issue: {result.error_message}\")
    return False

print(\"Healthy:\", check_session_health(session))
```

## Related

- Best practices: [`docs/computer/best-practices.md`](best-practices.md)
- API reference: [`docs/api-reference/capabilities/computer.md`](../api-reference/capabilities/computer.md)

