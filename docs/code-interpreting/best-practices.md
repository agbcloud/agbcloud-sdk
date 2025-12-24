# Best practices

## Code Organization

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

## Error Recovery

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

## Resource Management

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

## Code Validation

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
