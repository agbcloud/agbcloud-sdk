# AGB SDK Documentation

Welcome to the comprehensive documentation for the AGB SDK.

## Core Concept: The Session

Sessions are the fundamental building blocks of the AGB SDK. A session represents an isolated, secure cloud environment (sandbox) that provides **tools and execution context** for your AI agents. Instead of running locally, your agents use sessions to securely execute code, run shell commands, browse the web, and manage files in the cloud.

### Supported Environments

Unlike other sandboxes that only support code execution, AGB provides specialized environments (Images) tailored for different AI agent capabilities:

| Environment Type | Image ID Pattern | Key Capabilities | Ideal For |
| :--- | :--- | :--- | :--- |
| **Code Space** | `agb-code-space-*` | - Python, Node.js, Java, R runtimes<br>- Shell access & File system<br>- Pre-installed data science libs | Data analysis, Code interpretation, Math solving, Backend logic. |
| **Browser Use** | `agb-browser-use-*` | - **Headless Browser** automation<br>- AI-driven navigation & extraction<br>- Chrome Extension support | Web scraping, UI testing, Web-browsing agents, Data extraction. |
| **Computer Use** | *(Beta)* | - coordinate-based mouse/keyboard control<br>- window/app management<br>- screenshot capture | Desktop application operations, Software automation testing, Document processing tasks. |

### Session Lifecycle

Understanding the lifecycle of a session is crucial for resource management and cost control.

1.  **Creation**: AGB allocates a fresh cloud environment based on your specified `image_id`.
2.  **Active**: The session maintains state (files, variables, processes) between operations.
3.  **Timeout (Auto-Shutdown)**: Sessions are automatically reclaimed after **30 minutes** of inactivity by default to prevent runaway costs.
4.  **Deletion**: Explicitly deleting a session releases resources immediately.

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()

# Example: Create a Code Execution Session
code_params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(code_params)

if result.success:
    code_session = result.session

    # ... perform operations ...

    # Clean up
    agb.delete(code_session)
else:
    print(f"Failed to create session: {result.error_message}")
```

### Key Capabilities

-   **Labels**: Tag sessions with custom key-value pairs (e.g., `user_id`, `env`) for organization and filtering.
-   **Networking**: Use `session.get_link(port=30100)` to expose internal services (like TensorBoard or web apps) securely to the public internet.
-   **Data Persistence**: By default, session storage is ephemeral. Use **Context Sync** to synchronize local files with the remote session automatically.
-   **Resource Monitoring**: Retrieve real-time status and resource usage via `session.info()`.

---

## Quick Start

Master the fundamental building blocks of AGB.

-   **[Quick Start](quickstart.md)**
    5-minute path: install the SDK, create your first session, and run a sample task.

-   **[API key](api-key.md)**
    Create AGB API keys for SDK and CLI use.

-   **[MCP Guide](mcp-guide.md)**
    Set up MCP servers, configure tools, and connect agents to AGB sessions via MCP.


## ⚙️ API Reference

Low-level API documentation.

-   **[API Reference Index](api-reference/README.md)**
