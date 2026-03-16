# Context file operations

## What you’ll do

Upload, download, list, and delete files stored in a Context.

## Prerequisites

- `AGB_API_KEY`
- A Context (`context_id`)
- `requests` installed (examples use presigned URLs)

## Quickstart

Get a presigned upload URL and upload a local file:

::: code-group

```python [Python]
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
```

```typescript [TypeScript]
import { AGB } from "agbcloud-sdk";

const agb = new AGB();
const context = (await agb.context.get("test", true)).context!;

const uploadResult = await agb.context.getFileUploadUrl(
  context.id, "/tmp/my-file.txt",
);

if (uploadResult.success && uploadResult.url) {
  const resp = await fetch(uploadResult.url, {
    method: "PUT",
    body: fs.readFileSync("local-file.txt"),
  });
  console.log("Upload status:", resp.status);
}
```

:::

## Common tasks

### Download a file

::: code-group

```python [Python]
import requests
from agb import AGB

agb = AGB()
context = agb.context.get("test", create=True).context

download_result = agb.context.get_file_download_url(
    context_id=context.id, file_path="/tmp/my-file.txt",
)

if download_result.success:
    resp = requests.get(download_result.url)
    if resp.status_code == 200:
        with open("downloaded-file.txt", "wb") as f:
            f.write(resp.content)
```

```typescript [TypeScript]
const downloadResult = await agb.context.getFileDownloadUrl(
  context.id, "/tmp/my-file.txt",
);

if (downloadResult.success && downloadResult.url) {
  const resp = await fetch(downloadResult.url);
  if (resp.ok) {
    fs.writeFileSync("downloaded-file.txt", Buffer.from(await resp.arrayBuffer()));
  }
}
```

:::

### List files

::: code-group

```python [Python]
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

```typescript [TypeScript]
const filesResult = await agb.context.listFiles(context.id, "/tmp", 1, 50);

if (filesResult.success) {
  for (const entry of filesResult.entries ?? []) {
    console.log(entry.filePath, entry.size);
  }
}
```

:::

### Delete a file

::: code-group

```python [Python]
delete_result = agb.context.delete_file(
    context_id=context.id, file_path="/data/my-file.txt",
)
print(delete_result.success, delete_result.error_message)
```

```typescript [TypeScript]
const deleteResult = await agb.context.deleteFile(context.id, "/data/my-file.txt");
console.log(deleteResult.success, deleteResult.errorMessage);
```

:::

## Best practices

- Use structured folders (e.g. `/project/data/`, `/project/models/`) to keep contexts organized.
- Paginate when listing large directories.

## Troubleshooting

### Upload/download fails

- **Likely cause**: local file missing, wrong path, or expired URL.
- **Fix**: re-request presigned URL and retry; verify file paths.

## Related

- Overview: [`docs/context/overview.md`](overview.md)
- API reference: [`docs/api-reference/python/data_context/context.md`](../api-reference/python/data_context/context.md)

