# Use detailed command results (`exit_code`, `stdout`, `stderr`, `trace_id`)

## What you’ll do

Understand and use detailed fields in `CommandResult` to implement robust error handling and output parsing.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` that supports command execution (commonly `agb-code-space-1`)

## Quickstart

Minimal runnable example: run a failing command and inspect `exit_code`, `stdout`, and `stderr`.

::: code-group

```python [Python]
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
finally:
    agb.delete(session)
```

```typescript [TypeScript]
import { AGB, CreateSessionParams } from "agbcloud-sdk";

const agb = new AGB();
const createResult = await agb.create(
  new CreateSessionParams({ imageId: "agb-code-space-1" })
);
if (!createResult.success || !createResult.session) {
  throw new Error(`Session creation failed: ${createResult.errorMessage}`);
}

const session = createResult.session;
try {
  const result = await session.command.execute("ls /path/does-not-exist");
  console.log("success:", result.success);
  console.log("exitCode:", result.exitCode);
  console.log("stdout:", result.stdout);
  console.log("stderr:", result.stderr);
} finally {
  await agb.delete(session);
}
```

:::

## Common tasks

### Branch logic based on `exit_code`

::: code-group

```python [Python]
result = session.command.execute("grep -R \"needle\" /tmp")
if result.exit_code == 0:
    print("Found matches")
elif result.exit_code == 1:
    print("No matches")
else:
    raise RuntimeError(f"grep failed: exit_code={result.exit_code}, stderr={result.stderr}")
```

```typescript [TypeScript]
const result = await session.command.execute('grep -R "needle" /tmp');
if (result.exitCode === 0) {
  console.log("Found matches");
} else if (result.exitCode === 1) {
  console.log("No matches");
} else {
  throw new Error(`grep failed: exitCode=${result.exitCode}, stderr=${result.stderr}`);
}
```

:::

### Parse `stdout` and keep `stderr` for diagnostics

::: code-group

```python [Python]
result = session.command.execute("python -c 'print(\"ok\")'")
if not result.success:
    raise RuntimeError(f"Command failed: {result.error_message} (stderr={result.stderr})")

stdout = (result.stdout or "").strip()
print("parsed:", stdout)
```

```typescript [TypeScript]
const result = await session.command.execute("python -c 'print(\"ok\")'");
if (!result.success) {
  throw new Error(`Command failed: ${result.errorMessage} (stderr=${result.stderr})`);
}

const stdout = (result.stdout ?? "").trim();
console.log("parsed:", stdout);
```

:::

### Use `trace_id` when reporting issues

If you need to open a ticket with server-side logs, include `trace_id` (when present):

::: code-group

```python [Python]
result = session.command.execute("some-command")
if not result.success and result.trace_id:
    print("trace_id:", result.trace_id)
```

```typescript [TypeScript]
const result = await session.command.execute("some-command");
if (!result.success && result.traceId) {
  console.log("traceId:", result.traceId);
}
```

:::

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
- API reference: [`docs/api-reference/python/capabilities/shell_commands.md`](../api-reference/python/capabilities/shell_commands.md)

