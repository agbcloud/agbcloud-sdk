# Session Lifecycle

Understand how sessions are created, managed, and released in AGB.

## Overview

A session goes through several states during its lifetime:

```
Created → Active → Idle → Released
            ↑        |
            └────────┘ (on activity)
```

**Key concepts:**
- Sessions consume resources while active
- Idle sessions can be automatically released via `idle_release_timeout`
- Any API request resets the idle timer
- Always clean up sessions when done

**Default limits:**
- `idle_release_timeout`: 5 minutes (if not specified)
- Maximum session lifetime: 30 minutes (extended durations coming soon)

## Lifecycle states

| State | Description |
|-------|-------------|
| **Created** | Session initialized, resources allocated |
| **Active** | Session is processing API requests |
| **Idle** | No recent API activity, timer counting down |
| **Released** | Session terminated, resources freed |

## Auto-release mechanism

When you create a session with `idle_release_timeout`, the session will be automatically released after a period of inactivity.

### How it works

1. **Timer starts**: After each API request, an idle timer begins counting down
2. **Timer resets**: Any API request (e.g., `code.run()`, `file.read()`) resets the timer
3. **Manual refresh**: Call `keep_alive()` to reset the timer without other operations
4. **Auto-release**: If the timer reaches zero, the session is released and cannot be recovered

### Basic usage

::: code-group

```python [Python]
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()

# Create session with 5-minute idle timeout
session = agb.create(
    CreateSessionParams(
        image_id="agb-code-space-1",
        idle_release_timeout=300,
    )
).session

# Any API call resets the idle timer
session.code.run("print('Hello')", "python")

# Explicitly reset timer without other operations
session.keep_alive()

# Clean up when done
agb.delete(session)
```

```typescript [TypeScript]
import { AGB, CreateSessionParams } from "agbcloud-sdk";

const agb = new AGB();

// Create session with 5-minute idle timeout
const session = (await agb.create(
  new CreateSessionParams({
    imageId: "agb-code-space-1",
    idleReleaseTimeout: 300,
  })
)).session;

// Any API call resets the idle timer
await session.code.run("print('Hello')", "python");

// Explicitly reset timer without other operations
await session.keepAlive();

// Clean up when done
await agb.delete(session);
```

:::

## Manual deletion

Always delete sessions explicitly when your workflow completes:

::: code-group

```python [Python]
try:
    # Your workflow
    session.code.run("print('Working')", "python")
finally:
    agb.delete(session)
```

```typescript [TypeScript]
try {
  // Your workflow
  await session.code.run("print('Working')", "python");
} finally {
  await agb.delete(session);
}
```

:::

## Best practices

### Choose appropriate timeout

| Workflow type | Recommended timeout | Rationale |
|--------------|-------------------|-----------|
| Quick tasks | 60-120 seconds | Minimize resource usage |
| Interactive | 300-600 seconds | Balance cost and convenience |
| Long-running | 600-1800 seconds | Accommodate extended operations |

### Call `keep_alive()` proactively

When waiting for external events (user input, API responses), call `keep_alive()` at **50-70%** of your timeout duration:

```python
# Example: 5-minute timeout, refresh every 2 minutes
idle_timeout = 300
refresh_interval = 120

# During long waits
session.keep_alive()
```

### Handle failures gracefully

::: code-group

```python [Python]
result = session.keep_alive()
if not result.success:
    print(f"Failed: {result.error_message}")
    # Create new session if needed
```

```typescript [TypeScript]
const result = await session.keepAlive();
if (!result.success) {
  console.log(`Failed: ${result.errorMessage}`);
  // Create new session if needed
}
```

:::

## Troubleshooting

### Session released unexpectedly

- **Cause**: Idle timer expired before `keep_alive()` was called
- **Fix**: Call `keep_alive()` more frequently, or increase `idle_release_timeout`

### `keep_alive()` returns failure

- **Cause**: Session already released or network issue
- **Fix**: Create a new session and restore state if needed

## Related

- [Session Overview](./overview.md) - Session management basics
- [Context Sync](../context/overview.md) - Data persistence across sessions
