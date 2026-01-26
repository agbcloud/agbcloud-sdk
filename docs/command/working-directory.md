# Set working directory for commands (`cwd`)

## What you’ll do

Run commands in a specific working directory using the `cwd` parameter, without relying on `cd` across separate command executions.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` that supports command execution (commonly `agb-code-space-1`)

## Quickstart

Minimal runnable example: create a session, run a command in `/tmp`, then clean up.

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-code-space-1"))
if not create_result.success:
    raise SystemExit(f"Session creation failed: {create_result.error_message}")

session = create_result.session
try:
    result = session.command.execute("pwd && ls -la", cwd="/tmp")
    if not result.success:
        raise RuntimeError(f"Command failed: {result.error_message}")
    print("Output:", result.output)
finally:
    agb.delete(session)
```

## Common tasks

### Run a command relative to a directory

```python
session.command.execute("ls -la", cwd="/var/log")
```

### Create files in a directory without `cd`

```python
session.command.execute("mkdir -p demo && echo hello > demo/hello.txt", cwd="/tmp")
```

### Legacy alternative: command chaining (still works)

Each `execute()` call runs in a new shell session, so `cd` does not persist between calls. You can still chain commands in one call:

```python
session.command.execute("cd /tmp && pwd && ls -la")
```

## Best practices

- Prefer `cwd` over `cd` to avoid state assumptions between calls.
- Use absolute paths (or `cwd`) for scripts that touch files.
- When combining `cwd` with environment variables, also use `envs` (see Related).

## Troubleshooting

### It still runs in the wrong directory

- **Likely cause**: you used `cd` in a previous call and expected it to persist.
- **Fix**: pass `cwd=...` for every call that depends on working directory.

### Permission denied / no such file or directory

- **Likely cause**: the target directory does not exist or is not accessible.
- **Fix**: create the directory (`mkdir -p`) or choose a writable location like `/tmp`.

## Related

- Overview: [`docs/command/overview.md`](./overview.md)
- Environment variables: [`docs/command/environment-variables.md`](./environment-variables.md)
- API reference: [`docs/api-reference/capabilities/shell_commands.md`](../api-reference/capabilities/shell_commands.md)

