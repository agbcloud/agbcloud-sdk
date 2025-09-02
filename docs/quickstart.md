# Quick Start

## 🎯 Choose Your Learning Path

<details>
<summary><strong>👋 I'm a Beginner - Complete Tutorial</strong></summary>

### 1. Installation

```bash
pip install agbcloud-sdk
export AGB_API_KEY="your_key"
```

### 2. First Example

```python
from agb import AGB

# Create client
agb = AGB()

# Create code execution session
session = agb.create().session

# Execute code
result = session.code.run_code("print('Hello AGB!')", "python")
print(result.result)

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
session = agb.create(params).session

# Use different modules
# Code execution
code_result = session.code.run_code("import os; print(os.getcwd())", "python")

# Command execution
cmd_result = session.command.execute_command("ls -la")

# File operations
session.file_system.write_file("/tmp/test.txt", "Hello World!")
file_result = session.file_system.read_file("/tmp/test.txt")

# OSS cloud storage (requires configuration)
# session.oss.upload("bucket", "key", "/tmp/test.txt")

print("Code output:", code_result.result)
print("Command output:", cmd_result.output)
print("File content:", file_result.content)

agb.delete(session)
```

### 4. Next Steps

- 📚 [Session Management Guide](guides/session-management.md) - Understanding session management
- 🐍 [Code Execution Guide](guides/code-execution.md) - Deep dive into code execution
- 💾 [File Operations Guide](guides/file-operations.md) - File and directory management
- ☁️ [OSS Integration Guide](guides/oss-integration.md) - Cloud storage integration

</details>

<details>
<summary><strong>🚀 I Have Experience - Quick Start</strong></summary>

### Core Concepts

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()

# Type-safe session creation
session = agb.create().session

# Modules included in all sessions
session.code.run_code(code, "python")           # Code execution
session.command.execute_command("ls -la")       # Shell commands
session.file_system.read_file("/path/file")     # File operations
session.oss.upload("bucket", "key", "path")     # Cloud storage
```

### Key Differences

**vs Traditional Tools**:
- ✅ **Cloud Environment with No Configuration**: No need to install Python/Node.js locally
- ✅ **Unified API**: Integrated code execution, commands, files, and cloud storage
- ✅ **Session Isolation**: Independent cloud environment for each session
- ✅ **Type Safety**: Strongly typed sessions and response objects

**vs Other Cloud Services**:
- ✅ **Multi-language Support**: Python + JavaScript
- ✅ **Complete File System**: More than just code execution
- ✅ **Integrated Cloud Storage**: Built-in OSS support
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
    result = agb.create()
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
agb = AGB()  # Automatically reads AGB_API_KEY

# Custom configuration
from agb.config import Config
config = Config(
    endpoint="your-custom-endpoint.com",
    timeout_ms=60000,
)
agb = AGB(cfg=config)
```
</details>