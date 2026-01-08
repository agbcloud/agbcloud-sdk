# Use context for persistence across sessions

## What you’ll do

Create a **Context** (persistent storage), attach it to sessions via `ContextSync`, and synchronize data across sessions.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` (commonly `agb-code-space-1` for code/file workflows)
- Permission to create contexts and sessions in your account

## Quickstart

Minimal runnable example: create/get a context, mount it into a session, then delete the session.

```python
from agb import AGB
from agb.context_sync import ContextSync, SyncPolicy
from agb.session_params import CreateSessionParams

agb = AGB()

context_result = agb.context.get("my-project", create=True)
if not context_result.success:
    raise SystemExit(f"Context get/create failed: {context_result.error_message}")
context = context_result.context

sync = ContextSync.new(
    context_id=context.id,
    path="/home/project",
    policy=SyncPolicy(),
)

create_result = agb.create(
    CreateSessionParams(image_id="agb-code-space-1", context_syncs=[sync])
)
if not create_result.success:
    raise SystemExit(f"Session creation failed: {create_result.error_message}")

session = create_result.session
agb.delete(session)
```

## Common tasks

This topic is large. Detailed content has been split into smaller pages:

- Context basics (create/get/list): [`docs/context/basics.md`](basics.md)
- Context file operations (upload/download/list/delete): [`docs/context/file-operations.md`](file-operations.md)
- Sync in sessions (manual sync, status monitoring, modes): [`docs/context/sync-in-sessions.md`](sync-in-sessions.md)
- Sync policies (advanced): [`docs/context/sync-policies.md`](sync-policies.md)
- Cross-platform persistence: [`docs/context/cross-platform-persistence.md`](cross-platform-persistence.md)

## Best practices

See: [`docs/context/best-practices.md`](best-practices.md)

## Troubleshooting

See: [`docs/context/troubleshooting.md`](troubleshooting.md)

## Related

- API reference: [`docs/api-reference/data_context/context.md`](../api-reference/data_context/context.md)
- API reference (sync): [`docs/api-reference/data_context/synchronization.md`](../api-reference/data_context/synchronization.md)
- Examples: [`docs/examples/data_persistence/README.md`](../examples/data_persistence/README.md)