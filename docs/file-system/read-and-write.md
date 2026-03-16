# Read and write files

## What you’ll do

Read and write files inside a session with `session.file`.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` that supports filesystem operations (commonly `agb-code-space-1`)

## Quickstart

::: code-group

```python [Python]
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-code-space-1"))
if not create_result.success:
    raise SystemExit(f"Failed to create session: {create_result.error_message}")

session = create_result.session
try:
    write_result = session.file.write(
        path="/tmp/example.txt",
        content="This is example content\nWith multiple lines",
    )
    if not write_result.success:
        raise SystemExit(f"Failed to write file: {write_result.error_message}")

    read_result = session.file.read("/tmp/example.txt")
    print("File content:")
    print(read_result.content)
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
  throw new Error(`Failed to create session: ${createResult.errorMessage}`);
}

const session = createResult.session;
try {
  const writeResult = await session.file.write(
    "/tmp/example.txt",
    "This is example content\nWith multiple lines",
  );
  if (!writeResult.success) {
    throw new Error(`Failed to write file: ${writeResult.errorMessage}`);
  }

  const readResult = await session.file.read("/tmp/example.txt");
  console.log("File content:");
  console.log(readResult.content);
} finally {
  await agb.delete(session);
}
```

:::

## Related

- Read binary (bytes): [`docs/file-system/read-binary-files.md`](read-binary-files.md)