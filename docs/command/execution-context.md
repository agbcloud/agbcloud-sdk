# Maintain execution context across commands

## What you'll do

Keep shell state (working directory, variables) consistent across multiple operations by chaining commands or using shell scripts — since each `execute()` call runs in a fresh shell session. Note that filesystem changes (installed tools, created files) persist within the session; only shell-level state resets between calls.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` that supports command execution (commonly `agb-code-space-1`)

## Quickstart

Minimal runnable example: chain commands to navigate and operate within the same shell context.

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
    result = session.command.execute("cd /app && ls -la")
    if not result.success:
        raise RuntimeError(f"Command failed: {result.error_message}")
    print("Output:", result.output)
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
  const result = await session.command.execute("cd /app && ls -la");
  if (!result.success) throw new Error(`Command failed: ${result.errorMessage}`);
  console.log("Output:", result.output);
} finally {
  await agb.delete(session);
}
```

:::

## Common tasks

### Method 1: Chain commands with `&&`

Use `&&` to run multiple steps in a single shell invocation. The working directory, variables, and any state set earlier in the chain are preserved within that one call.

::: code-group

```python [Python]
# Navigate to a directory and run a build step
result = session.command.execute(
    "cd /app && npm install && npm run build",
    timeout_ms=60000,
)
print(result.output)
```

```typescript [TypeScript]
// Navigate to a directory and run a build step
const result = await session.command.execute(
  "cd /app && npm install && npm run build",
  60000,
);
console.log(result.output);
```

:::

::: code-group

```python [Python]
# Set a variable and use it in the same call
result = session.command.execute("export VERSION=1.2.3 && echo Building version $VERSION")
print(result.output)  # Building version 1.2.3
```

```typescript [TypeScript]
// Set a variable and use it in the same call
const result = await session.command.execute(
  "export VERSION=1.2.3 && echo Building version $VERSION"
);
console.log(result.output); // Building version 1.2.3
```

:::

### Method 2: Write all steps to a shell script

For more complex workflows, write the full logic into a `.sh` script on the session file system first, then execute it. This keeps the code clean and avoids deeply nested command strings.

::: code-group

```python [Python]
# Step 1: write the script to the session file system
script = """#!/bin/bash
set -e
cd /app
npm install
npm run build
echo "Build complete"
"""
session.file.write("/tmp/build.sh", script)

# Step 2: run it
result = session.command.execute("bash /tmp/build.sh", timeout_ms=60000)
if not result.success:
    raise RuntimeError(f"Script failed: {result.error_message}")
print(result.output)
```

```typescript [TypeScript]
// Step 1: write the script to the session file system
const script = `#!/bin/bash
set -e
cd /app
npm install
npm run build
echo "Build complete"
`;
await session.file.write("/tmp/build.sh", script);

// Step 2: run it
const result = await session.command.execute("bash /tmp/build.sh", 60000);
if (!result.success) throw new Error(`Script failed: ${result.errorMessage}`);
console.log(result.output);
```

:::

### Run a long-running process in the background

`execute()` is synchronous and blocks until the command exits or the timeout is reached. For processes that run indefinitely (servers, daemons, watchers), launch them with `nohup ... &` so `execute()` returns immediately.

::: code-group

```python [Python]
# Start a server in the background; execute() returns right away
session.command.execute(
    "nohup python -m http.server 8080 > /tmp/server.log 2>&1 &",
    timeout_ms=5000,
)

# Later, check whether it started
result = session.command.execute("curl -fs http://localhost:8080 && echo ok || echo not ready")
print(result.output)
```

```typescript [TypeScript]
// Start a server in the background; execute() returns right away
await session.command.execute(
  "nohup python -m http.server 8080 > /tmp/server.log 2>&1 &",
  5000,
);

// Later, check whether it started
const result = await session.command.execute(
  "curl -fs http://localhost:8080 && echo ok || echo not ready"
);
console.log(result.output);
```

:::

> **Note:** `execute()` has a `timeout_ms` limit (default 1000 ms). Any command that takes longer than the timeout will be terminated and return a failure. For long-running processes, use `nohup ... &` to run them in the background, or use `computer.app.start()` described below.

