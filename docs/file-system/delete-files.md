# Delete files

## What you’ll do

Delete a file in an AGB session using `session.file.remove(path)` and handle common failure cases safely.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` that supports filesystem operations (commonly `agb-code-space-1`)

## Quickstart

Minimal runnable example: delete an existing file, then clean up.

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
    delete_result = session.file.remove("/tmp/to_delete.txt")
    if not delete_result.success:
        raise SystemExit(f"Delete failed: {delete_result.error_message}")
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
  const deleteResult = await session.file.remove("/tmp/to_delete.txt");
  if (!deleteResult.success) {
    throw new Error(`Delete failed: ${deleteResult.errorMessage}`);
  }
} finally {
  await agb.delete(session);
}
```

:::

## Common tasks

### Delete multiple files under a directory

::: code-group

```python [Python]
entries = session.file.list("/tmp").entries
for e in entries:
    if e.is_file and e.name.endswith(".tmp"):
        session.file.remove(f"/tmp/{e.name}")
```

```typescript [TypeScript]
const listResult = await session.file.list("/tmp");
for (const e of listResult.entries ?? []) {
  if (e.type === "file" && e.name.endsWith(".tmp")) {
    await session.file.remove(`/tmp/${e.name}`);
  }
}
```

:::

## Best practices

- Prefer deleting under `/tmp` unless you know the image’s writable locations.
- Treat delete as a potentially destructive operation; verify paths and patterns.
- Always check `delete_result.success` and log `error_message` for diagnosis.

## Troubleshooting

### Permission denied

- **Likely cause**: the target path is not writable for the default user.
- **Fix**: delete under writable directories (e.g. `/tmp`), or use an image/user with the required permissions.

### “Path is a directory”

- **Likely cause**: you passed a directory path to `remove`.
- **Fix**: delete a file path; for directories use directory APIs (see directory management docs).

## Related

- API reference: [`docs/api-reference/python/capabilities/file_system.md`](../api-reference/python/capabilities/file_system.md)
- Overview: [`docs/file-system/overview.md`](overview.md)
- Directory management: [`docs/file-system/directory-management.md`](directory-management.md)

