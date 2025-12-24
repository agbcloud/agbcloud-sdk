# Browser automation guide

Welcome to the AGB Browser Automation Guide! This comprehensive guide covers everything you need to know about using AGB's powerful browser automation capabilities.

## 🎯 Quick Navigation

- [Getting Started](#getting-started) - Basic setup and first browser session
- [Browser Configuration](#browser-configuration) - Customizing browser behavior
- [AI Agent Operations](#ai-agent-operations) - Using natural language automation
- [Advanced Features](#advanced-features) - Proxy, stealth mode, fingerprinting, and extensions
- [Best Practices](#best-practices) - Tips for reliable automation
- [Troubleshooting](#troubleshooting) - Common issues and solutions

## 🚀 What is AGB Browser Automation?

AGB Browser Automation provides a managed platform for running headless/non-headless browsers at scale. It combines traditional browser automation with AI-powered natural language operations, making it easy to automate complex web workflows.

### Key Features

- **Playwright/Puppeteer Compatible**: Connect via CDP (Chrome DevTools Protocol)
- **AI-Powered Operations**: Execute tasks using natural language descriptions
- **Advanced Configuration**: Stealth mode, proxy support, fingerprint customization
- **Scalable Infrastructure**: Cloud-managed sessions with elastic resource allocation
- **Rich API**: Clean primitives for browser lifecycle and agent operations

## Getting Started

### Prerequisites

- Python 3.10 or higher
- AGB API key (set as `AGB_API_KEY` environment variable)
- Playwright installed: `pip install playwright && python -m playwright install chromium`

### Basic Browser Session

Here's a minimal example to get you started:

```python
import os
import asyncio
from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser import BrowserOption
from playwright.async_api import async_playwright

async def main():
    # Initialize AGB client
    api_key = os.getenv("AGB_API_KEY")
    agb = AGB(api_key=api_key)

    # Create a session with browser support
    params = CreateSessionParams(image_id="agb-browser-use-1")
    result = agb.create(params)

    if not result.success:
        raise RuntimeError(f"Failed to create session: {result.error_message}")

    session = result.session

    # Initialize browser
    success = await session.browser.initialize_async(BrowserOption())
    if not success:
        raise RuntimeError("Browser initialization failed")

    # Get CDP endpoint and connect Playwright
    endpoint_url = session.browser.get_endpoint_url()

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(endpoint_url)
        page = await browser.new_page()

        # Navigate and interact
        await page.goto("https://example.com")
        title = await page.title()
        print(f"Page title: {title}")

        await browser.close()

    # Clean up
    agb.delete(session)

if __name__ == "__main__":
    asyncio.run(main())
```

## Browser Configuration

### Basic Configuration Options

The `BrowserOption` class provides comprehensive configuration for your browser instance:

```python
from agb.modules.browser import (
    BrowserOption, BrowserViewport, BrowserScreen,
    BrowserFingerprint, BrowserProxy
)

# Basic configuration
option = BrowserOption(
    use_stealth=True,
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    viewport=BrowserViewport(width=1366, height=668),
    screen=BrowserScreen(width=1920, height=1080)
)
```

### Viewport and Screen Settings

Control how your browser appears to websites:

```python
# Mobile viewport
mobile_option = BrowserOption(
    viewport=BrowserViewport(width=375, height=667),
    screen=BrowserScreen(width=375, height=667),
    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
)

# Desktop viewport
desktop_option = BrowserOption(
    viewport=BrowserViewport(width=1920, height=1080),
    screen=BrowserScreen(width=1920, height=1080)
)
```

### Proxy Configuration

#### Custom Proxy

```python
custom_proxy = BrowserProxy(
    proxy_type="custom",
    server="127.0.0.1:8080",
    username="proxy_user",
    password="proxy_pass"
)

option = BrowserOption(proxies=[custom_proxy])
```

#### Built-in Proxy

```python
# Polling strategy
polling_proxy = BrowserProxy(
    proxy_type="built-in",
    strategy="polling",
    pollsize=10
)

# Restricted strategy
restricted_proxy = BrowserProxy(
    proxy_type="built-in",
    strategy="restricted"
)
```

### Browser Type Selection

Choose between Chrome and Chromium browsers (only available for computer use images):

```python
# Use Google Chrome
chrome_option = BrowserOption(browser_type="chrome")

# Use Chromium (open-source)
chromium_option = BrowserOption(browser_type="chromium")

# Use Default (Chromium)
default_option = BrowserOption()
```

**Note:** chrome only support for computer use image

### Custom Command Arguments

Pass custom command-line arguments to the browser:

```python
# Disable specific Chrome features
option = BrowserOption(
    cmd_args=[
        "--disable-features=PrivacySandboxSettings4",
        "--disable-notifications",
        "--no-first-run"
    ]
)
```

### Default Navigation URL

Set a default URL for the browser to navigate to on startup:

```python
# Useful for debugging: navigate to Chrome version page
debug_option = BrowserOption(
    default_navigate_url="chrome://version/"
)
```

**Note:** For Browser Initialize operations, it's **highly recommended** to use Chrome internal pages (e.g., `chrome://version/`, `chrome://settings/`) or extension pages instead of internet URLs. Navigating to internet pages during initialization may cause timeout of browser launch.

## AI Agent Operations

AGB's AI Agent allows you to control browsers using natural language, making complex automation tasks much simpler.

### The Three Core Operations

#### 1. Act - Perform Actions

Execute actions on web pages using natural language:

```python
from agb.modules.browser import ActOptions

# Simple click action
act_result = await session.browser.agent.act_async(ActOptions(
    action="Click the login button"
), page)


# Complex interactions
act_result = await session.browser.agent.act_async(ActOptions(
    action="Scroll down to find the 'Load More' button and click it"
), page)

print(f"Action result: {act_result.success} - {act_result.message}")
```

#### 2. Observe - Analyze Page Content

Observe and analyze page elements:

```python
from agb.modules.browser import ObserveOptions

# Find interactive elements
success, results = await session.browser.agent.observe_async(ObserveOptions(
    instruction="Find all clickable buttons and links on the page"
), page)

if success:
    for result in results:
        print(f"Found: {result.description}")
        print(f"Selector: {result.selector}")
        print(f"Action: {result.method}")
```

#### 3. Extract - Get Structured Data

Extract structured information from web pages:

```python
from agb.modules.browser import ExtractOptions
from pydantic import BaseModel
from typing import List

# Define data structure
class Product(BaseModel):
    name: str
    price: str
    rating: float
    availability: str

class ProductList(BaseModel):
    products: List[Product]

# Extract data
success, data = await session.browser.agent.extract_async(ExtractOptions(
    instruction="Extract all product information from this e-commerce page",
    schema=ProductList,
    use_text_extract=True
), page)

if success and data:
    for product in data.products:
        print(f"Product: {product.name} - ${product.price}")
```

### Advanced Agent Configuration

```python
# With iframe support and custom timeouts
act_result = await session.browser.agent.act_async(ActOptions(
    action="Navigate through the multi-step checkout process"
), page)

# Selective extraction with CSS selector
success, data = await session.browser.agent.extract_async(ExtractOptions(
    instruction="Extract pricing information from the product cards",
    schema=ProductList,
), page)
```

## Advanced Features

### Fingerprint

Enable Fingerprint feature to avoid bot detection, the following is a basic fingerprint feature's config. For more advanced fingerprint feature descriptions, please refer to the [Browser Fingerprint](./fingerprint.md)
**Note:** `use_stealth` needs to be set to true to enable the fingerprint feature

```python
stealth_option = BrowserOption(
    use_stealth=True,
    fingerprint=BrowserFingerprint(
        devices=["desktop"],
        operating_systems=["windows"],
        locales=["en-US"]
    )
)
```

### Browser Extensions

AGB supports loading Chrome extensions into browser sessions, allowing you to automate workflows that require specific browser functionality.

#### Uploading and Managing Extensions

Use the `ExtensionsService` to manage browser extensions:

```python
from agb.extension import ExtensionsService

# Initialize extension service
extensions_service = ExtensionsService(agb, "my_browser_extensions")

# Upload an extension from a ZIP file
extension = extensions_service.create("/path/to/my-extension.zip")
print(f"Uploaded extension: {extension.id}")

# List all extensions
extensions = extensions_service.list()
for ext in extensions:
    print(f"Extension: {ext.id} - {ext.name}")

# Update an extension
updated_extension = extensions_service.update(extension.id, "/path/to/updated-extension.zip")

# Delete an extension
extensions_service.delete(extension.id)
```

#### Loading Extensions in Browser Sessions

To load extensions in a browser session, configure the session with extension options:

```python
from agb.session_params import BrowserContext
from agb.extension import ExtensionOption

# Upload extensions
ext1 = extensions_service.create("/path/to/extension1.zip")
ext2 = extensions_service.create("/path/to/extension2.zip")

# Create extension option for browser integration
ext_option = extensions_service.create_extension_option([ext1.id, ext2.id])

# Create browser context with extensions
browser_context = BrowserContext(
    context_id="browser_session_with_extensions",
    auto_upload=True,
    extension_option=ext_option
)

# Create session with browser context
params = CreateSessionParams(
    image_id="agb-browser-use-1",
    browser_context=browser_context
)

session_result = agb.create(params)
session = session_result.session

# Initialize browser with extensions
browser_option = BrowserOption(
    extension_path="/tmp/extensions/"
)

success = await session.browser.initialize_async(browser_option)
```

#### Working with Loaded Extensions

Once extensions are loaded, you can interact with them using Playwright:

```python
# Connect to browser and check loaded extensions
endpoint_url = session.browser.get_endpoint_url()

async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp(endpoint_url)
    cdp_session = await browser.new_browser_cdp_session()

    # Get all targets to find loaded extensions
    targets = await cdp_session.send("Target.getTargets")

    for info in targets["targetInfos"]:
        url = info.get("url", "")
        if url.startswith("chrome-extension://"):
            ext_id = url.split("/")[2]
            print(f"Loaded extension: {ext_id} - {info.get('title')}")

    await cdp_session.detach()
```

### Session Management

```python
# Check browser status
if session.browser.is_initialized():
    print("Browser is ready")

# Get current configuration
current_option = session.browser.get_option()
if current_option:
    print(f"Using stealth: {current_option.use_stealth}")
```

### Error Handling

```python
from agb.exceptions import BrowserError

try:
    success = await session.browser.initialize_async(option)
    if not success:
        raise BrowserError("Failed to initialize browser")

    act_result = await session.browser.agent.act_async(ActOptions(
        action="Click the submit button"
    ), page)

    if not act_result.success:
        print(f"Action failed: {act_result.message}")

except BrowserError as e:
    print(f"Browser error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

### 1. Resource Management

Always clean up resources properly:

```python
try:
    # Your automation code here
    pass
finally:
    if 'browser' in locals():
        await browser.close()
    if 'session' in locals():
        agb.delete(session)
```

### 2. Timeout Configuration

Use appropriate timeouts for different operations:

```python
# Quick interactions
quick_action = ActOptions(action="Click button")

# Form submissions
form_action = ActOptions(action="Submit form")

# Page navigation
nav_action = ActOptions(action="Navigate to next page")
```

### 3. Robust Element Interaction

Make your automation more reliable:

```python
# Wait for elements to be ready
act_result = await session.browser.agent.act_async(ActOptions(
    action="Wait for the page to fully load, then click the submit button"
), page)

# Handle dynamic content
observe_result = await session.browser.agent.observe_async(ObserveOptions(
    instruction="Wait for the search results to appear and find the first result link"
), page)
```

### 4. Error Recovery

Implement retry logic for critical operations:

```python
async def retry_action(agent, page, action_options, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await agent.act_async(action_options, page)
            if result.success:
                return result
            print(f"Attempt {attempt + 1} failed: {result.message}")
        except Exception as e:
            print(f"Attempt {attempt + 1} error: {e}")

        if attempt < max_retries - 1:
            await asyncio.sleep(2)  # Wait before retry

    raise BrowserError(f"Action failed after {max_retries} attempts")
```

## Troubleshooting

### Common Issues

#### Browser Initialization Fails

```python
# Check session status
if not result.success:
    print(f"Session creation failed: {result.error_message}")
    return

# Verify browser initialization
```

#### CDP Connection Issues

```python
try:
    endpoint_url = session.browser.get_endpoint_url()
    browser = await p.chromium.connect_over_cdp(endpoint_url)
except Exception as e:
    print(f"CDP connection failed: {e}")
    # Try reinitializing browser
    await session.browser.initialize_async(BrowserOption())
```

#### Agent Actions Fail

```python
# Add more specific instructions
act_result = await session.browser.agent.act_async(ActOptions(
    action="Look for a button with text 'Submit' or 'Send' and click it"
), page)

# Check page state first
success, elements = await session.browser.agent.observe_async(ObserveOptions(
    instruction="Check if the page has finished loading and show all interactive elements"
), page)
```

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your automation code with detailed logs
```

### Performance Tips

1. **Reuse Sessions**: Create one session for multiple operations
2. **Optimize Timeouts**: Use shorter timeouts for simple operations
3. **Batch Operations**: Combine multiple actions when possible
4. **Monitor Resources**: Check session resource usage regularly
