# Directory management

```python
# Create directories
create_result = session.file.mkdir("/tmp/project")
if create_result.success:
    print("Directory created")

# Create nested directories
session.file.mkdir("/tmp/project/src")
session.file.mkdir("/tmp/project/docs")

# List directory contents
list_result = session.file.list("/tmp/project")
if list_result.success:
    print("Directory contents:")
    for entry in list_result.entries:
        print(f"- {entry['name']} ({entry['isDirectory']})")
```