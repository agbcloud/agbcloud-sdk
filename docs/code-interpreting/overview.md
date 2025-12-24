# Overview

The AGB SDK provides powerful code execution capabilities in the cloud. You can run Python, JavaScript, Java, and R code in isolated, secure environments without needing to install language runtimes locally. This guide covers everything from basic code execution to advanced patterns and best practices.

## Quick Reference (1 minute)

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)

if result.success:
    session = result.session

    # Execute Python code
    result = session.code.run_code("print('Hello, World!')", "python")
    print(result.result)

    # Execute JavaScript
    print(session.code.run_code("console.log('Hello World')", "javascript").result)

    agb.delete(session)
else:
    print(f"Failed to create session: {result.error_message}")
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