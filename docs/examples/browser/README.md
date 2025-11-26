# Browser Automation Examples

This directory contains practical examples demonstrating various browser automation capabilities using the AGB SDK.

## 📁 Available Examples

### Basic Automation
- **basic_navigation.py** - Simple page navigation and interaction

### AI Agent Operations
- **natural_language_actions.py** - Using natural language to control the browser
- **data_extraction.py** - Extracting structured data from web pages



## 🚀 Quick Start

### Prerequisites

1. Install required dependencies:
```bash
pip install agbcloud-sdk playwright pydantic
python -m playwright install chromium
```

2. Set your API key:
```bash
export AGB_API_KEY=your_api_key_here
```

### Running Examples

Each example is self-contained and can be run directly:

```bash
python basic_navigation.py
python natural_language_actions.py
python data_extraction.py
```

## 📖 Example Descriptions

### Available Examples

#### basic_navigation.py
Demonstrates fundamental browser operations:
- Creating and initializing a browser session
- Navigating to web pages
- Getting page information (title, URL, etc.)
- Basic Playwright integration

#### natural_language_actions.py
Demonstrates AI-powered browser control:
- Using natural language to describe actions
- Complex multi-step operations
- Handling dynamic page content
- Error recovery with AI assistance

#### data_extraction.py
Demonstrates structured data extraction:
- Defining data schemas with Pydantic
- Extracting product information
- Handling lists and nested data
- Text-based vs DOM-based extraction

## 🛠️ Common Patterns

### Session Management
```python
import os
from agb import AGB
from agb.session_params import CreateSessionParams

# Standard session setup
api_key = os.getenv("AGB_API_KEY")
agb = AGB(api_key=api_key)
params = CreateSessionParams(image_id="agb-browser-use-1")
result = agb.create(params)
session = result.session
```

### Browser Initialization
```python
from agb.modules.browser import BrowserOption, BrowserViewport

# Basic initialization
option = BrowserOption(use_stealth=True)
success = await session.browser.initialize_async(option)

# Advanced configuration
option = BrowserOption(
    use_stealth=True,
    viewport=BrowserViewport(width=1366, height=768),
    user_agent="Custom User Agent"
)
```

### Playwright Integration
```python
from playwright.async_api import async_playwright

endpoint_url = session.browser.get_endpoint_url()
async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp(endpoint_url)
    page = await browser.new_page()
    # Your automation code here
    await browser.close()
```

### AI Agent Usage
```python
from agb.modules.browser import ActOptions, ObserveOptions, ExtractOptions

# Perform actions
result = await session.browser.agent.act_async(ActOptions(
    action="Click the submit button"
), page)

# Observe elements
success, results = await session.browser.agent.observe_async(bserveOptions(
    instruction="Find all product cards"
), page)

# Extract data
success, data = await session.browser.agent.extract_async(ExtractOptions(
    instruction="Extract product information",
    schema=ProductSchema
), page)
```

## 🔧 Troubleshooting

### Common Issues

1. **Browser initialization fails**
   - Check your API key and session image
   - Verify network connectivity
   - Review the basic_navigation.py example for proper setup

2. **CDP connection issues**
   - Ensure browser is properly initialized
   - Check endpoint URL validity
   - Try reinitializing the browser

3. **AI agent actions fail**
   - Make instructions more specific
   - Increase timeout values
   - Check page loading state

4. **Resource cleanup**
   - Always close browsers and delete sessions
   - Use try-finally blocks for cleanup
   - Follow the patterns shown in existing examples

### Debug Mode

Enable detailed logging for troubleshooting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Additional Resources

- [Browser Automation Guide](../../guides/browser-automation.md) - Comprehensive guide
- [API Reference](../../api-reference/capabilities/browser.md) - Detailed API documentation
- [Best Practices](../../guides/best-practices.md) - Production deployment tips
- [Session Management](../../guides/session-management.md) - Advanced session handling

## 🤝 Contributing

Found a bug or want to add an example? Please:
1. Check existing issues and examples
2. Create a clear, focused example
3. Include proper error handling
4. Add documentation and comments
5. Test thoroughly before submitting

## 📄 License

These examples are provided under the same license as the AGB SDK. See the main LICENSE file for details.