# AI Agent operations

## What you’ll do

Control web pages using AGB’s AI Agent with three core operations:

- **Act**: perform actions from natural language instructions
- **Observe**: find/describe interactable elements
- **Extract**: extract structured data using a schema

## Prerequisites

- `AGB_API_KEY`
- A valid browser `image_id` (e.g. `agb-browser-use-1`)
- A Playwright `page` connected via CDP (see [`docs/browser/overview.md`](overview.md))

## Quickstart

```python
from agb.modules.browser import ActOptions

act_result = await session.browser.agent.act_async(
    ActOptions(action="Click the login button"),
    page,
)
print(act_result.success, act_result.message)
```

## Common tasks

### Act: perform actions

```python
from agb.modules.browser import ActOptions

await session.browser.agent.act_async(ActOptions(action="Scroll down and click 'Load more'"), page)
```

### Observe: analyze the page

```python
from agb.modules.browser import ObserveOptions

success, results = await session.browser.agent.observe_async(
    ObserveOptions(instruction="Find all clickable buttons and links on the page"),
    page,
)

if success:
    for r in results:
        print(r.description, r.selector, r.method)
```

### Extract: structured data

```python
from typing import List
from pydantic import BaseModel
from agb.modules.browser import ExtractOptions


class Product(BaseModel):
    name: str
    price: str
    rating: float
    availability: str


class ProductList(BaseModel):
    products: List[Product]


success, data = await session.browser.agent.extract_async(
    ExtractOptions(
        instruction="Extract all product information from this page",
        schema=ProductList,
        use_text_extract=True,
    ),
    page,
)

if success and data:
    for p in data.products:
        print(p.name, p.price)
```

## Best practices

- Be explicit in instructions (what to click, how to identify it, what to do next).
- For dynamic pages, ask the agent to wait for content to load before acting.

## Troubleshooting

### Agent actions fail

- **Likely cause**: ambiguous instructions or page not fully loaded.
- **Fix**: add constraints (“button with text…”) and ask the agent to observe page state first.

## Related

- Main guide: [`docs/browser/overview.md`](overview.md)
- API reference: [`docs/api-reference/capabilities/browser.md`](../api-reference/capabilities/browser.md)

