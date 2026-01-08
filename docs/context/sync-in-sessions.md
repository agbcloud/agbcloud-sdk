# Sync in sessions

## What you’ll do

Mount a Context into a session with `ContextSync`, trigger manual sync, and check sync status.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` (e.g. `agb-code-space-1`)
- A Context (`context_id`)

## Quickstart

Create a session with a mounted context:

```python
from agb import AGB
from agb.context_sync import ContextSync, SyncPolicy
from agb.session_params import CreateSessionParams

agb = AGB()
context = agb.context.get("test", create=True).context

context_sync = ContextSync.new(
    context_id=context.id,
    path="/home/my-data",
    policy=SyncPolicy(),
)

create_result = agb.create(
    CreateSessionParams(image_id="agb-code-space-1", context_syncs=[context_sync])
)
if not create_result.success:
    raise SystemExit(create_result.error_message)

session = create_result.session
agb.delete(session)
```

## Common tasks

### Trigger manual sync (async)

`session.context.sync()` is an async method. Use it inside an async function:

```python
import asyncio

async def sync_now(session) -> None:
    result = await session.context.sync()
    print(result.success, result.error_message)

asyncio.run(sync_now(session))
```

### Trigger sync in background (callback)

```python
def on_done(success: bool) -> None:
    print("Sync done:", success)

session.context.sync(callback=on_done)
```

### Monitor sync status

```python
info_result = session.context.info()
if info_result.success:
    for s in info_result.context_status_data:
        print(s.context_id, s.path, s.status, s.task_type, s.error_message)
```

## Best practices

- Keep your mount path stable (e.g. `/home/project`) across sessions.
- Use sync policies to control auto upload/download behavior (see `docs/context/sync-policies.md`).

## Troubleshooting

### Sync fails

- **Likely cause**: invalid `context_id`/path mapping or network/API errors.
- **Fix**: verify the context exists, the mount path is correct, and inspect `error_message`.

## Related

- Overview: [`docs/context/overview.md`](overview.md)
- Sync policies: [`docs/context/sync-policies.md`](sync-policies.md)
- API reference (sync): [`docs/api-reference/data_context/synchronization.md`](../api-reference/data_context/synchronization.md)

