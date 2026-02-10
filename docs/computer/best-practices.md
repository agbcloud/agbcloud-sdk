# Best practices

## What you’ll do

Apply practical patterns to make computer automation more reliable: cleanup, retries, coordinate validation, and app readiness checks.

## Prerequisites

- `AGB_API_KEY`
- A valid computer automation `image_id` (e.g. `agb-computer-use-ubuntu-2204`)

## Quickstart

Use `try/finally` to always delete sessions:

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-computer-use-ubuntu-2204"))
if not create_result.success:
    raise SystemExit(create_result.error_message)

session = create_result.session
try:
    session.computer.mouse.click(100, 100)
finally:
    agb.delete(session)
```

## Common tasks

### Always clean up sessions

```python
from agb import AGB
from agb.session_params import CreateSessionParams

def safe_automation_task() -> bool:
    agb = AGB()
    result = agb.create(CreateSessionParams(image_id="agb-computer-use-ubuntu-2204"))
    if not result.success:
        print(f"Failed to create session: {result.error_message}")
        return False

    session = result.session
    try:
        click_result = session.computer.mouse.click(100, 100)
        return click_result.success
    finally:
        agb.delete(session)
```

### Error handling and retry logic

```python
import time

def robust_operation(operation_func, max_retries: int = 3):
    for attempt in range(max_retries):
        result = operation_func()
        if result and getattr(result, "success", False):
            return result
        if attempt < max_retries - 1:
            time.sleep(2)
    return None
```

### Coordinate validation

```python
import json
from agb import MouseButton

def safe_click(session, x: int, y: int, button: MouseButton = MouseButton.LEFT) -> bool:
    try:
        size_result = session.computer.screen.get_size()
        if not size_result.success or not size_result.data:
            return False
        screen_data = size_result.data
        max_x = screen_data["width"]
        max_y = screen_data["height"]
    except Exception:
        return False

    if x < 0 or x >= max_x or y < 0 or y >= max_y:
        print(f"Invalid coordinates: ({x}, {y}). Screen size: {max_x}x{max_y}")
        return False

    return session.computer.mouse.click(x=x, y=y, button=button).success
```

### Ensure application is ready

```python
import time

def ensure_application_ready(session, app_name: str, timeout_s: int = 30):
    try:
        start_result = session.computer.app.start(app_name)
        if not start_result.success or not start_result.data:
            return None
    except Exception as e:
        return None

    start_time = time.time()
    while time.time() - start_time < timeout_s:
        try:
            windows = session.computer.window.list_root_windows()
            for window in windows:
                if getattr(window, "window_id", None):
                    session.computer.window.activate(window.window_id)
                    return window
        except Exception:
            pass
        time.sleep(1)
    return None
```

## Troubleshooting

### Flaky UI actions

- **Likely cause**: timing/state issues (window not ready, focus not set).
- **Fix**: add delays, validate window state, and retry idempotent operations.

## Related

- Workflows: [`docs/computer/workflows.md`](workflows.md)
- Troubleshooting: [`docs/computer/troubleshooting.md`](troubleshooting.md)

