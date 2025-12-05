# Code Execution Guide

## Overview

The AGB SDK provides powerful code execution capabilities in the cloud. You can run Python, JavaScript, Java, and R code in isolated, secure environments without needing to install language runtimes locally. This guide covers everything from basic code execution to advanced patterns and best practices.

## Quick Reference (1 minute)

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-1")
session = agb.create(params).session

# Execute Python code
result = session.code.run_code("print('Hello, World!')", "python")
print(result.result)

# Execute JavaScript
print(session.code.run_code("console.log('Hello World')", "javascript").result)

agb.delete(session)
```

## Core Concepts

### Supported Languages
- **Python**: Full Python environment with standard libraries (and often pandas/numpy pre-installed in data science images).
- **JavaScript**: Node.js environment.
- **Java**: Supports code snippets (no class boilerplate required).
- **R**: Statistical computing environment.

### Timeouts
Default execution timeout is 60 seconds. For long-running tasks:
```python
session.code.run_code("import time; time.sleep(100)", "python", timeout_s=120)
```

## Advanced Usage (15-30 minutes)

For production applications, consider implementing these advanced patterns. Complete implementations are available in the examples directory.

### 1. Caching Results
To reduce costs and latency, cache deterministic code execution results locally.
- **Example**: [Caching Example](../examples/code_execution/README.md)

### 2. Concurrent Execution
Process data pipelines faster by running multiple code snippets in parallel (using multiple sessions).
- **Example**: [Concurrency Example](../examples/code_execution/README.md)

### 3. Security Validation
Always validate user-provided code before execution to prevent resource abuse or unwanted behavior.
- **Example**: [Security Example](../examples/code_execution/README.md)

## Best Practices

### 1. Code Organization

```python
# ✅ Good: Break complex code into steps
def execute_data_pipeline(session):
    """Execute a data processing pipeline in steps"""

    # Step 1: Data loading
    load_code = """
import pandas as pd
data = pd.read_csv('/tmp/input.csv')
print(f"Loaded {len(data)} rows")
"""
    result1 = session.code.run_code(load_code, "python")
    if not result1.success:
        return False, "Data loading failed"

    # Step 2: Data processing
    process_code = """
# Clean and process data
data_cleaned = data.dropna()
data_processed = data_cleaned.groupby('category').sum()
print("Data processed successfully")
"""
    result2 = session.code.run_code(process_code, "python")
    if not result2.success:
        return False, "Data processing failed"

    # Step 3: Save results
    save_code = """
data_processed.to_csv('/tmp/output.csv')
print("Results saved")
"""
    result3 = session.code.run_code(save_code, "python")
    return result3.success, "Pipeline completed" if result3.success else "Save failed"
```

### 2. Error Recovery

```python
def robust_code_execution(session, code: str, language: str, max_retries: int = 3):
    """Execute code with retry logic"""
    for attempt in range(max_retries):
        try:
            result = session.code.run_code(code, language)
            if result.success:
                return result
            else:
                print(f"Attempt {attempt + 1} failed: {result.error_message}")
                if attempt < max_retries - 1:
                    print("Retrying...")
        except Exception as e:
            print(f"Attempt {attempt + 1} exception: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")

    return None  # All attempts failed
```

### 3. Resource Management

```python
def execute_with_resource_monitoring(session, code: str, language: str):
    """Execute code with resource monitoring"""
    import time

    start_time = time.time()

    # Check initial session health
    initial_info = session.info()

    try:
        result = session.code.run_code(code, language)
        execution_time = time.time() - start_time

        print(f"Execution completed in {execution_time:.2f}s")

        # Check final session health
        final_info = session.info()
        if initial_info.success and final_info.success:
            print("Session remained healthy")

        return result

    except Exception as e:
        execution_time = time.time() - start_time
        print(f"Execution failed after {execution_time:.2f}s: {e}")
        return None
```

### 4. Code Validation

```python
def validate_and_execute(session, code: str, language: str):
    """Validate code before execution"""

    # Basic validation
    if not code.strip():
        return {"success": False, "error": "Empty code"}

    if language not in ["python", "javascript"]:
        return {"success": False, "error": f"Unsupported language: {language}"}

    # Language-specific validation
    if language == "python":
        # Check for dangerous operations
        dangerous_patterns = ["os.system", "subprocess.call", "exec(", "eval("]
        for pattern in dangerous_patterns:
            if pattern in code:
                print(f"Warning: Potentially dangerous operation detected: {pattern}")

    # Execute the code
    result = session.code.run_code(code, language)

    return {
        "success": result.success,
        "output": result.result,
        "error": result.error_message if not result.success else None
    }
```

## Troubleshooting

### Common Issues

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

## Related Documentation
- **[Session Management Guide](session-management.md)** - Managing code execution sessions
- **[Command Execution Tutorial](../guides/command-execution.md)** - Running shell commands
- **[File Operations Tutorial](../guides/file-operations.md)** - Working with files in code
- **[API Reference](../api-reference/capabilities/code_execution.md)** - Complete code execution API
- **[Examples](../examples/file_system/README.md)** - More code execution examples
