# Quick Start

## 👋 I'm a Beginner - Complete Tutorial

### 1. Installation

```bash
pip install agbcloud-sdk
export AGB_API_KEY="your_key"
```

### 2. First Example
**Important**: When using AGB, you need to specify an appropriate `image_id`. Please ensure you use valid image IDs that are available in your account. You can view and manage your available images in the [AGB Console Image Management](https://agb.ai/console/image-management) page.

```python
from agb import AGB
from agb.session_params import CreateSessionParams

# Create client
agb = AGB()

# Create code execution session
params = CreateSessionParams(image_id="agb-code-space-1")
result =agb .create(params)
if not result.success:
    print(f"✅ Session created failed: {result.error_message}")
    exit(1)

session = result.session

# Execute code
result = session.code.run("print('Hello AGB!')", "python")
# Print execution results
if result.success and result.results:
    for exec_result in result.results:
        if exec_result.text:
            print(exec_result.text)

# Cleanup
agb.delete(session)
```


### 3. Explore More Features

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()

# Create session with custom image
params = CreateSessionParams(
    image_id="agb-code-space-1"
)
result = agb.create(params)
if not result.success:
    print(f"Session creation failed: {result.error_message}")
    exit(1)
session = result.session

# Use different modules
# Code execution
code_result = session.code.run("import os; print(os.getcwd())", "python")

# Command execution
cmd_result = session.command.execute("ls -la")

# File operations
session.file.write("/tmp/test.txt", "Hello World!")
file_result = session.file.read("/tmp/test.txt")


# Print results with proper handling
if code_result.success and code_result.results:
    print("Code output:", code_result.results[0].text if code_result.results else "No output")
print("Command output:", cmd_result.output)
print("File content:", file_result.content)

agb.delete(session)
```

### 4. Next Steps

- 📚 [Session Management Guide](/session/overview.md) - Understanding session management
- 🐍 [Code Execution Guide](/code-interpreting/overview.md) - Deep dive into code execution
- 💾 [File Operations Guide](/file-system/overview.md) - File and directory management


## 🚀 I Have Experience - Quick Start

### Core Concepts

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()

# Type-safe session creation
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if not result.success:
    print(f"Session creation failed: {result.error_message}")
    exit(1)
session = result.session

# Modules included in all sessions
session.code.run(code, "python")           # Code execution
session.command.execute("ls -la")       # Shell commands
session.file.read("/path/file")     # File operations
```

### Key Differences

**vs Traditional Tools**:
- ✅ **Cloud Environment with No Configuration**: No need to install Python/Node.js locally
- ✅ **Unified API**: Integrated code execution, commands, files, and cloud storage
- ✅ **Session Isolation**: Independent cloud environment for each session
- ✅ **Type Safety**: Strongly typed sessions and response objects

**vs Other Cloud Services**:
- ✅ **Multi-language Support**: Python + JavaScript + Java + R
- ✅ **Complete File System**: More than just code execution
- ✅ **Command Line Access**: Full shell environment

### Advanced Usage

```python
# Session management
params = CreateSessionParams(
    image_id="agb-code-space-1"
)

# Error handling
result = agb.create(params)
if result.success:
    session = result.session
    # Use session...
else:
    print(f"Creation failed: {result.error_message}")

# Batch operations
sessions = []
for i in range(3):
    params = CreateSessionParams(image_id="agb-code-space-1")
    result = agb.create(params)
    if result.success:
        sessions.append(result.session)

# Clean up all sessions
for session in sessions:
    agb.delete(session)
```

### Production Environment Configuration

```python
import os

# Environment variable configuration
agb = AGB()

# Custom configuration
from agb.config import Config
config = Config(
    endpoint="your-custom-endpoint.com",
    timeout_ms=60000,
)
agb = AGB(cfg=config)
```