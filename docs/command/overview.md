# Run shell commands in a session

## What you’ll do

Execute Linux shell commands via `session.command.execute()`, handle outputs, and avoid common pitfalls (non-persistent working directory / environment variables).

The Command Execution API also supports:
- **Working Directory**: Use the `cwd` parameter to set the working directory for commands
- **Environment Variables**: Use the `envs` parameter to set environment variables for commands
- **Detailed Results**: Access `exit_code`, `stdout`, `stderr`, and `trace_id` fields for better error handling and output parsing

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` that supports command execution (commonly `agb-code-space-1`)
- (Optional) Any tools you want to run must exist in the image or be installed at runtime

## Quickstart

Minimal runnable example: create a session, run a command, print output, then clean up.

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-code-space-1"))
if not create_result.success:
    raise SystemExit(f"Session creation failed: {create_result.error_message}")

session = create_result.session
cmd_result = session.command.execute("ls -la /tmp")

if cmd_result.success:
    print("Output:", cmd_result.output)
    # Access new fields for more detailed information
    if cmd_result.exit_code is not None:
        print("Exit code:", cmd_result.exit_code)
    if cmd_result.stdout:
        print("Stdout:", cmd_result.stdout)
    if cmd_result.stderr:
        print("Stderr:", cmd_result.stderr)
else:
    print("Error:", cmd_result.error_message)
    if cmd_result.exit_code is not None:
        print("Exit code:", cmd_result.exit_code)

agb.delete(session)
```

## Common tasks

### Learn the new command execution features

- Working directory (`cwd`): [`docs/command/working-directory.md`](./working-directory.md)
- Environment variables (`envs`): [`docs/command/environment-variables.md`](./environment-variables.md)
- Detailed results (`exit_code`, `stdout`, `stderr`, `trace_id`): [`docs/command/detailed-results.md`](./detailed-results.md)

### Set working directory with `cwd` parameter

Use the `cwd` parameter to set the working directory for a command:

```python
# Using cwd parameter (recommended)
result = session.command.execute("pwd", cwd="/tmp")
print(result.output)  # Output: /tmp

# Alternative: command chaining (still works)
session.command.execute("cd /tmp && pwd")
```

### Set environment variables with `envs` parameter

Use the `envs` parameter to set environment variables for a command:

```python
# Using envs parameter (recommended)
result = session.command.execute(
    "echo $TEST_VAR $ANOTHER_VAR",
    envs={"TEST_VAR": "hello", "ANOTHER_VAR": "world"}
)
print(result.output)  # Output: hello world

# Alternative: inline env vars (still works)
session.command.execute("TEST_VAR=hello echo $TEST_VAR")
```

### Combine `cwd` and `envs` parameters

```python
result = session.command.execute(
    "pwd && echo $MY_VAR",
    cwd="/tmp",
    envs={"MY_VAR": "test_value"}
)
```

### Access detailed command results

The command result includes separate `stdout`, `stderr`, and `exit_code` fields:

```python
result = session.command.execute("ls /nonexistent")

if result.exit_code == 0:
    print("Success!")
    print("Output:", result.stdout)
else:
    print(f"Command failed with exit code: {result.exit_code}")
    print("Stdout:", result.stdout)
    print("Stderr:", result.stderr)
    if result.trace_id:
        print("Trace ID:", result.trace_id)
```

### Run multiple operations in one command (legacy approach)

Each `execute` call runs in a **new, isolated shell session**. That means:

- Working directory changes (e.g. `cd`) do **not** persist between calls.
- Environment variables set with `export` do **not** persist between calls.

You can still use command chaining (though using `cwd` and `envs` parameters is recommended):

```python
session.command.execute("cd /tmp && ls -la")
session.command.execute("cd /tmp && ls -la && cat file.txt")
```

### Run diagnostics (CPU / memory / disk)

```python
session.command.execute("free -h")
session.command.execute("df -h")
```

### Do advanced file operations with CLI tools

```python
session.command.execute("tar -czf logs.tar.gz /var/log/*.log")
```

### Install packages (if permitted by the image)

```python
session.command.execute("apt-get update && apt-get install -y jq", timeout_ms=30000)
```

### Increase timeout for long-running commands

```python
session.command.execute("wget large-file.zip", timeout_ms=60000)
```

## Best practices

- Avoid interactive commands (they hang until timeout).
- Always check `cmd_result.success` and handle `cmd_result.error_message`.
- Use the `cwd` parameter instead of `cd` commands for better control.
- Use the `envs` parameter instead of `export` commands for better control.
- Check `exit_code` for more precise error handling (0 means success).
- Use `stdout` and `stderr` separately for better output parsing.
- Prefer absolute paths or use the `cwd` parameter (don't rely on `cd` across calls).
- Chain dependent operations using `&&` or `;` when needed.

## Troubleshooting

### Command not found

- **Likely cause**: the tool is not installed in the image, or `PATH` is missing it.
- **Fix**: verify the tool exists, install it (if allowed), or use an absolute path (e.g. `/bin/ls`).

### Permission denied

- **Likely cause**: commands run as the default user and lack permissions.
- **Fix**: use `sudo` if available and permitted, or switch to an image/user that has the needed access.

### Command timeout

- **Likely cause**: the command runs longer than the default timeout.
- **Fix**: increase `timeout_ms`, or split the operation into smaller steps.

### Working directory / environment variables not persisting

- **Likely cause**: each `execute` call runs in a new shell session.
- **Fix**: use the `cwd` parameter to set working directory, and the `envs` parameter to set environment variables. Alternatively, chain commands (`cd /tmp && ...`) and set env vars in the same command.

## Related

- API reference: [`docs/api-reference/capabilities/shell_commands.md`](../api-reference/capabilities/shell_commands.md)
- Examples: [`docs/examples/command_execution/README.md`](../examples/command_execution/README.md)
- Sessions: [`docs/api-reference/session.md`](../api-reference/session.md)
- Working directory (`cwd`): [`docs/command/working-directory.md`](./working-directory.md)
- Environment variables (`envs`): [`docs/command/environment-variables.md`](./environment-variables.md)
- Detailed results: [`docs/command/detailed-results.md`](./detailed-results.md)
