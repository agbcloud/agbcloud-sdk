# AGB SDK Examples

Practical, runnable examples demonstrating the capabilities of the AGB SDK.

## Example Catalog

| Category | Example | Description |
|----------|---------|-------------|
| **Start Here** | [**Session Management**](session_management/README.md) | Create, retrieve, and manage session lifecycle. |
| | [**Code Execution**](code_execution/README.md) | Run Python, JavaScript, Java, and R code. |
| | [**Command Execution**](command_execution/README.md) | Execute shell commands and system tools. |
| | [**File Operations**](file_system/README.md) | Read, write, upload, and manage files in the cloud. |
| **Browser** | [**Basic Navigation**](browser/README.md) | Open URLs, click buttons, and take screenshots. |
| | [**Data Extraction**](browser/README.md) | Extract structured data from web pages using AI. |
| | [**Browser Examples**](browser/README.md) | Full list of browser automation examples. |
| **Advanced** | [**Browser Extensions**](extensions/README.md) | Load and manage Chrome extensions in your sessions. |
| | [**Context Sync**](data_persistence/README.md) | Sync local context to remote sessions. |
| | [**Directory Monitoring**](directory_monitoring/README.md) | Watch for file changes in real-time. |

## How to Run

1. **Install the SDK**:
   ```bash
   pip install agbcloud-sdk
   ```

2. **Set your API Key**:
   ```bash
   export AGB_API_KEY="your_api_key_here"
   ```

3. **Run a script**:
   ```bash
   # Run from the project root
   python docs/examples/session_management/create_session.py
   ```

## Key Concepts Demonstrated

- **Session Lifecycle**: All examples show proper `create` -> `use` -> `delete` patterns.
- **Error Handling**: Check `result.success` and handle `result.error_message`.
- **Resource Management**: Use `try...finally` blocks to ensure sessions are cleaned up.

## Troubleshooting

- **Authentication Error**: Double-check your `AGB_API_KEY`.
- **Image ID Error**: Ensure you are using a valid `image_id` (e.g., `agb-code-space-1` or `agb-browser-use-1`).
- **Timeout Error**: Some operations might take longer depending on network conditions; try increasing timeout values.

## Contributing

Have a useful example? We'd love to include it! Please ensure your example is:
- **Self-contained**: Runnable without external dependencies.
- **Well-documented**: Clear comments and explanations.
- **Error-handled**: Proper error checking and cleanup.
