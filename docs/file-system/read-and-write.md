# Read and write files

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)

if result.success:
    session = result.session

    # Write a text file
    write_result = session.file_system.write_file(
        path="/tmp/example.txt",
        content="This is example content\nWith multiple lines"
    )

    if write_result.success:
        print("File written successfully")

        # Read the file back
        read_result = session.file_system.read_file("/tmp/example.txt")
        if read_result.success:
            print("File content:")
            print(read_result.content)
        else:
            print(f"Failed to read file: {read_result.error_message}")
        else:
            print(f"Failed to write file: {write_result.error_message}")
else:
    print(f"Failed to create session: {result.error_message}")

agb.delete(session)