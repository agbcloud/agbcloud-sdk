<h1 align="center">AGB Python SDK</h1>
<h4 align="center">
  <a href="https://pypi.org/project/agbcloud-sdk/">
    <img alt="Last 1 month downloads for the Python SDK" loading="lazy" decoding="async" style="color:transparent;width:170px;height:18px" src="https://static.pepy.tech/personalized-badge/agbcloud-sdk?period=monthly&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=PyPi%20Monthly%20Downloads">
  </a>
</h4>

---

## 🔥 Moltbot (formerly Clawdbot) Quick Deployment

You can use AGB SDK to spin up a prebuilt Moltbot cloud desktop in minutes, then open the Moltbot console inside the desktop browser.

- **Cookbook (Discord):** [docs/examples/openclaw/openclaw_discord_config_example.py](docs/examples/openclaw/openclaw_discord_config_example.py) — create session, run openclaw config (Bailian/Discord), and get the cloud desktop URL.
- **Cookbook (Slack):** [docs/examples/openclaw/openclaw_slack_config_example.py](docs/examples/openclaw/openclaw_slack_config_example.py) — create session, run openclaw config (Bailian/Slack), and get the cloud desktop URL.
- **Cookbook (Telegram):** [docs/examples/openclaw/openclaw_telegram_config_example.py](docs/examples/openclaw/openclaw_telegram_config_example.py) — create session, run openclaw config (Bailian/Telegram), and get the cloud desktop URL.
- **Cloud Desktop URL:** The example prints `session.resource_url` and pauses for hands-on exploration.
- **Moltbot console:** Open `http://127.0.0.1:18789` inside the cloud desktop.

---

AGB Cloud SDK provides client libraries for interacting with the AGB cloud service.

## Features

- Create and manage sessions in the AGB cloud environment
- Work with file system, command execution, and code execution modules
- Browser automation with AI-powered natural language operations
- Persistent context management with sync policies

### 🎯 Scenario-Based Features
- **Computer Use** - Linux computer control (mouse, keyboard, window, application, screen)
- **Browser Use** - Web automation, scraping, and browser control
- **CodeSpace** - Code execution and development environment

## Installation

```bash
# Python
pip install agbcloud-sdk

# TypeScript
npm install agbcloud-sdk
```

## Quick Start

### Python

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

### TypeScript

```typescript
import { AGB, CreateSessionParams } from "agbcloud-sdk";

// Initialize AGB with your API key
const agb = new AGB({ apiKey: "your-api-key" });

// Create a session
const params = new CreateSessionParams({ imageId: "agb-code-space-1" });
const result = await agb.create(params);

if (result.success && result.session) {
  const session = result.session;

  // Execute Python code
  const codeResult = await session.code.run("print('Hello AGB!')", "python");
  console.log(codeResult.results[0]?.text);

  // Execute shell command
  const cmdResult = await session.command.execute("ls -la");
  console.log(cmdResult.stdout);

  // Work with files
  await session.file.writeFile("/tmp/test.txt", "Hello World!");
  const fileResult = await session.file.readFile("/tmp/test.txt");
  console.log(fileResult.content);

  // Clean up
  await agb.delete(session);
} else {
  console.error(`Failed to create session: ${result.errorMessage}`);
}
```

## Documentation

For comprehensive documentation, guides, and examples, visit:

📚 **[Complete Documentation](docs/README.md)**

- [Quick Start Guide](docs/quickstart.md) - Get started quickly with basic examples
- [User Guides](docs/README.md) - Comprehensive guides and tutorials
- [API Reference](docs/api-reference/README.md) - Detailed API documentation
- [Examples](docs/examples/README.md) - Practical usage examples

## Development

### Python

```bash
cd python
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev,test]"
```

### TypeScript

```bash
cd typescript
npm install
npm run build
npm test
```

## Get Help
- [GitHub Issues](https://github.com/agbcloud/agbcloud-sdk/issues)

## Contact
Welcome to visit our product website and join our community!

- **AGB Product Website**: [https://agb.cloud/](https://agb.cloud/)
- **AGB Console**: [https://agb.cloud/console/overview](https://agb.cloud/console/overview)
- **Discord Community**: [Join on Discord](https://discord.gg/WQ2EHJxhy7)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
