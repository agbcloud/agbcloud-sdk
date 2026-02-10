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

apps_result = session.computer.app.list_installed()
if not apps_result.success:
    raise SystemExit(apps_result.error_message)
apps = apps_result.data
print("Installed apps:", len(apps))

agb.delete(session)
```

## Common tasks

### Discover installed applications

```python
apps_result = session.computer.app.list_installed()
if not apps_result.success:
    raise SystemExit(apps_result.error_message)
apps = apps_result.data
print(f"Found {len(apps)} installed applications")
for app in apps[:5]:
    print(f"Name: {app.name}")
    print(f"Start Command: {app.start_cmd}")
    print(f"Stop Command: {app.stop_cmd if app.stop_cmd else 'N/A'}")
    print(f"Work Directory: {app.work_directory if app.work_directory else 'N/A'}")
    print("---")
```

### Start an application

Start by name:

```python
result = session.computer.app.start("notepad.exe")
if not result.success:
    raise SystemExit(result.error_message)
processes = result.data
print(f"Started {len(processes)} processes")
```

Start with a working directory:

```python
result = session.computer.app.start("notepad.exe", work_directory="C:\\Users\\Public\\Documents")
if not result.success:
    raise SystemExit(result.error_message)
processes = result.data
print(f"Started {len(processes)} processes")
```

Start from the installed apps list:

```python
apps_result = session.computer.app.list_installed()
if not apps_result.success:
    raise SystemExit(apps_result.error_message)
apps = apps_result.data
target_app = None
for app in apps:
    if "google chrome" in app.name.lower():
        target_app = app
        break

if target_app:
    start_result = session.computer.app.start(target_app.start_cmd)
    if not start_result.success:
        raise SystemExit(start_result.error_message)
```

### List visible/running applications

```python
visible_result = session.computer.app.get_visible()
if not visible_result.success:
    raise SystemExit(visible_result.error_message)
visible_apps = visible_result.data
for app in visible_apps:
    print(f"App: {app.pname} (PID: {app.pid})")
    if app.cmdline:
        print("Command:", app.cmdline)
```

### Stop an application

Stop by process name:

```python
result = session.computer.app.stop_by_pname("notepad.exe")
print(result.success, result.error_message)
```

Stop by PID:

```python
start_result = session.computer.app.start("notepad.exe")
if start_result.success and start_result.data:
    target_pid = start_result.data[0].pid
    result = session.computer.app.stop_by_pid(target_pid)
    print(result.success, result.error_message)
```

Stop by shell command (e.g. kill by PID):

```python
# Get PID from the process started by app.start(), then run a kill command
start_result = session.computer.app.start("notepad.exe")
if start_result.success and start_result.data:
    pid = start_result.data[0].pid
    result = session.computer.app.stop_by_cmd(f"kill -9 {pid}")
    print(result.success, result.error_message)
```

## Best practices

- Use `app.list_installed()` to find the right `start_cmd` instead of guessing.
- Add delays after `app.start()` to allow windows to appear.
## Troubleshooting

### Application not starting

- **Likely cause**: app is not installed, or `start_cmd` is not correct for this image.
- **Fix**: list installed apps and verify `start_cmd`.

## Related

- Window management: [`docs/computer/windows.md`](windows.md)
- API reference: [`docs/api-reference/capabilities/computer.md`](../api-reference/capabilities/computer.md)

