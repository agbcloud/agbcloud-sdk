# Directory management

::: code-group

```python [Python]
create_result = session.file.mkdir("/tmp/project")
if create_result.success:
    print("Directory created")

session.file.mkdir("/tmp/project/src")
session.file.mkdir("/tmp/project/docs")

list_result = session.file.list("/tmp/project")
if list_result.success:
    for entry in list_result.entries:
        print(f"- {entry['name']} ({entry['isDirectory']})")
```

```typescript [TypeScript]
const createResult = await session.file.mkdir("/tmp/project");
if (createResult.success) {
  console.log("Directory created");
}

await session.file.mkdir("/tmp/project/src");
await session.file.mkdir("/tmp/project/docs");

const listResult = await session.file.list("/tmp/project");
if (listResult.success) {
  for (const entry of listResult.entries ?? []) {
    console.log(`- ${entry.name} (${entry.type})`);
  }
}
```

:::