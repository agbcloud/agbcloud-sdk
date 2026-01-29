<h1 align="center">AGB Python SDK</h1>

---

## 🔥 Moltbot (formerly Clawdbot) Quick Deployment

You can use AGB SDK to spin up a prebuilt Moltbot cloud desktop in minutes, then open the Moltbot console inside the desktop browser.

- **Cookbook (Discord):** [docs/examples/openclaw/openclaw_discord_config_example.py](docs/examples/openclaw/openclaw_discord_config_example.py) — create session, run openclaw config (Bailian/Discord), and get the cloud desktop URL.
- **Cookbook (Slack):** [docs/examples/openclaw/openclaw_slack_config_example.py](docs/examples/openclaw/openclaw_slack_config_example.py) — create session, run openclaw config (Bailian/Slack), and get the cloud desktop URL.
- **Cookbook (Telegram):** [docs/examples/openclaw/openclaw_telegram_config_example.py](docs/examples/openclaw/openclaw_telegram_config_example.py) — create session, run openclaw config (Bailian/Telegram), and get the cloud desktop URL.
- **Cloud Desktop URL:** The example prints `session.resource_url` and pauses for hands-on exploration.
- **Moltbot console:** Open `http://127.0.0.1:18789` inside the cloud desktop.

---

AGB Python SDK provides a convenient way to interact with the AGB cloud service.

## Features

- Create and manage sessions in the AGB cloud environment
- Access session information
- Work with file system, command execution, and code execution modules
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
    image_id="agb-code-space-1",
)
result = agb.create(params)

if result.success:
    session = result.session

    # Execute Python code
    code_result = session.code.run("print('Hello AGB!')", "python")
    print(code_result.result)

    # Execute shell command
    cmd_result = session.command.execute("ls -la")
    print(cmd_result.output)

    # Work with files
    session.file.write("/tmp/test.txt", "Hello World!")
    file_result = session.file.read("/tmp/test.txt")
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
- [User Guides](docs/README.md) - Comprehensive guides and tutorials
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
   pip install -e ."[dev,test]"
   ```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.