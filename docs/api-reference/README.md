# AGB SDK API Reference

Complete technical API documentation for developers. This reference covers all classes, methods, parameters, and return types in the AGB SDK.

## 🚀 Quick Reference

### Core API Pattern
```python
from agb import AGB
from agb.session_params import CreateSessionParams

# Client initialization
agb = AGB()  # Uses AGB_API_KEY environment variable

# Session lifecycle
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
session = result.session

# Module usage
session.code.run_code(code, language, timeout_s=300)
session.command.execute_command(command, timeout_ms=1000)
session.file_system.read_file(path)

# Cleanup
agb.delete(session)
```

## 📚 API Documentation

### 🏗️ Core Classes

| Class | Purpose | Documentation |
|-------|---------|---------------|
| **[AGB](01_agb.md)** | Main SDK client | Session creation and management |
| **[Session](02_session.md)** | Session management | Session lifecycle and information |
| **[CreateSessionParams](reference/configurations.md)** | Session configuration | Parameters for session creation |
| **[ExtensionsService](reference/extensions.md)** | Extension management | Browser extension lifecycle |
| **[ExtensionOption](reference/extensions.md#extensionoption)** | Extension configuration | Browser extension integration |

### 🔧 Modules

| Module | Purpose | Documentation |
|--------|---------|---------------|
| **[Code](capabilities/code_execution.md)** | Code execution | Python, JavaScript, Java, R execution |
| **[Command](capabilities/shell_commands.md)** | Shell commands | Command execution and output |
| **[FileSystem](capabilities/file_system.md)** | File operations | File and directory management |
| **[Browser](capabilities/browser.md)** | Web automation | Browser automation and web scraping |

### 📊 Response Types

| Response Type | Purpose | Documentation |
|---------------|---------|---------------|
| **[SessionResult](reference/types.md#sessionresult)** | Session creation results | Success status and session object |
| **[DeleteResult](reference/types.md#deleteresult)** | Session deletion results | Deletion status and request ID |
| **[CodeExecutionResult](reference/types.md#codeexecutionresult)** | Code execution results | Output, success status, and errors |
| **[CommandResult](reference/types.md#commandresult)** | Command execution results | Command output and execution status |
| **[FileContentResult](reference/types.md#filecontentresult)** | File read results | File content and metadata |
| **[DirectoryListResult](reference/types.md#directorylistresult)** | Directory listing results | Directory entries and metadata |
| **[FileInfoResult](reference/types.md#fileinforesult)** | File info results | File metadata and properties |
| **BoolResult** | Boolean operation results | Success/failure status for operations |


## 🎯 API Categories

### Session Management API
```python
# AGB class methods
agb.create(params=None) -> SessionResult
agb.list() -> List[BaseSession]
agb.delete(session) -> DeleteResult

# Session methods
session.info() -> OperationResult
session.get_session_id() -> str
session.get_api_key() -> str
```

### Extension Management API
```python
# ExtensionsService methods
from agb.extension import ExtensionsService

# Initialize extension service
extensions_service = ExtensionsService(agb, context_id="my_extensions")

# Extension lifecycle
extension = extensions_service.create(local_path="/path/to/extension.zip")
extensions = extensions_service.list()
updated_extension = extensions_service.update(extension_id, new_local_path)
success = extensions_service.delete(extension_id)

# Extension integration with browser sessions
ext_option = extensions_service.create_extension_option([extension1.id, extension2.id])
```

### Code Execution API
```python
# Code module methods
session.code.run_code(
    code: str,
    language: str,
    timeout_s: int = 300
) -> CodeExecutionResult
```

### Command Execution API
```python
# Command module methods
session.command.execute_command(
    command: str,
    timeout_ms: int = 1000
) -> CommandResult
```

### File System API
```python
# FileSystem module methods
session.file_system.read_file(path: str) -> FileContentResult
session.file_system.write_file(path: str, content: str) -> BoolResult
session.file_system.read_multiple_files(paths: List[str]) -> MultipleFileContentResult
session.file_system.list_directory(path: str) -> DirectoryListResult
session.file_system.create_directory(path: str) -> BoolResult
session.file_system.get_file_info(path: str) -> FileInfoResult
session.file_system.move_file(source: str, destination: str) -> BoolResult
session.file_system.edit_file(path: str, edits: List[dict]) -> BoolResult
session.file_system.search_files(path: str, pattern: str) -> FileSearchResult
session.file_system.watch_directory(path: str, callback: Callable, interval: float = 1.0, stop_event: Optional[threading.Event] = None) -> threading.Thread
```


### Browser API
```python
# Browser module methods
session.browser.initialize(option: BrowserOption) -> bool
session.browser.get_endpoint_url() -> str
session.browser.is_initialized() -> bool
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
export AGB_API_KEY="your_api_key_here"

# Optional
export AGB_ENDPOINT="sdk-api.agb.cloud"
export AGB_TIMEOUT_MS="60000"
```

### Client Configuration
```python
from agb import AGB
from agb.config import Config

# Default configuration (recommended)
agb = AGB()

# Custom configuration
config = Config(
    endpoint="your-custom-endpoint.com",
    timeout_ms=60000,
)
agb = AGB(api_key="your_key", cfg=config)
```

## 📋 Session Capabilities

### Available Modules
All sessions provide access to the following modules:

```python
# All sessions have these capabilities
session.code         # ✅ Python, JavaScript, Java, R execution
session.command      # ✅ Shell command execution
session.file_system  # ✅ File & directory operations
session.browser      # ✅ Web browser automation
```

## 🚨 Error Handling

### Common Response Pattern
```python
class ApiResponse:
    request_id: str      # Unique request identifier
    success: bool        # Operation success status
    error_message: str   # Error description if failed
```

### Error Handling Examples
```python
from agb import AGB
from agb.session_params import CreateSessionParams

# Session creation error handling
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if not result.success:
    print(f"Error: {result.error_message}")
    print(f"Request ID: {result.request_id}")

# Module operation error handling
code_result = session.code.run_code("invalid code", "python")
if not code_result.success:
    print(f"Execution failed: {code_result.error_message}")
    # Partial output may still be available
    if code_result.result:
        print(f"Partial output: {code_result.result}")
```

## 📖 Detailed Documentation

### Core Classes
- **[AGB Client](01_agb.md)** - Main SDK client class
- **[Session Management](02_session.md)** - Session lifecycle and operations
- **[Session Parameters](reference/configurations.md)** - Configuration options
- **[Extensions API](reference/extensions.md)** - Browser extension management

### Modules
- **[Code Execution](capabilities/code_execution.md)** - Python, JavaScript, Java, R execution
- **[Command Execution](capabilities/shell_commands.md)** - Shell command operations
- **[File System](capabilities/file_system.md)** - File and directory management
- **[Browser Automation](capabilities/browser.md)** - Web browser automation and scraping

### Response Types
- **[Session Responses](reference/types.md#sessionresult)** - Session operation results
- **[Execution Responses](reference/types.md)** - Code and command results
- **[File System Responses](reference/types.md)** - File operation results

## 🔗 Related Documentation

- **[User Guides](../guides/README.md)** - Task-oriented usage guides
- **[Examples](../examples/README.md)** - Practical code examples
- **[Getting Started](../quickstart.md)** - Quick start tutorial

## 📞 Developer Support

For API-specific questions:
- 📖 Check the detailed class documentation above
- 💡 Review [practical examples](../examples/README.md)
- 🐛 [Report API issues](https://github.com/agbcloud/agbcloud-sdk/issues)