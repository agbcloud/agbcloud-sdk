# Browser API Reference

## 🌐 Related Tutorial

- [Browser Automation Guide](../../guides/browser-automation.md) - Complete guide to browser automation

## Overview

The Browser module provides comprehensive browser automation capabilities including navigation,
element interaction, screenshot capture, and content extraction. It enables automated testing
and web scraping workflows with support for proxy configuration, fingerprinting, and stealth mode.


## Requirements

- Requires `agb-browser-use-1` image for browser automation features



## BrowserProxy

```python
class BrowserProxy()
```

Browser proxy configuration.
Supports two types of proxy: custom proxy, built-in proxy.
built-in proxy support two strategies: restricted and polling.

## BrowserViewport

```python
class BrowserViewport()
```

Browser viewport options.

## BrowserScreen

```python
class BrowserScreen()
```

Browser screen options.

## BrowserFingerprint

```python
class BrowserFingerprint()
```

Browser random fingerprint options.

## FingerprintFormat

```python
class FingerprintFormat()
```

Complete fingerprint format including fingerprint data and headers.

## BrowserOption

```python
class BrowserOption()
```

browser initialization options.

## Browser

```python
class Browser(BaseService)
```

Browser provides browser-related operations for the session.

### initialize

```python
def initialize(option: "BrowserOption") -> bool
```

Initialize the browser instance with the given options.
Returns True if successful, False otherwise.

### initialize\_async

```python
async def initialize_async(option: "BrowserOption") -> bool
```

Initialize the browser instance with the given options asynchronously.
Returns True if successful, False otherwise.

### destroy

```python
def destroy()
```

Destroy the browser instance.
This method stops the browser process and releases associated resources.


## BrowserFingerprintGenerator

```python
class BrowserFingerprintGenerator()
```

Browser fingerprint generator class for extracting comprehensive browser fingerprint data.
This class uses Playwright to launch a local browser and collect fingerprint information
including screen properties, navigator data, codecs, plugins, WebGL info, and HTTP headers.

### \_\_init\_\_

```python
def __init__(headless: bool = False, use_chrome_channel: bool = True)
```

Initialize the fingerprint generator.

**Arguments**:

- `headless` _bool_ - Whether to run browser in headless mode. Default is False.
- `use_chrome_channel` _bool_ - Whether to use Chrome channel. Default is True.

### generate\_fingerprint

```python
async def generate_fingerprint() -> Optional[FingerprintFormat]
```

Extract comprehensive browser fingerprint using Playwright.

**Returns**:

    Optional[FingerprintFormat]: FingerprintFormat object containing fingerprint and headers,
    or None if generation failed.

### generate\_fingerprint\_to\_file

```python
async def generate_fingerprint_to_file(output_filename: str = "fingerprint_output.json") -> bool
```

Extract comprehensive browser fingerprint and save to file.

**Arguments**:

- `output_filename` _str_ - Name of the file to save fingerprint data. Default is "fingerprint_output.json".


**Returns**:

    bool: True if fingerprint generation and saving succeeded, False otherwise.


## ActOptions

```python
class ActOptions()
```

Options for configuring the behavior of the act method.

## ActResult

```python
class ActResult()
```

Result of the act method.

## ObserveOptions

```python
class ObserveOptions()
```

Options for configuring the behavior of the observe method.

## ObserveResult

```python
class ObserveResult()
```

Result of the observe method.

## ExtractOptions

```python
class ExtractOptions(Generic[T])
```

Options for configuring the behavior of the extract method.

## BrowserAgent

```python
class BrowserAgent(BaseService)
```

BrowserAgent handles browser automation and agent logic.

### navigate\_async

```python
async def navigate_async(url: str) -> str
```

Navigates a specific page to the given URL.

**Arguments**:

- `url` _str_ - The URL to navigate to.


**Returns**:

    str: A string indicating the result of the navigation.

### screenshot

```python
def screenshot(page=None,
               full_page: bool = True,
               quality: int = 80,
               clip: Optional[Dict[str, float]] = None,
               timeout: Optional[int] = None) -> str
```

Takes a screenshot of the specified page.

**Arguments**:

- `page` _Optional[Page]_ - The Playwright Page object to take a screenshot of. If None,
  the agent's currently focused page will be used.
- `full_page` _bool_ - Whether to capture the full scrollable page.
- `quality` _int_ - The quality of the image (0-100), for JPEG format.
- `clip` _Optional[Dict[str, float]]_ - An object specifying the clipping region {x, y, width, height}.
- `timeout` _Optional[int]_ - Custom timeout for the operation in milliseconds.


