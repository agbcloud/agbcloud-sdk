# Use detailed command results (`exit_code`, `stdout`, `stderr`, `trace_id`)

## What you’ll do

Understand and use detailed fields in `CommandResult` to implement robust error handling and output parsing.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` that supports command execution (commonly `agb-code-space-1`)

## Quickstart

Minimal runnable example: run a failing command and inspect `exit_code`, `stdout`, and `stderr`.

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-code-space-1"))
if not create_result.success:
    raise SystemExit(f"Session creation failed: {create_result.error_message}")

session = create_result.session
try:
    result = session.command.execute("ls /path/does-not-exist")
    print("success:", result.success)
    print("exit_code:", result.exit_code)
    print("stdout:", result.stdout)
    print("stderr:", result.stderr)
    print("trace_id:", result.trace_id)
finally:
    agb.delete(session)
```

## Common tasks

### Branch logic based on `exit_code`

```python
result = session.command.execute("grep -R \"needle\" /tmp")
if result.exit_code == 0:
    print("Found matches")
elif result.exit_code == 1:
    print("No matches")
else:
    raise RuntimeError(f"grep failed: exit_code={result.exit_code}, stderr={result.stderr}")
```

### Parse `stdout` and keep `stderr` for diagnostics

```python
result = session.command.execute("python -c 'print(\"ok\")'")
if not result.success:
    raise RuntimeError(f"Command failed: {result.error_message} (stderr={result.stderr})")

stdout = (result.stdout or "").strip()
print("parsed:", stdout)
```

### Use `trace_id` when reporting issues

If you need to open a ticket with server-side logs, include `trace_id` (when present):

```python
result = session.command.execute("some-command")
if not result.success and result.trace_id:
    print("trace_id:", result.trace_id)
```

## Best practices

- Prefer `exit_code/stdout/stderr` over parsing a combined `output` string.
- Treat `stdout` as data and `stderr` as diagnostics (don’t mix them).
- For automation, branch on `exit_code` when the command has meaningful exit codes.
- Always include `trace_id` in bug reports when available.

## Troubleshooting

### `success` is false but `exit_code` is `None`

- **Likely cause**: the request failed before the command actually executed (transport/service error).
- **Fix**: check `error_message` and `trace_id`; retry if appropriate.

### Output looks empty but the command printed something

- **Likely cause**: the command wrote to `stderr` instead of `stdout`.
- **Fix**: inspect both `stdout` and `stderr`.

## Related

- Overview: [`docs/command/overview.md`](./overview.md)
- Working directory: [`docs/command/working-directory.md`](./working-directory.md)
- Environment variables: [`docs/command/environment-variables.md`](./environment-variables.md)
- API reference: [`docs/api-reference/capabilities/shell_commands.md`](../api-reference/capabilities/shell_commands.md)

