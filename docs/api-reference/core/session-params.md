# Session Parameters API Reference

Parameters for creating and managing sessions in the AGB cloud environment.

## CreateSessionParams Class

Parameters for creating a new session.

### Class Definition

```python
class CreateSessionParams:
    def __init__(
        self,
        image_id: Optional[str] = None,
    )
```

### Parameters

#### `image_id`
- **Type:** `Optional[str]`
- **Default:** `None`
- **Description:** ID of the image to use for the session. If not provided, defaults to "code_latest".

### Usage Examples

#### Basic Session Creation

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB(api_key="your_api_key")

# Create session with default parameters
result = agb.create()
if result.success:
    session = result.session
    print(f"Created session: {session.session_id}")
```



#### With Custom Image

```python
# Create session with specific image
params = CreateSessionParams(
    image_id="agb-code-space-1"
)

result = agb.create(params)
```

#### Complete Configuration

```python
from agb.session_params import CreateSessionParams

# Full configuration example
params = CreateSessionParams(
    image_id="agb-code-space-1"
)

result = agb.create(params)
```

**Note:** This class is defined for future functionality. Currently, the `agb.list()` method returns all sessions without filtering.

## Available Images

The following images are available for session creation:

```python
# Default images
DEFAULT_IMAGES = {
    "code_latest": "Latest general-purpose code execution environment",
    "agb-code-space-1": "Specialized code execution environment"
}
```

### Image Selection

```python
# Use default image (code_latest)
params = CreateSessionParams()

# Use specific image
params = CreateSessionParams(image_id="agb-code-space-1")
```

## Best Practices



### 1. Choose Appropriate Images
- Use `"code_latest"` for general code execution
- Use `"agb-code-space-1"` for specialized environments

### 2. Session Organization
```python
# Use meaningful image IDs for different project types
params = CreateSessionParams(
    image_id="agb-code-space-1"  # For specialized environments
)
```

## Related Content

- 🔧 **API Reference**: [AGB API](agb.md)
- 💡 **Examples**: [Session Examples](../../examples/README.md)
- 📚 **Best Practices**: [Best Practices Guide](../../guides/best-practices.md)