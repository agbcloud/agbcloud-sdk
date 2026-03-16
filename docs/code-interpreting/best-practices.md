# Best practices

## Code Organization

::: code-group

```python [Python]
def execute_data_pipeline(session):
    """Execute a data processing pipeline in steps"""
    load_code = """
import pandas as pd
data = pd.read_csv('/tmp/input.csv')
print(f"Loaded {len(data)} rows")
"""
    result1 = session.code.run(load_code, "python")
    if not result1.success:
        return False, "Data loading failed"

    process_code = """
data_cleaned = data.dropna()
data_processed = data_cleaned.groupby('category').sum()
print("Data processed successfully")
"""
    result2 = session.code.run(process_code, "python")
    if not result2.success:
        return False, "Data processing failed"

    save_code = """
data_processed.to_csv('/tmp/output.csv')
print("Results saved")
"""
    result3 = session.code.run(save_code, "python")
    return result3.success, "Pipeline completed" if result3.success else "Save failed"
```

```typescript [TypeScript]
async function executeDataPipeline(session: Session) {
  const loadCode = `
import pandas as pd
data = pd.read_csv('/tmp/input.csv')
print(f"Loaded {len(data)} rows")
`;
  const result1 = await session.code.run(loadCode, "python");
  if (!result1.success) return { success: false, message: "Data loading failed" };

  const processCode = `
data_cleaned = data.dropna()
data_processed = data_cleaned.groupby('category').sum()
print("Data processed successfully")
`;
  const result2 = await session.code.run(processCode, "python");
  if (!result2.success) return { success: false, message: "Data processing failed" };

  const saveCode = `
data_processed.to_csv('/tmp/output.csv')
print("Results saved")
`;
  const result3 = await session.code.run(saveCode, "python");
  return { success: result3.success, message: result3.success ? "Pipeline completed" : "Save failed" };
}
```

:::

## Error Recovery

::: code-group

```python [Python]
def robust_code_execution(session, code: str, language: str, max_retries: int = 3):
    """Execute code with retry logic"""
    for attempt in range(max_retries):
        try:
            result = session.code.run(code, language)
            if result.success:
                return result
            print(f"Attempt {attempt + 1} failed: {result.error_message}")
        except Exception as e:
            print(f"Attempt {attempt + 1} exception: {e}")
    return None
```

```typescript [TypeScript]
async function robustCodeExecution(
  session: Session, code: string, language: string, maxRetries = 3,
) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const result = await session.code.run(code, language);
      if (result.success) return result;
      console.log(`Attempt ${attempt + 1} failed: ${result.errorMessage}`);
    } catch (e) {
      console.log(`Attempt ${attempt + 1} exception: ${e}`);
    }
  }
  return null;
}
```

:::

## Resource Management

::: code-group

```python [Python]
def execute_with_resource_monitoring(session, code: str, language: str):
    """Execute code with resource monitoring"""
    import time
    start_time = time.time()
    initial_info = session.info()

    try:
        result = session.code.run(code, language)
        execution_time = time.time() - start_time
        print(f"Execution completed in {execution_time:.2f}s")
        final_info = session.info()
        if initial_info.success and final_info.success:
            print("Session remained healthy")
        return result
    except Exception as e:
        print(f"Execution failed after {time.time() - start_time:.2f}s: {e}")
        return None
```

```typescript [TypeScript]
async function executeWithResourceMonitoring(
  session: Session, code: string, language: string,
) {
  const startTime = Date.now();
  const initialInfo = await session.info();

  try {
    const result = await session.code.run(code, language);
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(`Execution completed in ${elapsed}s`);
    const finalInfo = await session.info();
    if (initialInfo.success && finalInfo.success) {
      console.log("Session remained healthy");
    }
    return result;
  } catch (e) {
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(`Execution failed after ${elapsed}s: ${e}`);
    return null;
  }
}
```

:::

## Code Validation

::: code-group

```python [Python]
def validate_and_execute(session, code: str, language: str):
    """Validate code before execution"""
    if not code.strip():
        return {"success": False, "error": "Empty code"}

    if language not in ["python", "javascript"]:
        return {"success": False, "error": f"Unsupported language: {language}"}

    result = session.code.run(code, language)
    output = result.results[0].text if result.success and result.results else ""

    return {
        "success": result.success,
        "output": output,
        "error": result.error_message if not result.success else None,
    }
```

```typescript [TypeScript]
async function validateAndExecute(
  session: Session, code: string, language: string,
) {
  if (!code.trim()) {
    return { success: false, error: "Empty code" };
  }

  if (!["python", "javascript"].includes(language)) {
    return { success: false, error: `Unsupported language: ${language}` };
  }

  const result = await session.code.run(code, language);
  const output = result.success && result.results?.length
    ? result.results[0].text ?? ""
    : "";

  return {
    success: result.success,
    output,
    error: result.success ? null : result.errorMessage,
  };
}
```

:::
