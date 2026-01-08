# Context file operations

## What you’ll do

Upload, download, list, and delete files stored in a Context.

## Prerequisites

- `AGB_API_KEY`
- A Context (`context_id`)
- `requests` installed (examples use presigned URLs)

## Quickstart

Get a presigned upload URL and upload a local file:

```python
import requests
from agb import AGB

agb = AGB()
context = agb.context.get("test", create=True).context

upload_result = agb.context.get_file_upload_url(
    context_id=context.id,
    file_path="/tmp/my-file.txt",
)

if upload_result.success:
    with open("local-file.txt", "rb") as f:
        resp = requests.put(upload_result.url, data=f)
    print("Upload status:", resp.status_code)
else:
    print(upload_result.error_message)
```

## Common tasks

### Download a file

```python
import requests
from agb import AGB

agb = AGB()
context = agb.context.get("test", create=True).context

download_result = agb.context.get_file_download_url(
    context_id=context.id,
    file_path="/tmp/my-file.txt",
)

if download_result.success:
    resp = requests.get(download_result.url)
    if resp.status_code == 200:
        with open("downloaded-file.txt", "wb") as f:
            f.write(resp.content)
else:
    print(download_result.error_message)
```

### List files

```python
from agb import AGB

agb = AGB()
context = agb.context.get("test", create=True).context

files_result = agb.context.list_files(
    context_id=context.id,
    parent_folder_path="/tmp",
    page_number=1,
    page_size=50,
)

if files_result.success:
    for entry in files_result.entries:
        print(entry.file_path, entry.size)
```

### Delete a file

```python
from agb import AGB

agb = AGB()
context = agb.context.get("test", create=True).context

delete_result = agb.context.delete_file(
    context_id=context.id,
    file_path="/data/my-file.txt",
)
print(delete_result.success, delete_result.error_message)
```

## Best practices

- Use structured folders (e.g. `/project/data/`, `/project/models/`) to keep contexts organized.
- Paginate when listing large directories.

## Troubleshooting

### Upload/download fails

- **Likely cause**: local file missing, wrong path, or expired URL.
- **Fix**: re-request presigned URL and retry; verify file paths.

## Related

- Overview: [`docs/context/overview.md`](overview.md)
- API reference: [`docs/api-reference/data_context/context.md`](../api-reference/data_context/context.md)

