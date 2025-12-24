# Get information about a file

```python
# Get file information
info_result = session.file_system.get_file_info("/tmp/example.txt")
if info_result.success:
    info = info_result.file_info
    print(f"File size: {info.get('size', 'unknown')} bytes")
    print(f"File type: {info.get('type', 'unknown')}")
    print(f"Last modified: {info.get('modified', 'unknown')}")
```