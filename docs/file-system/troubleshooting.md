# Troubleshooting

## Common Issues

**File Not Found Errors**
```python
read_result = session.file_system.read_file("/nonexistent/file.txt")
if not read_result.success:
    if "not found" in read_result.error_message.lower():
        print("File doesn't exist - create it first")
    else:
        print(f"Other error: {read_result.error_message}")
```

**Directory Creation Issues**
```python
# Create parent directories first
def ensure_directory_exists(session, filepath):
    """Ensure parent directory exists before writing file"""
    import os
    parent_dir = os.path.dirname(filepath)

    if parent_dir and parent_dir != "/":
        create_result = session.file_system.create_directory(parent_dir)
        if not create_result.success:
            print(f"Warning: Could not create directory {parent_dir}")

    return parent_dir

# Usage
filepath = "/tmp/deep/nested/file.txt"
ensure_directory_exists(session, filepath)
session.file_system.write_file(filepath, "content")
```