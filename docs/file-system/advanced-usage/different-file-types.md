
# Working with different file types

```python
import json
import csv
from io import StringIO

def handle_json_file(session, filepath, data):
    """Handle JSON file operations"""
    # Write JSON data
    json_content = json.dumps(data, indent=2)
    write_result = session.file.write(filepath, json_content)

    if write_result.success:
        # Read and parse JSON
        read_result = session.file.read(filepath)
        if read_result.success:
            parsed_data = json.loads(read_result.content)
            return True, parsed_data

    return False, None

def handle_csv_file(session, filepath, data):
    """Handle CSV file operations"""
    # Create CSV content
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    csv_content = output.getvalue()

    # Write CSV file
    write_result = session.file.write(filepath, csv_content)

    if write_result.success:
        # Read and parse CSV
        read_result = session.file.read(filepath)
        if read_result.success:
            reader = csv.DictReader(StringIO(read_result.content))
            parsed_data = list(reader)
            return True, parsed_data

    return False, None

# Usage examples
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)

if result.success:
    session = result.session

    # JSON example
    json_data = {"name": "John", "age": 30, "city": "New York"}
    success, result = handle_json_file(session, "/tmp/data.json", json_data)
    if success:
        print("JSON data:", result)

    # CSV example
    csv_data = [
        {"name": "Alice", "age": 25, "city": "Boston"},
        {"name": "Bob", "age": 30, "city": "Chicago"}
    ]
    success, result = handle_csv_file(session, "/tmp/data.csv", csv_data)
    if success:
        print("CSV data:", result)

    agb.delete(session)
else:
    print(f"Failed to create session: {result.error_message}")
```
