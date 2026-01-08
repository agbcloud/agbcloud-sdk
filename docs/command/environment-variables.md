# Set environment variables for commands (`envs`)

## What you’ll do

Provide environment variables for a command using the `envs` parameter, without relying on `export` across separate calls.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` that supports command execution (commonly `agb-code-space-1`)

## Quickstart

Minimal runnable example: pass env vars to a command, print output, then clean up.

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-code-space-1"))
if not create_result.success:
    raise SystemExit(f"Session creation failed: {create_result.error_message}")

session = create_result.session
try:
    result = session.command.execute_command(
        "echo $GREETING $TARGET",
        envs={"GREETING": "hello", "TARGET": "world"},
    )
    if not result.success:
        raise RuntimeError(f"Command failed: {result.error_message}")
    print("Output:", result.output)
finally:
    agb.delete(session)
```

## Common tasks

### Set a single variable

```python
session.command.execute_command("echo $FOO", envs={"FOO": "bar"})
```

### Pass multiple variables

```python
session.command.execute_command(
    "python -c 'import os; print(os.environ[\"A\"], os.environ[\"B\"])'",
    envs={"A": "1", "B": "2"},
)
```

### Legacy alternative: inline env vars (still works)

```python
session.command.execute_command("FOO=bar echo $FOO")
```

Note: inline env vars can be fine for simple cases, but `envs` is easier to manage and less error-prone for complex values.

## Best practices

- Do not rely on `export VAR=...` persisting between calls; it won’t.
- Use `envs` for values with spaces/special characters to avoid shell quoting issues.
- Avoid logging secrets; keep sensitive values out of printed output and logs.

## Troubleshooting

### Environment variables are missing inside the command

- **Likely cause**: you used `export` in a previous call and expected it to persist.
- **Fix**: pass `envs={...}` on the call that needs those variables.

### The command prints empty values

- **Likely cause**: variable name mismatch, or the shell expands before setting the env in some patterns.
- **Fix**: double-check variable names; prefer `envs` and avoid tricky quoting.

## Related

- Overview: [`docs/command/overview.md`](./overview.md)
- Working directory: [`docs/command/working-directory.md`](./working-directory.md)
- Detailed results: [`docs/command/detailed-results.md`](./detailed-results.md)
- API reference: [`docs/api-reference/capabilities/shell_commands.md`](../api-reference/capabilities/shell_commands.md)

