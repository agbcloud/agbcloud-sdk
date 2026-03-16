# Troubleshooting

## Common Issues

**File Not Found Errors**

::: code-group

```python [Python]
read_result = session.file.read("/nonexistent/file.txt")
if not read_result.success:
    if "not found" in read_result.error_message.lower():
        print("File doesn't exist - create it first")
    else:
        print(f"Other error: {read_result.error_message}")
```

```typescript [TypeScript]
const readResult = await session.file.read("/nonexistent/file.txt");
if (!readResult.success) {
  if (readResult.errorMessage?.toLowerCase().includes("not found")) {
    console.log("File doesn't exist - create it first");
  } else {
    console.error("Other error:", readResult.errorMessage);
  }
}
```

:::

**Directory Creation Issues**

::: code-group

```python [Python]
import os

def ensure_directory_exists(session, filepath):
    parent_dir = os.path.dirname(filepath)
    if parent_dir and parent_dir != "/":
        session.file.mkdir(parent_dir)
    return parent_dir

filepath = "/tmp/deep/nested/file.txt"
ensure_directory_exists(session, filepath)
session.file.write(filepath, "content")
```

```typescript [TypeScript]
import * as path from "path";

async function ensureDirectoryExists(session: Session, filepath: string) {
  const parentDir = path.dirname(filepath);
  if (parentDir && parentDir !== "/") {
    await session.file.mkdir(parentDir);
  }
}

const filepath = "/tmp/deep/nested/file.txt";
await ensureDirectoryExists(session, filepath);
await session.file.write(filepath, "content");
```

:::