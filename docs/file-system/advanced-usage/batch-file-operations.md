# Batch file operations

```python
def process_multiple_files(session, file_data):
    """Process multiple files in batch"""
    results = []

    for filename, content in file_data.items():
        # Write file
        write_result = session.file_system.write_file(filename, content)

        if write_result.success:
            # Verify by reading back
            read_result = session.file_system.read_file(filename)
            results.append({
                "filename": filename,
                "success": read_result.success,
                "content_length": len(read_result.content) if read_result.success else 0
            })
        else:
            results.append({
                "filename": filename,
                "success": False,
                "error": write_result.error_message
            })

    return results

# Usage
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)

if result.success:
    session = result.session

    files_to_create = {
        "/tmp/file1.txt": "Content of file 1",
        "/tmp/file2.txt": "Content of file 2",
        "/tmp/file3.txt": "Content of file 3"
    }

    results = process_multiple_files(session, files_to_create)
    for result in results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['filename']}")

        agb.delete(session)
else:
    print(f"Failed to create session: {result.error_message}")
```
