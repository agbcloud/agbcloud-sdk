# File processing pipeline

```python
def file_processing_pipeline(session, input_file, output_file):
    """Complete file processing pipeline"""

    # Step 1: Read input file
    read_result = session.file_system.read_file(input_file)
    if not read_result.success:
        return False, f"Failed to read input: {read_result.error_message}"

    # Step 2: Process content (example: convert to uppercase)
    original_content = read_result.content
    processed_content = original_content.upper()

    # Step 3: Write processed content
    write_result = session.file_system.write_file(output_file, processed_content)
    if not write_result.success:
        return False, f"Failed to write output: {write_result.error_message}"

    # Step 4: Verify output
    verify_result = session.file_system.read_file(output_file)
    if not verify_result.success:
        return False, f"Failed to verify output: {verify_result.error_message}"

    return True, {
        "input_size": len(original_content),
        "output_size": len(processed_content),
        "processed": True
    }

# Usage example
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)

if result.success:
    session = result.session

    # Create input file
    session.file_system.write_file("/tmp/input.txt", "hello world\nthis is a test")

    # Process file
    success, result = file_processing_pipeline(
        session,
        "/tmp/input.txt",
        "/tmp/output.txt"
    )

    if success:
        print("Pipeline completed successfully:")
        print(f"Input size: {result['input_size']} bytes")
        print(f"Output size: {result['output_size']} bytes")
    else:
        print(f"Pipeline failed: {result}")

    agb.delete(session)
else:
    print(f"Failed to create session: {result.error_message}")
```