**Returns**:

    str: A base64 encoded data URL of the screenshot, or an error message.

### screenshot\_async

```python
async def screenshot_async(page=None,
                           full_page: bool = True,
                           quality: int = 80,
                           clip: Optional[Dict[str, float]] = None,
                           timeout: Optional[int] = None) -> str
```

Asynchronously takes a screenshot of the specified page.

**Arguments**:

- `page` _Optional[Page]_ - The Playwright Page object to take a screenshot of. If None,
  the agent's currently focused page will be used.
- `full_page` _bool_ - Whether to capture the full scrollable page.
- `quality` _int_ - The quality of the image (0-100), for JPEG format.
- `clip` _Optional[Dict[str, float]]_ - An object specifying the clipping region {x, y, width, height}.
- `timeout` _Optional[int]_ - Custom timeout for the operation in milliseconds.


**Returns**:

    str: A base64 encoded data URL of the screenshot, or an error message.

### close\_async

```python
async def close_async() -> bool
```

Asynchronously closes the remote browser agent session.
This will terminate the browser process managed by the agent.

**Returns**:

    bool: True if the session was closed successfully, False otherwise.

### act

```python
def act(action_input: Union[ObserveResult, ActOptions],
        page=None) -> "ActResult"
```

Perform an action on a web page, using ActOptions to configure behavior.

**Arguments**:

- `action_input` _Union[ObserveResult, ActOptions]_ - The action to perform, either as a
  pre-defined ObserveResult or custom ActOptions.
- `page` _Optional[Page]_ - The Playwright Page object to act on. If None, the agent's
  currently focused page will be used automatically.


**Returns**:

    ActResult: The result of the action.

### act\_async

```python
async def act_async(action_input: Union[ObserveResult, ActOptions],
                    page=None) -> "ActResult"
```

Asynchronously perform an action on a web page.

**Arguments**:

- `action_input` _Union[ObserveResult, ActOptions]_ - The action to perform.
- `page` _Optional[Page]_ - The Playwright Page object to act on. If None, the agent's
  currently focused page will be used automatically.


**Returns**:

    ActResult: The result of the action.

### observe

```python
def observe(options: ObserveOptions,
            page=None) -> Tuple[bool, List[ObserveResult]]
```

Observe elements or state on a web page.

**Arguments**:

- `options` _ObserveOptions_ - Options to configure the observation behavior.
- `page` _Optional[Page]_ - The Playwright Page object to observe. If None, the agent's
  currently focused page will be used.


**Returns**:

  Tuple[bool, List[ObserveResult]]: A tuple containing a success boolean and a list
  of observation results.

### observe\_async

```python
async def observe_async(options: ObserveOptions,
                        page=None) -> Tuple[bool, List[ObserveResult]]
```

Asynchronously observe elements or state on a web page.

**Arguments**:

- `options` _ObserveOptions_ - Options to configure the observation behavior.
- `page` _Optional[Page]_ - The Playwright Page object to observe. If None, the agent's
  currently focused page will be used.


**Returns**:

  Tuple[bool, List[ObserveResult]]: A tuple containing a success boolean and a list
  of observation results.

### extract

```python
def extract(options: ExtractOptions, page=None) -> Tuple[bool, T]
```

Extract information from a web page.

**Arguments**:

- `options` _ExtractOptions_ - Options to configure the extraction, including schema.
- `page` _Optional[Page]_ - The Playwright Page object to extract from. If None, the agent's
  currently focused page will be used.


**Returns**:

  Tuple[bool, T]: A tuple containing a success boolean and the extracted data as a
  Pydantic model instance, or None on failure.

### extract\_async

```python
async def extract_async(options: ExtractOptions, page=None) -> Tuple[bool, T]
```

Asynchronously extract information from a web page.

**Arguments**:

- `options` _ExtractOptions_ - Options to configure the extraction, including schema.
- `page` _Optional[Page]_ - The Playwright Page object to extract from. If None, the agent's
  currently focused page will be used.


**Returns**:

  Tuple[bool, T]: A tuple containing a success boolean and the extracted data as a
  Pydantic model instance, or None on failure.

## Best Practices

1. Initialize browser with appropriate options before use
2. Wait for page load completion before interacting with elements
3. Use appropriate selectors (CSS, XPath) for reliable element identification
4. Handle navigation timeouts and errors gracefully
5. Take screenshots for debugging and verification
6. Clean up browser resources after automation tasks
7. Configure proxy settings properly for network requirements

## Related Resources

- [Session API Reference](../session.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
