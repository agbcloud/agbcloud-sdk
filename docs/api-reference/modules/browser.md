# Browser Module API Reference

The Browser module provides comprehensive browser automation capabilities with AI-powered natural language operations.

## Classes

### Browser

Main browser management class that handles browser lifecycle and provides access to automation capabilities.

#### Constructor

```python
Browser(session: Session)
```

**Parameters:**
- `session` (Session): The AGB session instance

#### Methods

##### initialize

```python
def initialize(option: BrowserOption) -> bool
```

Initialize the browser instance with the given options synchronously.

**Parameters:**
- `option` (BrowserOption): Browser configuration options

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
option = BrowserOption(use_stealth=True)
success = session.browser.initialize(option)
```

##### initialize_async

```python
async def initialize_async(option: BrowserOption) -> bool
```

Initialize the browser instance with the given options asynchronously.

**Parameters:**
- `option` (BrowserOption): Browser configuration options

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
option = BrowserOption(use_stealth=True)
success = await session.browser.initialize_async(option)
```

##### get_endpoint_url

```python
def get_endpoint_url() -> str
```

Returns the CDP endpoint URL for connecting external automation frameworks.

**Returns:**
- `str`: CDP WebSocket endpoint URL

**Raises:**
- `BrowserError`: If browser is not initialized

**Example:**
```python
if session.browser.is_initialized():
    endpoint_url = session.browser.get_endpoint_url()
    browser = await p.chromium.connect_over_cdp(endpoint_url)
```

##### is_initialized

```python
def is_initialized() -> bool
```

Check if the browser instance is initialized and ready for use.

**Returns:**
- `bool`: True if initialized, False otherwise

##### get_option

```python
def get_option() -> Optional[BrowserOption]
```

Get the current browser configuration options.

**Returns:**
- `Optional[BrowserOption]`: Current browser options or None if not set

#### Properties

##### agent

```python
agent: BrowserAgent
```

Access to the AI-powered browser agent for natural language operations.

---

### BrowserOption

Configuration class for browser initialization options.

#### Constructor

```python
BrowserOption(
    use_stealth: bool = False,
    user_agent: str = None,
    viewport: BrowserViewport = None,
    screen: BrowserScreen = None,
    fingerprint: BrowserFingerprint = None,
    proxies: Optional[List[BrowserProxy]] = None
)
```

**Parameters:**
- `use_stealth` (bool): Enable stealth mode to avoid detection
- `user_agent` (str): Custom user agent string
- `viewport` (BrowserViewport): Browser viewport configuration
- `screen` (BrowserScreen): Screen size configuration
- `fingerprint` (BrowserFingerprint): Fingerprint customization options
- `proxies` (List[BrowserProxy]): Proxy configuration (max 1 proxy)

**Example:**
```python
option = BrowserOption(
    use_stealth=True,
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    viewport=BrowserViewport(width=1366, height=768),
    proxies=[BrowserProxy(proxy_type="custom", server="127.0.0.1:8080")]
)
```

---

### BrowserViewport

Browser viewport size configuration.

#### Constructor

```python
BrowserViewport(width: int = 1920, height: int = 1080)
```

**Parameters:**
- `width` (int): Viewport width in pixels
- `height` (int): Viewport height in pixels

---

### BrowserScreen

Browser screen size configuration.

#### Constructor

```python
BrowserScreen(width: int = 1920, height: int = 1080)
```

**Parameters:**
- `width` (int): Screen width in pixels
- `height` (int): Screen height in pixels

---

### BrowserFingerprint

Browser fingerprint customization options.

#### Constructor

```python
BrowserFingerprint(
    devices: List[Literal["desktop", "mobile"]] = None,
    operating_systems: List[Literal["windows", "macos", "linux", "android", "ios"]] = None,
    locales: List[str] = None
)
```

**Parameters:**
- `devices` (List[str]): Device types to emulate
- `operating_systems` (List[str]): Operating systems to emulate
- `locales` (List[str]): Locale codes to use

**Example:**
```python
fingerprint = BrowserFingerprint(
    devices=["desktop"],
    operating_systems=["windows", "macos"],
    locales=["en-US", "zh-CN"]
)
```