### Method 3: Use `computer.app.start()` for long-running scripts

> **Note:** This method is only available for **computer images** (e.g., `agb-computer-use-ubuntu-2204`). It is not supported on code-space images.

For long-running scripts that exceed the `execute()` timeout, use `computer.app.start()`. This method launches a process without waiting for it to complete and returns immediately with the started process information (PID), which you can use to monitor or stop the process later.

::: code-group

```python [Python]
# Write a long-running data processing script
script = """#!/bin/bash
set -e
cd /data
for file in *.csv; do
    echo "Processing $file..."
    python process.py "$file"
    sleep 1
done
echo "All files processed" > /tmp/done.txt
"""
session.file.write("/tmp/batch_process.sh", script)

# Start the script using computer.app.start()
result = session.computer.app.start("bash /tmp/batch_process.sh", work_directory="/data")
if not result.success:
    raise RuntimeError(f"Failed to start script: {result.error_message}")

# result.data contains started process info
for process in result.data:
    print(f"Started process: PID={process.pid}, Name={process.pname}")

# Later, check if the script has completed
check = session.command.execute("cat /tmp/done.txt 2>/dev/null || echo 'still running'")
print(check.output)
```

```typescript [TypeScript]
// Write a long-running data processing script
const script = `#!/bin/bash
set -e
cd /data
for file in *.csv; do
    echo "Processing $file..."
    python process.py "$file"
    sleep 1
done
echo "All files processed" > /tmp/done.txt
`;
await session.file.write("/tmp/batch_process.sh", script);

// Start the script using computer.app.start()
const result = await session.computer.app.start("bash /tmp/batch_process.sh", "/data");
if (!result.success) {
  throw new Error(`Failed to start script: ${result.errorMessage}`);
}

// result.data contains started process info
for (const process of result.data) {
  console.log(`Started process: PID=${process.pid}, Name=${process.pname}`);
}

// Later, check if the script has completed
const check = await session.command.execute("cat /tmp/done.txt 2>/dev/null || echo 'still running'");
console.log(check.output);
```

:::

> **When to use `computer.app.start()` vs `nohup`:**
> - Use `computer.app.start()` when you need process information (PID) returned immediately
> - Use `nohup ... &` within `execute()` for simple background tasks where you don't need process tracking

## Best practices

- Use `&&` for linear multi-step workflows that must share shell state within one call.
- Use a shell script for complex logic (loops, conditionals, error handling with `set -e`).
- For processes that run indefinitely, use `computer.app.start()` or `nohup ... &`; increase `timeout_ms` only for genuinely long-running one-shot commands (e.g., large downloads or builds).
- Use `computer.app.start()` when you need to track the started process (PID); use `nohup` for simpler fire-and-forget scenarios.
- Check `result.success` and `result.exit_code` (TypeScript: `exitCode`) after every call; do not assume a command succeeded.

## Troubleshooting

### Shell state (variables, `cd`) does not carry over to the next call

- **Likely cause**: each `execute()` call opens a new shell session; state is not shared between calls.
- **Fix**: chain all dependent steps using `&&` in a single call, or write them into a shell script.

### Command times out before finishing

- **Likely cause**: `timeout_ms` is too short for the operation.
- **Fix**: increase `timeout_ms` for one-shot long commands, run the process in the background with `nohup ... &`, or use `computer.app.start()` for long-running processes.

### Background process does not start

- **Likely cause**: the `nohup ... &` line itself errored before backgrounding.
- **Fix**: check `result.output` / `result.stderr` from the launch call, and inspect the log file (e.g., `/tmp/server.log`).

## Related

- Overview: [`docs/command/overview.md`](./overview.md)
- Working directory: [`docs/command/working-directory.md`](./working-directory.md)
- Environment variables: [`docs/command/environment-variables.md`](./environment-variables.md)
- Detailed results: [`docs/command/detailed-results.md`](./detailed-results.md)
- Computer module (app.start): [`docs/computer/overview.md`](../computer/overview.md)
- API reference: [`docs/api-reference/python/capabilities/shell_commands.md`](../api-reference/python/capabilities/shell_commands.md)
