# Proxy configuration

Configure proxy settings for browser sessions to route traffic through custom or built-in proxies.

## What you'll do

Set up custom proxies or use AGB's built-in proxy service to manage browser traffic routing.

## Prerequisites

- `AGB_API_KEY`
- A valid browser `image_id` (e.g. `agb-browser-use-1`)
- For custom proxy: proxy server address and credentials

## Quickstart

::: code-group

```python [Python]
from agb.modules.browser import BrowserOption, BrowserProxy

proxy = BrowserProxy(
    proxy_type="custom",
    server="127.0.0.1:8080",
)
option = BrowserOption(proxies=[proxy])
```

```typescript [TypeScript]
import type { BrowserOption } from "agbcloud-sdk";

const option: BrowserOption = {
  proxies: [{
    type: "custom",
    server: "127.0.0.1:8080",
  }],
};
```

:::

## Common tasks

### Custom proxy with authentication

Configure a custom proxy server with username and password:

::: code-group

```python [Python]
from agb.modules.browser import BrowserOption, BrowserProxy

custom_proxy = BrowserProxy(
    proxy_type="custom",
    server="127.0.0.1:8080",
    username="proxy_user",
    password="proxy_pass",
)
option = BrowserOption(proxies=[custom_proxy])
```

```typescript [TypeScript]
const option: BrowserOption = {
  proxies: [{
    type: "custom",
    server: "127.0.0.1:8080",
    username: "proxy_user",
    password: "proxy_pass",
  }],
};
```

:::

### Built-in proxy (polling strategy)

Use AGB's built-in proxy with polling strategy for load balancing:

::: code-group

```python [Python]
from agb.modules.browser import BrowserOption, BrowserProxy

polling_proxy = BrowserProxy(
    proxy_type="built-in",
    strategy="polling",
    pollsize=10,
)
option = BrowserOption(proxies=[polling_proxy])
```

```typescript [TypeScript]
import { BrowserProxyClass } from "agbcloud-sdk";

const option: BrowserOption = {
  proxies: [
    new BrowserProxyClass(
      "built-in",
      undefined,
      undefined,
      undefined,
      "polling",
      10
    )
  ],
};
```

:::

### Built-in proxy (restricted strategy)

Use restricted proxy for specific geographic or access requirements:

::: code-group

```python [Python]
from agb.modules.browser import BrowserOption, BrowserProxy

restricted_proxy = BrowserProxy(
    proxy_type="built-in",
    strategy="restricted",
)
option = BrowserOption(proxies=[restricted_proxy])
```

```typescript [TypeScript]
import { BrowserProxyClass } from "agbcloud-sdk";

const option: BrowserOption = {
  proxies: [
    new BrowserProxyClass(
      "built-in",
      undefined,
      undefined,
      undefined,
      "restricted"
    )
  ],
};
```

:::

### Proxy types reference

| Type | Strategy | Description |
|------|----------|-------------|
| `custom` | - | Your own proxy server |
| `built-in` | `polling` | AGB proxy pool with round-robin selection |
| `built-in` | `restricted` | AGB proxy with access restrictions |

## Best practices

- Test proxy connectivity before production use.
- Use authentication for custom proxies in production environments.
- Consider using built-in proxies for better integration and reliability.
- Set appropriate `pollsize` for polling strategy based on your traffic needs.

## Troubleshooting

### Proxy connection failed

- **Likely cause**: Incorrect proxy server address or port.
- **Fix**: Verify the proxy server is accessible and the address format is correct (e.g., `host:port`).

### Authentication error

- **Likely cause**: Invalid username or password.
- **Fix**: Double-check credentials and ensure they're properly escaped if containing special characters.

### Timeout with built-in proxy

- **Likely cause**: Network issues or proxy pool exhaustion.
- **Fix**: Try increasing `pollsize` or retry the request.

## Related

- Main guide: [`docs/browser/overview.md`](overview.md)
- Configuration: [Browser overview](overview.md)
- Fingerprint: [`docs/browser/fingerprint.md`](fingerprint.md)
