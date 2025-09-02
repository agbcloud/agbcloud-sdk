# Browser Automation Guide

Welcome to the AGB Browser Automation Guide! This comprehensive guide covers everything you need to know about using AGB's powerful browser automation capabilities.

## 🎯 Quick Navigation

- [Getting Started](#getting-started) - Basic setup and first browser session
- [Browser Configuration](#browser-configuration) - Customizing browser behavior
- [AI Agent Operations](#ai-agent-operations) - Using natural language automation
- [Advanced Features](#advanced-features) - Proxy, stealth mode, and fingerprinting
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

- Python 3.8 or higher
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
    viewport=BrowserViewport(width=1366, height=768),
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

### Fingerprint Customization

Customize browser fingerprints to avoid detection:

```python
fingerprint = BrowserFingerprint(
    devices=["desktop"],
    operating_systems=["windows", "macos"],
    locales=["en-US", "zh-CN"]
)

option = BrowserOption(
    fingerprint=fingerprint,
    use_stealth=True
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

## AI Agent Operations

AGB's AI Agent allows you to control browsers using natural language, making complex automation tasks much simpler.

### The Three Core Operations

#### 1. Act - Perform Actions

Execute actions on web pages using natural language:

```python
from agb.modules.browser import ActOptions

# Simple click action
act_result = await session.browser.agent.act_async(page, ActOptions(
    action="Click the login button",
    timeoutMS=10000
))

# Form filling
act_result = await session.browser.agent.act_async(page, ActOptions(
    action="Fill the email field with 'user@example.com' and password field with 'password123'",
    timeoutMS=15000
))

# Complex interactions
act_result = await session.browser.agent.act_async(page, ActOptions(
    action="Scroll down to find the 'Load More' button and click it",
    timeoutMS=20000,
    iframes=True  # Include iframe content
))

print(f"Action result: {act_result.success} - {act_result.message}")
```

#### 2. Observe - Analyze Page Content

Observe and analyze page elements:

```python
from agb.modules.browser import ObserveOptions

# Find interactive elements
success, results = await session.browser.agent.observe_async(page, ObserveOptions(
    instruction="Find all clickable buttons and links on the page",
    returnActions=10,
    iframes=False
))

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
success, data = await session.browser.agent.extract_async(page, ExtractOptions(
    instruction="Extract all product information from this e-commerce page",
    schema=ProductList,
    use_text_extract=True
))

if success and data:
    for product in data.products:
        print(f"Product: {product.name} - ${product.price}")
```

### Advanced Agent Configuration

```python
# With iframe support and custom timeouts
act_result = await session.browser.agent.act_async(page, ActOptions(
    action="Navigate through the multi-step checkout process",
    timeoutMS=30000,
    iframes=True,
    dom_settle_timeout_ms=2000  # Wait for DOM to settle
))

# Selective extraction with CSS selector
success, data = await session.browser.agent.extract_async(page, ExtractOptions(
    instruction="Extract pricing information from the product cards",
    schema=ProductList,
    selector=".product-card",  # Focus on specific elements
    iframe=False,
    dom_settle_timeout_ms=1000
))
```

## Advanced Features

### Stealth Mode

Enable stealth mode to avoid bot detection:

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
        
    act_result = await session.browser.agent.act_async(page, ActOptions(
        action="Click the submit button"
    ))
    
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
quick_action = ActOptions(action="Click button", timeoutMS=5000)

# Form submissions
form_action = ActOptions(action="Submit form", timeoutMS=15000)

# Page navigation
nav_action = ActOptions(action="Navigate to next page", timeoutMS=30000)
```

### 3. Robust Element Interaction

Make your automation more reliable:

```python
# Wait for elements to be ready
act_result = await session.browser.agent.act_async(page, ActOptions(
    action="Wait for the page to fully load, then click the submit button",
    timeoutMS=20000,
    dom_settle_timeout_ms=3000
))

# Handle dynamic content
observe_result = await session.browser.agent.observe_async(page, ObserveOptions(
    instruction="Wait for the search results to appear and find the first result link",
    returnActions=1
))
```

### 4. Error Recovery

Implement retry logic for critical operations:

```python
async def retry_action(agent, page, action_options, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await agent.act_async(page, action_options)
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
success = await session.browser.initialize_async(BrowserOption())
if not success:
    print("Browser initialization failed - check your session image")
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
act_result = await session.browser.agent.act_async(page, ActOptions(
    action="Look for a button with text 'Submit' or 'Send' and click it",
    timeoutMS=15000
))

# Check page state first
success, elements = await session.browser.agent.observe_async(page, ObserveOptions(
    instruction="Check if the page has finished loading and show all interactive elements"
))
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

## Next Steps

- Explore the [API Reference](../api-reference/modules/browser.md) for detailed method documentation
- Check out [Browser Examples](../examples/browser/README.md) for practical use cases
- Learn about [Session Management](session-management.md) for advanced session handling
- Review [Best Practices](best-practices.md) for production deployments 