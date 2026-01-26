# Best practices

## Always Check Operation Results

```python
# ✅ Good: Always check success status
write_result = session.file.write("/tmp/file.txt", "content")
if write_result.success:
    print("File written successfully")
else:
    print(f"Write failed: {write_result.error_message}")

# ❌ Bad: Assuming operations always succeed
session.file.write("/tmp/file.txt", "content")
# No error checking - could fail silently
```

## Use Absolute Paths

```python
# ✅ Good: Use absolute paths
session.file.write("/tmp/myfile.txt", "content")

# ❌ Avoid: Relative paths can be unpredictable
session.file.write("myfile.txt", "content")
```

## Large Files Are Handled Automatically

```python
def write_content(session, filepath, content):
    """Write content to file - large files are handled automatically"""
    # No need to check file size - the system handles chunking automatically
    result = session.file.write(filepath, content)
    return result.success, result.error_message

# Example: Write a large file (automatically chunked)
large_content = "x" * (2 * 1024 * 1024)  # 2MB content
success, error = write_content(session, "/tmp/large_file.txt", large_content)
if success:
    print("Large file written successfully with automatic chunking")
else:
    print(f"Write failed: {error}")
```

## Clean Up Temporary Files

```python
def with_temp_file(session, content, operation):
    """Context manager pattern for temporary files"""
    temp_file = f"/tmp/temp_{hash(content)}.txt"

    try:
        # Create temp file
        write_result = session.file.write(temp_file, content)
        if not write_result.success:
            raise Exception(f"Failed to create temp file: {write_result.error_message}")

        # Perform operation
        return operation(session, temp_file)

    finally:
        # Clean up
        session.file.move(temp_file, "/tmp/trash/" + temp_file.split("/")[-1])

# Usage
def process_file(session, filepath):
    read_result = session.file.read(filepath)
    return read_result.content.upper() if read_result.success else None

result = with_temp_file(session, "hello world", process_file)
print(result)  # "HELLO WORLD"
```
