# Best practices

## Always Clean Up Sessions

```python
from agb import AGB
from agb.session_params import CreateSessionParams

# ✅ Good: Always delete sessions
agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)

if result.success:
    session = result.session

    try:
    # Your code here
        session.code.run("print('Hello')", "python")
    finally:
        agb.delete(session)
else:
    print(f"Failed to create session: {result.error_message}")

# ✅ Better: Use context manager pattern
class SessionContext:
    def __init__(self, agb: AGB):
        self.agb = agb
        self.session = None

    def __enter__(self):
        params = CreateSessionParams(image_id="agb-code-space-1")
        result = self.agb.create(params)
        if not result.success:
            raise Exception(f"Failed to create session: {result.error_message}")
        self.session = result.session
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.agb.delete(self.session)

# Usage
agb = AGB()
with SessionContext(agb) as session:
    session.code.run("print('Hello')", "python")
# Session automatically cleaned up
```

## Handle Errors Gracefully

```python
from agb import AGB
from agb.session_params import CreateSessionParams

def safe_session_operation(agb: AGB, operation_func):
    """Safely execute an operation with proper error handling"""
    params = CreateSessionParams(image_id="agb-code-space-1")
    result = agb.create(params)
    if not result.success:
        return {"success": False, "error": result.error_message}

    session = result.session

    try:
        return operation_func(session)
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        try:
            agb.delete(session)
        except Exception as cleanup_error:
            print(f"Warning: Failed to cleanup session: {cleanup_error}")

# Usage
def my_operation(session):
    result = session.code.run("print('Hello')", "python")
    output = result.results[0].text if result.success and result.results else ""
    return {"success": result.success, "output": output}

agb = AGB()
result = safe_session_operation(agb, my_operation)
print(result)
```

## Use Labels for Organization

```python
from agb import AGB
from agb.session_params import CreateSessionParams

# ✅ Good: Organize sessions with meaningful labels
params = CreateSessionParams(
    image_id="agb-code-space-1",
    labels={
        "project": "data-pipeline",
        "environment": "production",
        "team": "analytics",
        "version": "v2.1.0"
    }
)

result = agb.create(params)

if result.success:
    session = result.session

    # ✅ Better: Use consistent labeling strategy
    class LabelManager:
        @staticmethod
        def create_project_labels(project_name: str, environment: str, **kwargs):
            """Create standardized labels for project sessions"""
            labels = {
                "project": project_name,
                "environment": environment,
                "created_by": "agb-sdk",
                "timestamp": str(int(time.time()))
            }
            labels.update(kwargs)
            return labels

    # Usage
    labels = LabelManager.create_project_labels(
        "ml-training",
        "staging",
        model_version="v1.3.2",
        gpu_enabled="true"
    )

    params = CreateSessionParams(image_id="agb-code-space-1", labels=labels)
    result = agb.create(params)

    if result.success:
        session = result.session

        # Update labels during session lifecycle
session.set_labels({
    **labels,
    "status": "training_complete",
    "accuracy": "0.94"
})
```

## Monitor Resource Usage

```python
from contextlib import contextmanager

@contextmanager
def monitor_session_usage(session, operation_name: str):
    """Monitor session resource usage during operations"""
    start_time = time.time()

    # Get initial session info
    initial_info = session.info()

    try:
        # Your operation here
        yield session
    finally:
        # Get final session info
        final_info = session.info()
        duration = time.time() - start_time

        print(f"Operation '{operation_name}' completed in {duration:.2f}s")
        if initial_info.success and final_info.success:
            print("Session remained healthy throughout operation")

# Usage
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)

if result.success:
    session = result.session

    with monitor_session_usage(session, "data_processing") as monitored_session:
        monitored_session.code.run("import pandas as pd; print('Processing data...')", "python")

    agb.delete(session)
else:
    print(f"Failed to create session: {result.error_message}")
```
