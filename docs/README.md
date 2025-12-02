# AGB SDK Documentation

## 🎯 Quick Navigation

### 👋 New Users
- **[5-Minute Quick Start](quickstart.md)** - Experience AGB immediately
- **[Session Management](guides/session-management.md)** - Manage your automation sessions
- **[Code Execution Getting Started](guides/code-execution.md)** - The simplest use case

### 🚀 Experienced Users
- **[API Reference Documentation](api-reference/README.md)** - Complete API documentation
- **[Best Practices](guides/best-practices.md)** - Production environment usage
- **[Session Management](guides/session-management.md)** - Advanced session management

### 📋 By Use Case

| I want to... | Recommended Documentation | Example Code |
|-----------|----------|----------|
| 🤖 Browser Automation | [Browser Automation Guide](guides/browser-automation.md) | [Browser Examples](examples/browser/README.md) |
| 🧩 Browser Extensions | [Extensions API](api-reference/reference/extensions.md) | [Extensions Examples](examples/extensions/README.md) |
| 🐍 Execute Code | [Code Execution Guide](guides/code-execution.md) | [Code Examples](examples/README.md) |
| 💾 File Operations | [File Operations Guide](guides/file-operations.md) | [File Examples](examples/file_system/README.md) |
| ⚡ Execute Commands | [Command Execution Guide](guides/command-execution.md) | [Command Examples](examples/README.md) |

## 📚 Documentation Structure

### Core Guides (`guides/`)
- **[browser-automation.md](guides/browser-automation.md)** - AI-Powered Browser Automation Guide
- **[session-management.md](guides/session-management.md)** - Complete Session Management Guide
- **[code-execution.md](guides/code-execution.md)** - Code Execution Guide
- **[command-execution.md](guides/command-execution.md)** - Command Execution Guide
- **[file-operations.md](guides/file-operations.md)** - File Operations Guide
- **[best-practices.md](guides/best-practices.md)** - Best Practices and Troubleshooting

### API Reference (`api-reference/`)
- **[README.md](api-reference/README.md)** - API Overview

### Example Code (`examples/`)
- **[README.md](examples/README.md)** - Examples Overview
- **[browser/](examples/browser/README.md)** - Browser Automation Examples
- **[extensions/](examples/extensions/README.md)** - Browser Extension Examples
- **[file_system/](examples/file_system/README.md)** - File Operations Examples
- **[session_creation/](examples/session_creation/README.md)** - Session Creation Examples

## 🚀 Quick Start

### Installation
```bash
pip install agbcloud-sdk
export AGB_API_KEY="your_api_key"
```

**Important**: When using AGB, you need to specify an appropriate `image_id`. Please ensure you use valid image IDs that are available in your account. You can view and manage your available images in the [AGB Console Image Management](https://agb.cloud/console/image-management) page.

### First Example
```python
from agb import AGB
from agb.session_params import CreateSessionParams

# Create client
agb = AGB()

# Create code execution session
params = CreateSessionParams(image_id="agb-code-space-1")
session = agb.create(params).session

# Execute code
result = session.code.run_code("print('Hello AGB!')", "python")
print(result.result)

# Cleanup
agb.delete(session)
```

## 📞 Get Help

- 🐛 **[Issue Feedback](https://github.com/agbcloud/agbcloud-sdk/issues)** - Report bugs or request features
- 📖 **[Complete Quick Start](quickstart.md)** - Detailed getting started tutorial
- 🔧 **[Best Practices](guides/best-practices.md)** - Production environment usage guide

---