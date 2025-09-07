# AGB Python SDK

AGB Python SDK provides a convenient way to interact with the AGB cloud service.

## Features

- Create and manage sessions in the AGB cloud environment
- Access session information
- Work with file system, command execution, code execution, and OSS storage modules
- Browser automation with AI-powered natural language operations
- Advanced browser configuration (stealth mode, proxies, fingerprinting)
- Structured data extraction from web pages

## Installation

```bash
pip install agbcloud-sdk
```

## Quick Start

```python
from agb import AGB
from agb.session_params import CreateSessionParams

# Initialize AGB with your API key
agb = AGB(api_key="your-api-key")

# Create a session
params = CreateSessionParams(
    image_id="agb-code-space-2",
    labels={"environment": "development", "project": "example"}
)
result = agb.create(params)

if result.success:
    session = result.session

    # Execute Python code
    code_result = session.code.run_code("print('Hello AGB!')", "python")
    print(code_result.result)

    # Execute shell command
    cmd_result = session.command.execute_command("ls -la")
    print(cmd_result.output)

    # Work with files
    session.file_system.write_file("/tmp/test.txt", "Hello World!")
    file_result = session.file_system.read_file("/tmp/test.txt")
    print(file_result.content)

    # Clean up
    agb.delete(session)
else:
    print(f"Failed to create session: {result.error_message}")
```

## Documentation

For comprehensive documentation, guides, and examples, visit:

📚 **[Complete Documentation](docs/README.md)**

- [Quick Start Guide](docs/quickstart.md) - Get started quickly with basic examples
- [User Guides](docs/guides/README.md) - Comprehensive guides and tutorials
- [API Reference](docs/api-reference/README.md) - Detailed API documentation
- [Examples](docs/examples/README.md) - Practical usage examples

## Development

### Prerequisites

- Python 3.10 or higher
- pip

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/agbcloud/agbcloud-sdk.git
   cd agbcloud-sdk
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .[dev,test]
   ```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.