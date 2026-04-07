# AGB Python SDK

Client library for the AGB cloud service: create and manage sessions, run code and commands, use the file system, browser automation, and persistent context.

## Installation

```bash
pip install agbcloud-sdk
```

## Quick Start

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB(api_key="your-api-key")
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)

if result.success:
    session = result.session
    code_result = session.code.run("print('Hello AGB!')", "python")
    print(code_result.result)
    cmd_result = session.command.execute("ls -la")
    print(cmd_result.output)
    agb.delete(session)
else:
    print(result.error_message)
```

## Features

- Session management (create, list, get, delete)
- **Code** – run Python/JavaScript/Java/R in cloud
- **Command** – execute shell commands
- **File** – read, write, edit, search, transfer
- **Browser** – automation, screenshots, fingerprint
- **Computer** – mouse, keyboard, window, app, screen
- **Context** – persistent data and sync policies

## Documentation

Full docs and API reference: see the [repository documentation](../docs/README.md) (quick start, guides, API reference, examples).

## License

Apache-2.0