---

### BrowserProxy

Proxy configuration for browser connections.

#### Constructor

```python
BrowserProxy(
    proxy_type: Literal["custom", "built-in"],
    server: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    strategy: Optional[Literal["restricted", "polling"]] = None,
    pollsize: int = 10
)
```

**Parameters:**
- `proxy_type` (str): Type of proxy - "custom" or "built-in"
- `server` (str): Proxy server address (required for custom type)
- `username` (str): Proxy username (optional for custom type)
- `password` (str): Proxy password (optional for custom type)
- `strategy` (str): Strategy for built-in proxy - "restricted" or "polling"
- `pollsize` (int): Pool size for polling strategy

**Examples:**

Custom proxy:
```python
custom_proxy = BrowserProxy(
    proxy_type="custom",
    server="127.0.0.1:8080",
    username="user",
    password="pass"
)
```

Built-in proxy with polling:
```python
builtin_proxy = BrowserProxy(
    proxy_type="built-in",
    strategy="polling",
    pollsize=10
)
```

---

### BrowserAgent

AI-powered browser agent for natural language automation.

#### Constructor

```python
BrowserAgent(session, browser)
```

**Parameters:**
- `session`: AGB session instance
- `browser`: Browser instance

#### Methods

##### act

```python
def act(page, action_input: Union[ObserveResult, ActOptions]) -> ActResult
```

Perform an action on the given Playwright Page object using natural language.

**Parameters:**
- `page`: Playwright Page object
- `action_input` (Union[ObserveResult, ActOptions]): Action configuration or observe result

**Returns:**
- `ActResult`: Result of the action

**Example:**
```python
result = session.browser.agent.act(page, ActOptions(
    action="Click the submit button",
    timeoutMS=10000
))
```

##### act_async

```python
async def act_async(page, action_input: Union[ObserveResult, ActOptions]) -> ActResult
```

Asynchronous version of the act method.

**Parameters:**
- `page`: Playwright Page object
- `action_input` (Union[ObserveResult, ActOptions]): Action configuration

**Returns:**
- `ActResult`: Result of the action

##### observe

```python
def observe(page, options: ObserveOptions) -> Tuple[bool, List[ObserveResult]]
```

Observe elements or state on the given Playwright Page object.

**Parameters:**
- `page`: Playwright Page object
- `options` (ObserveOptions): Observation configuration

**Returns:**
- `Tuple[bool, List[ObserveResult]]`: Success status and list of observed elements

**Example:**
```python
success, results = session.browser.agent.observe(page, ObserveOptions(
    instruction="Find all clickable buttons",
    returnActions=5
))
```

##### observe_async

```python
async def observe_async(page, options: ObserveOptions) -> Tuple[bool, List[ObserveResult]]
```

Asynchronous version of the observe method.

##### extract

```python
def extract(page, options: ExtractOptions[T]) -> Tuple[bool, T]
```

Extract structured information from the given Playwright Page object.

**Parameters:**
- `page`: Playwright Page object
- `options` (ExtractOptions[T]): Extraction configuration with schema

**Returns:**
- `Tuple[bool, T]`: Success status and extracted data

**Example:**
```python
success, data = session.browser.agent.extract(page, ExtractOptions(
    instruction="Extract product information",
    schema=ProductSchema
))
```

##### extract_async

```python
async def extract_async(page, options: ExtractOptions[T]) -> Tuple[bool, T]
```

Asynchronous version of the extract method.

---

### ActOptions

Configuration options for browser actions.

#### Constructor

```python
ActOptions(
    action: str,
    timeoutMS: Optional[int] = None,
    iframes: Optional[bool] = None,
    dom_settle_timeout_ms: Optional[int] = None
)
```

**Parameters:**
- `action` (str): Natural language description of the action to perform
- `timeoutMS` (int): Timeout in milliseconds for the action
- `iframes` (bool): Whether to include iframe content in the action
- `dom_settle_timeout_ms` (int): Time to wait for DOM to settle after action

---

### ActResult

Result of a browser action.

#### Properties

