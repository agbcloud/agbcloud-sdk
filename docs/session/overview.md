# Manage sessions

Sessions are the core concept in AGB SDK. A session represents an isolated cloud environment where you can execute code, run commands, manage files, and interact with cloud storage. This guide covers everything you need to know about managing sessions effectively.

**Important**: Image ID Management. When creating sessions, you need to specify an appropriate `image_id`. Please ensure you use valid image IDs that are available in your account. You can view and manage your available images in the [AGB Console Image Management](https://agb.cloud/console/image-management) page.

## What you’ll do

Create, use, list, label, and delete **sessions** (isolated cloud environments) in the AGB SDK.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` (for the runtime you need, e.g. `agb-code-space-1`)
- Permission to create sessions in your account

## Quickstart

Minimal runnable example: create a session, run one action, then delete it.

::: code-group

```python [Python]
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-code-space-1"))
if not create_result.success:
    raise SystemExit(f"Session creation failed: {create_result.error_message}")

session = create_result.session
session.code.run("print('Hello from AGB')", "python")
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
await session.code.run("print('Hello from AGB')", "python");
await agb.delete(session);
```

:::

## Understand auto-release (timeout)

Sessions are automatically released after a period of inactivity to free up resources.

- **`idle_release_timeout`**: Set at session creation to control how long a session can remain idle before auto-release. The timer starts from the last API request — any API call resets it.
- **`keep_alive()`**: Call this method periodically to prevent auto-release during long-running tasks or when waiting for external events.
- Released sessions will **not** appear in `agb.list()` and the session ID becomes invalid.

For detailed lifecycle management, see [Session Lifecycle](./lifecycle.md).

## WebSocket long connection

Sessions support **WebSocket long connections** for real-time streaming capabilities:

- **`ws_url`**: WebSocket endpoint URL
- **`token`**: Authentication token for WebSocket
- **`link_url`**: Direct HTTP endpoint for long-polling

These properties are automatically populated when a session is created and enable:

- **Real-time code streaming**: Receive stdout/stderr output as code executes
- **Live progress monitoring**: Track long-running computations in real-time
- **Lower latency**: Direct connection bypasses traditional API polling

For streaming code execution, see [Real-time Streaming](../code-interpreting/stream-outputs.md).

## Best practices

- Always delete sessions when done (including error paths).
- Make `image_id` explicit in examples; remind users it must exist in their account.
- Use labels to organize sessions (project/env/team) and simplify filtering.
- Treat `agb.list()` as “active sessions only”; do not use it as an audit log.
- For data persistence, use Context synchronization instead of relying on session lifetime.

## Troubleshooting

### Session creation failed

- **Likely cause**: invalid `AGB_API_KEY`, invalid `image_id`, or missing permissions.
- **Suggestion**: Check the `error_message` returned by the `create` API for specific error details.
- **Fix**: verify credentials and image availability in the console.

### My session is not in `agb.list()`

- **Likely cause**: `agb.list()` returns only active sessions; your session may have been deleted or auto-released.
- **Fix**: create a new session; use Context sync for persistence if needed.

### `delete()` fails

- **Likely cause**: session already released, or network/API issue.
- **Fix**: retry, and check the returned `error_message` for details.

## Related

- API reference: [`docs/api-reference/python/session.md`](../api-reference/python/session.md)
- API reference (client): [`docs/api-reference/python/agb.md`](../api-reference/python/agb.md)
- Examples: [`docs/examples/session_management/README.md`](../examples/session_management/README.md)
- Persistence: [`docs/context/overview.md`](../context/overview.md)