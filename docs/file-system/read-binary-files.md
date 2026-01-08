# Read binary files (bytes)

## What you’ll do

Read a file as **raw bytes** using `session.file_system.read_file(..., format="bytes")`, then save/inspect the data on the client side.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` that supports filesystem operations (commonly `agb-code-space-1`)

## Quickstart

Minimal runnable example: read a binary file as bytes and save it locally, then clean up.

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-code-space-1"))
if not create_result.success:
    raise SystemExit(f"Session creation failed: {create_result.error_message}")

session = create_result.session
try:
    # Pick a binary file that exists in most Linux images (ELF binary)
    remote_path = "/bin/ls"

    read_result = session.file_system.read_file(remote_path, format="bytes")
    if not read_result.success:
        raise SystemExit(f"Read failed: {read_result.error_message}")

    with open("ls.bin", "wb") as f:
        f.write(read_result.content)

    print("Saved:", "ls.bin", "bytes=", len(read_result.content))
finally:
    agb.delete(session)
```

## Common tasks

### Read an image and save it locally

```python
read_result = session.file_system.read_file("/tmp/image.png", format="bytes")
if not read_result.success:
    raise RuntimeError(read_result.error_message)

with open("image.png", "wb") as f:
    f.write(read_result.content)
```

### Prefer download for large files

`read_file(..., format="bytes")` returns the whole file content to the client. For large artifacts, prefer download APIs:

- See: [`docs/file-system/upload-and-download.md`](upload-and-download.md)

## Best practices

- Use `format="bytes"` for non-text content (images, archives, protobuf, etc.).
- Keep files reasonably sized when reading into memory; for large files use download.
- Use absolute paths (e.g. `/tmp/...`) to avoid ambiguity.

## Troubleshooting

### Read succeeds but content is empty

- **Likely cause**: the file is empty (size = 0).
- **Fix**: check `get_file_info()` and verify the file was created/written as expected.

### Permission denied

- **Likely cause**: the target path is not readable for the default user in the image.
- **Fix**: read files under readable locations (e.g. `/tmp`), or use an image/user with the required permissions.

### Out of memory (client)

- **Likely cause**: reading a very large file into memory.
- **Fix**: use download instead of `read_file(..., format="bytes")`.

## Related

- API reference: [`docs/api-reference/capabilities/file_system.md`](../api-reference/capabilities/file_system.md)
- Read & write (text): [`docs/file-system/read-and-write.md`](read-and-write.md)
- Upload & download: [`docs/file-system/upload-and-download.md`](upload-and-download.md)
- Delete files: [`docs/file-system/delete-files.md`](delete-files.md)

