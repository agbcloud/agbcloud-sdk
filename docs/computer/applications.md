# Application management

## What you’ll do

Discover installed applications, start/stop apps, and inspect running/visible applications in a computer session.

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

apps_result = session.computer.get_installed_apps()
print("Installed apps:", apps_result.success, len(apps_result.data) if apps_result.success else apps_result.error_message)

agb.delete(session)
```

## Common tasks

### Discover installed applications

```python
result = session.computer.get_installed_apps(
    start_menu=True,
    desktop=False,
    ignore_system_apps=True,
)

if result.success:
    apps = result.data
    print(f"Found {len(apps)} installed applications")
    for app in apps[:5]:
        print(f"Name: {app.name}")
        print(f"Start Command: {app.start_cmd}")
        print(f"Stop Command: {app.stop_cmd if app.stop_cmd else 'N/A'}")
        print(f"Work Directory: {app.work_directory if app.work_directory else 'N/A'}")
        print("---")
```

### Start an application

Start by command:

```python
start_cmd = "notepad.exe"
result = session.computer.start_app(start_cmd)
print(result.success, result.error_message)
```

Start with a working directory:

```python
start_cmd = "notepad.exe"
work_directory = "C:\\Users\\Public\\Documents"
result = session.computer.start_app(start_cmd=start_cmd, work_directory=work_directory)
print(result.success, result.error_message)
```

Start from the installed apps list:

```python
apps_result = session.computer.get_installed_apps()
if apps_result.success:
    target_app = None
    for app in apps_result.data:
        if "google chrome" in app.name.lower():
            target_app = app
            break

    if target_app:
        session.computer.start_app(target_app.start_cmd)
```

### List visible/running applications

```python
result = session.computer.list_visible_apps()
if result.success:
    for app in result.data:
        print(f"App: {app.pname} (PID: {app.pid})")
        if app.cmdline:
            print("Command:", app.cmdline)
```

### Stop an application

Stop by process name:

```python
result = session.computer.stop_app_by_pname("notepad.exe")
print(result.success, result.error_message)
```

Stop by PID:

```python
start_result = session.computer.start_app("notepad.exe")
if start_result.success and start_result.data:
    target_pid = start_result.data[0].pid
    stop_result = session.computer.stop_app_by_pid(target_pid)
    print(stop_result.success, stop_result.error_message)
```

Stop by stop command:

```python
apps_result = session.computer.get_installed_apps()
if apps_result.success:
    for app in apps_result.data:
        if app.stop_cmd and "google chrome" in app.name.lower():
            stop_result = session.computer.stop_app_by_cmd(app.stop_cmd)
            print(stop_result.success, stop_result.error_message)
            break
```

## Best practices

- Use `get_installed_apps()` to find the right `start_cmd` instead of guessing.\n+- Add delays after `start_app()` to allow windows to appear.\n+
## Troubleshooting

### Application not starting

- **Likely cause**: app is not installed, or `start_cmd` is not correct for this image.
- **Fix**: list installed apps and verify `start_cmd`.

## Related

- Window management: [`docs/computer/windows.md`](windows.md)
- API reference: [`docs/api-reference/capabilities/computer.md`](../api-reference/capabilities/computer.md)