```python
success: bool      # Whether the action succeeded
message: str       # Result message or error description
action: str        # The action that was performed
```

---

### ObserveOptions

Configuration options for page observation.

#### Constructor

```python
ObserveOptions(
    instruction: str,
    returnActions: Optional[int] = None,
    iframes: Optional[bool] = None,
    dom_settle_timeout_ms: Optional[int] = None
)
```

**Parameters:**
- `instruction` (str): Natural language description of what to observe
- `returnActions` (int): Maximum number of actions to return
- `iframes` (bool): Whether to include iframe content
- `dom_settle_timeout_ms` (int): Time to wait for DOM to settle

---

### ObserveResult

Result of a page observation.

#### Properties

```python
selector: str      # CSS selector for the observed element
description: str   # Description of the observed element
method: str        # Suggested interaction method
arguments: dict    # Arguments for the interaction method
```

---

### ExtractOptions

Configuration options for data extraction.

#### Constructor

```python
ExtractOptions(
    instruction: str,
    schema: Type[T],
    use_text_extract: Optional[bool] = None,
    selector: Optional[str] = None,
    iframe: Optional[bool] = None,
    dom_settle_timeout_ms: Optional[int] = None
)
```

**Parameters:**
- `instruction` (str): Natural language description of what to extract
- `schema` (Type[T]): Pydantic model class defining the expected data structure
- `use_text_extract` (bool): Whether to use text-based extraction
- `selector` (str): CSS selector to focus extraction on specific elements
- `iframe` (bool): Whether to include iframe content (note: parameter name is `iframe`, not `iframes`)
- `dom_settle_timeout_ms` (int): Time to wait for DOM to settle

**Example:**
```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: str
    rating: float

options = ExtractOptions(
    instruction="Extract product details from the page",
    schema=Product,
    use_text_extract=True
)
```

## Exceptions

### BrowserError

Exception raised for browser-related errors.

```python
class BrowserError(AGBError):
    pass
```

**Usage:**
```python
from agb.exceptions import BrowserError

try:
    success = session.browser.initialize(option)
    if not success:
        raise BrowserError("Browser initialization failed")
except BrowserError as e:
    print(f"Browser error: {e}")
```

## Usage Examples

### Basic Browser Setup

```python
import asyncio
from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser import BrowserOption, BrowserViewport
from playwright.async_api import async_playwright

async def setup_browser():
    # Create session
    agb = AGB(api_key="your-api-key")
    params = CreateSessionParams(image_id="agb-browser-use-1")
    result = agb.create(params)
    session = result.session
    
    # Configure and initialize browser
    option = BrowserOption(
        use_stealth=True,
        viewport=BrowserViewport(width=1366, height=768)
    )
    
    success = await session.browser.initialize_async(option)
    if not success:
        raise RuntimeError("Failed to initialize browser")
    
    # Connect Playwright
    endpoint_url = session.browser.get_endpoint_url()
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(endpoint_url)
        page = await browser.new_page()
        
        # Your automation code here
        
        await browser.close()
    
    agb.delete(session)
```

### AI Agent Operations

```python
from agb.modules.browser import ActOptions, ObserveOptions, ExtractOptions
from pydantic import BaseModel

# Perform actions
act_result = await session.browser.agent.act_async(page, ActOptions(
    action="Fill the search box with 'Python automation' and press Enter",
    timeoutMS=15000
))

# Observe page elements
success, results = await session.browser.agent.observe_async(page, ObserveOptions(
    instruction="Find all search result links",
    returnActions=10
))

# Extract structured data
class SearchResult(BaseModel):
    title: str
    url: str
    description: str

success, data = await session.browser.agent.extract_async(page, ExtractOptions(
    instruction="Extract search results information",
    schema=SearchResult
))
```

## Best Practices

1. **Always check initialization status** before performing operations
2. **Use appropriate timeouts** for different types of operations
3. **Handle exceptions properly** with try-catch blocks
4. **Clean up resources** by closing browsers and deleting sessions
5. **Use stealth mode** when needed to avoid detection
6. **Configure proxies** for IP rotation when required
7. **Implement retry logic** for critical operations 