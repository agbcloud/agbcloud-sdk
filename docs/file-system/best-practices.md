# Best practices

## Always Check Operation Results

::: code-group

```python [Python]
write_result = session.file.write("/tmp/file.txt", "content")
if write_result.success:
    print("File written successfully")
else:
    print(f"Write failed: {write_result.error_message}")
```

```typescript [TypeScript]
const writeResult = await session.file.write("/tmp/file.txt", "content");
if (writeResult.success) {
  console.log("File written successfully");
} else {
  console.error("Write failed:", writeResult.errorMessage);
}
```

:::

## Use Absolute Paths

::: code-group

```python [Python]
session.file.write("/tmp/myfile.txt", "content")    # ✅ absolute path
session.file.write("myfile.txt", "content")          # ❌ relative path
```

```typescript [TypeScript]
await session.file.write("/tmp/myfile.txt", "content");  // ✅ absolute path
await session.file.write("myfile.txt", "content");       // ❌ relative path
```

:::

## Large Files Are Handled Automatically

::: code-group

```python [Python]
large_content = "x" * (2 * 1024 * 1024)  # 2MB content
result = session.file.write("/tmp/large_file.txt", large_content)
if result.success:
    print("Large file written successfully with automatic chunking")
```

```typescript [TypeScript]
const largeContent = "x".repeat(2 * 1024 * 1024); // 2MB content
const result = await session.file.write("/tmp/large_file.txt", largeContent);
if (result.success) {
  console.log("Large file written successfully with automatic chunking");
}
```

:::

## Clean Up Temporary Files

::: code-group

```python [Python]
def with_temp_file(session, content, operation):
    temp_file = f"/tmp/temp_{hash(content)}.txt"
    try:
        session.file.write(temp_file, content)
        return operation(session, temp_file)
    finally:
        session.file.move(temp_file, "/tmp/trash/" + temp_file.split("/")[-1])

def process_file(session, filepath):
    read_result = session.file.read(filepath)
    return read_result.content.upper() if read_result.success else None

result = with_temp_file(session, "hello world", process_file)
print(result)  # "HELLO WORLD"
```

```typescript [TypeScript]
async function withTempFile<T>(
  session: Session, content: string, operation: (s: Session, path: string) => Promise<T>,
): Promise<T> {
  const tempFile = `/tmp/temp_${Date.now()}.txt`;
  try {
    await session.file.write(tempFile, content);
    return await operation(session, tempFile);
  } finally {
    await session.file.move(tempFile, `/tmp/trash/${tempFile.split("/").pop()}`);
  }
}

const result = await withTempFile(session, "hello world", async (s, path) => {
  const readResult = await s.file.read(path);
  return readResult.success ? readResult.content?.toUpperCase() : null;
});
console.log(result); // "HELLO WORLD"
```

:::
