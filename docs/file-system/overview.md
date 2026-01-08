# Manage files in a session

## What you’ll do

Use `session.file_system` to read, write, and manage files/directories inside an AGB session.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` that supports filesystem operations (commonly `agb-code-space-1`)

## Quickstart

Minimal runnable example: create a session, write a file, read it back, then clean up.

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-code-space-1"))
if not create_result.success:
    raise SystemExit(f"Session creation failed: {create_result.error_message}")

session = create_result.session

try:
    session.file_system.write_file("/tmp/hello.txt", "Hello World!")
    content = session.file_system.read_file("/tmp/hello.txt").content
    print(content)
finally:
    agb.delete(session)
```

## Common tasks

### Create and list directories

```python
session.file_system.create_directory("/tmp/trash/")
entries = session.file_system.list_directory("/tmp").entries
print([e.name for e in entries])
```

### Move files

```python
session.file_system.move_file("/tmp/hello.txt", "/tmp/trash/hello.txt")
```

### Upload / download files

See the dedicated page for details and options:

- `docs/file-system/upload-and-download.md`

### Read binary files

See:

- `docs/file-system/read-binary-files.md`

### Delete files

See:

- `docs/file-system/delete-files.md`

### File metadata

See:

- `docs/file-system/file-metadata.md`

## Best practices

- Use absolute paths (e.g. `/tmp/...`) to avoid ambiguity.
- Clean up sessions when finished to reduce cost (`agb.delete(session)`).
- For large files or batch operations, prefer the dedicated upload/download and batch-operation docs.
## Troubleshooting

### Permission denied

- **Likely cause**: the target path is not writable for the default user in the image.
- **Fix**: write under writable directories (e.g. `/tmp`), or use an image/user with the required permissions.
### File not found

- **Likely cause**: the path does not exist.
- **Fix**: create directories first (`create_directory`) and use `list_directory` to verify paths.
## Related

- API reference: [`docs/api-reference/capabilities/file_system.md`](../api-reference/capabilities/file_system.md)
- Examples: [`docs/examples/file_system/README.md`](../examples/file_system/README.md)
- Read & write: [`docs/file-system/read-and-write.md`](read-and-write.md)
- Read binary (bytes): [`docs/file-system/read-binary-files.md`](read-binary-files.md)
- Upload & download: [`docs/file-system/upload-and-download.md`](upload-and-download.md)
- Delete files: [`docs/file-system/delete-files.md`](delete-files.md)
- Directory management: [`docs/file-system/directory-management.md`](directory-management.md)
- Directory monitoring: [`docs/file-system/directory-monitoring.md`](directory-monitoring.md)
- Best practices: [`docs/file-system/best-practices.md`](best-practices.md)
- Troubleshooting: [`docs/file-system/troubleshooting.md`](troubleshooting.md)