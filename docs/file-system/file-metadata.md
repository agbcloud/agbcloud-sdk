# Get information about a file

::: code-group

```python [Python]
info_result = session.file.info("/tmp/example.txt")
if info_result.success:
    info = info_result.file_info
    print(f"File size: {info.get('size', 'unknown')} bytes")
    print(f"File type: {info.get('type', 'unknown')}")
    print(f"Last modified: {info.get('modified', 'unknown')}")
```

```typescript [TypeScript]
const infoResult = await session.file.getFileInfo("/tmp/example.txt");
if (infoResult.success) {
  const info = infoResult.fileInfo;
  console.log(`File size: ${info?.size ?? "unknown"} bytes`);
  console.log(`File type: ${info?.type ?? "unknown"}`);
}
```

:::