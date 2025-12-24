# Directory management

```python
# Create directories
create_result = session.file_system.create_directory("/tmp/project")
if create_result.success:
    print("Directory created")

# Create nested directories
session.file_system.create_directory("/tmp/project/src")
session.file_system.create_directory("/tmp/project/docs")

# List directory contents
list_result = session.file_system.list_directory("/tmp/project")
if list_result.success:
    print("Directory contents:")
    for entry in list_result.entries:
        print(f"- {entry['name']} ({entry['isDirectory']})")
```