# Troubleshooting

## Common Issues

**Timeout Errors**
```python
# Increase timeout for long-running code
result = session.code.run_code(long_code, "python", timeout_s=600)  # 10 minutes
```

**Memory Issues**
```python
# Break large operations into smaller chunks
large_data_code = """
# Instead of loading all data at once
# data = pd.read_csv('huge_file.csv')  # May cause memory issues

# Process in chunks
chunk_size = 10000
for chunk in pd.read_csv('huge_file.csv', chunksize=chunk_size):
    # Process each chunk
    processed_chunk = chunk.groupby('category').sum()
    print(f"Processed chunk with {len(chunk)} rows")
"""
```

**Import Errors**
```python
# Check available packages
check_packages = """
import sys
import pkg_resources

installed_packages = [d.project_name for d in pkg_resources.working_set]
print("Available packages:", sorted(installed_packages))
"""

session.code.run_code(check_packages, "python")
```

**Syntax Errors**
```python
# Validate syntax before execution
def validate_python_syntax(code: str) -> bool:
    try:
        compile(code, '<string>', 'exec')
        return True
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        return False

# Usage
code_to_check = "print('Hello World')"
if validate_python_syntax(code_to_check):
    result = session.code.run_code(code_to_check, "python")
```