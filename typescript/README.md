# AGB TypeScript SDK

Client library for the AGB cloud service: create and manage sessions, run code and commands, use the file system, browser automation, and persistent context.

## Installation

```bash
npm install agbcloud-sdk
```

## Quick Start

```typescript
import { AGB, CreateSessionParams } from "agbcloud-sdk";

const agb = new AGB({ apiKey: "your-api-key" });
const params = new CreateSessionParams({ imageId: "agb-code-space-1" });
const result = await agb.create(params);

if (result.success && result.session) {
  const session = result.session;
  const codeResult = await session.code.run("print('Hello AGB!')", "python");
  console.log(codeResult.results[0]?.text);
  const cmdResult = await session.command.execute("ls -la");
  console.log(cmdResult.stdout);
  await agb.delete(session);
} else {
  console.error(result.errorMessage);
}
```

## Features

- Session management (create, list, get, delete)
- **Code** – run Python/JavaScript/Java/R in cloud
- **Command** – execute shell commands
- **File** – read, write, edit, search, transfer
- **Browser** – automation, screenshots, fingerprint, BrowserAgent
- **Computer** – mouse, keyboard, window, app, screen
- **Context** – persistent data and sync policies

## Documentation

Full docs and API reference: see the [repository documentation](../docs/README.md) (quick start, guides, API reference, examples).

## License

Apache-2.0
