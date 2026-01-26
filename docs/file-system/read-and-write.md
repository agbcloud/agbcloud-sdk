# Read and write files

## What you’ll do

Read and write files inside a session with `session.file`.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` that supports filesystem operations (commonly `agb-code-space-1`)

## Quickstart

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-code-space-1"))
if not create_result.success:
    raise SystemExit(f"Failed to create session: {create_result.error_message}")

session = create_result.session
try:
    # Write a text file
    write_result = session.file.write(
        path="/tmp/example.txt",
        content="This is example content\nWith multiple lines",
    )
    if not write_result.success:
        raise SystemExit(f"Failed to write file: {write_result.error_message}")

    # Read the file back (text)
    read_result = session.file.read("/tmp/example.txt")
    if not read_result.success:
        raise SystemExit(f"Failed to read file: {read_result.error_message}")

    print("File content:")
    print(read_result.content)
finally:
    agb.delete(session)
```

## Related

- Read binary (bytes): [`docs/file-system/read-binary-files.md`](read-binary-files.md)