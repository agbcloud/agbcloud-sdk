# Browser API Reference

## 🌐 Related Tutorial

- [Browser Automation Guide](../../guides/browser-automation.md) - Complete guide to browser automation

## Overview

The Browser module provides comprehensive browser automation capabilities including navigation,
element interaction, screenshot capture, and content extraction. It enables automated testing
and web scraping workflows with support for proxy configuration, fingerprinting, and stealth mode.


## Requirements

- Requires `agb-browser-use-1` image for browser automation features



## BrowserFingerprintContext

```python
class BrowserFingerprintContext()
```

Browser fingerprint context configuration.

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

Browser fingerprint options.

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

### screenshot

```python
async def screenshot(page, full_page: bool = False, **options) -> bytes
```

Takes a screenshot of the specified page with enhanced options and error handling.
This is the async version of the screenshot method.

**Arguments**:

- `page` _Page_ - The Playwright Page object to take a screenshot of. This is a required parameter.
- `full_page` _bool_ - Whether to capture the full scrollable page. Defaults to False.
    **options: Additional screenshot options that will override defaults.
  Common options include:
  - type (str): Image type, either 'png' or 'jpeg' (default: 'png')
  - quality (int): Quality of the image, between 0-100 (jpeg only)
  - timeout (int): Maximum time in milliseconds (default: 60000)
  - animations (str): How to handle animations (default: 'disabled')
  - caret (str): How to handle the caret (default: 'hide')
  - scale (str): Scale setting (default: 'css')


**Returns**:

    bytes: Screenshot data as bytes.


**Raises**:

    BrowserError: If browser is not initialized.
    RuntimeError: If screenshot capture fails.

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

## ScreenFingerprint

```python
@dataclass
class ScreenFingerprint()
```

Screen fingerprint data structure.

#### availHeight: `int`

```python
availHeight = None
```

#### availWidth: `int`

```python
availWidth = None
```

#### availTop: `int`

```python
availTop = None
```

#### availLeft: `int`

```python
availLeft = None
```

#### colorDepth: `int`

```python
colorDepth = None
```

#### height: `int`

```python
height = None
```

#### pixelDepth: `int`

```python
pixelDepth = None
```

#### width: `int`

```python
width = None
```

#### devicePixelRatio: `float`

```python
devicePixelRatio = None
```

#### pageXOffset: `int`

```python
pageXOffset = None
```

#### pageYOffset: `int`

```python
pageYOffset = None
```

#### innerHeight: `int`

```python
innerHeight = None
```

#### outerHeight: `int`

```python
outerHeight = None
```

#### outerWidth: `int`

```python
outerWidth = None
```

#### innerWidth: `int`

```python
innerWidth = None
```

#### screenX: `int`

```python
screenX = None
```

#### clientWidth: `int`

```python
clientWidth = None
```

#### clientHeight: `int`

```python
clientHeight = None
```

#### hasHDR: `bool`

```python
hasHDR = None
```

## Brand

```python
@dataclass
class Brand()
```

Brand information data structure.

#### brand: `str`

```python
brand = None
```

#### version: `str`

```python
version = None
```

## UserAgentData

```python
@dataclass
class UserAgentData()
```

User agent data structure.

#### brands: `List[Brand]`

```python
brands = None
```

#### mobile: `bool`

```python
mobile = None
```

#### platform: `str`

```python
platform = None
```

#### architecture: `str`

```python
architecture = None
```

#### bitness: `str`

```python
bitness = None
```

#### fullVersionList: `List[Brand]`

```python
fullVersionList = None
```

#### model: `str`

```python
model = None
```

#### platformVersion: `str`

```python
platformVersion = None
```

#### uaFullVersion: `str`

```python
uaFullVersion = None
```

## ExtraProperties

```python
@dataclass
class ExtraProperties()
```

Navigator extra properties data structure.

#### vendorFlavors: `List[str]`

```python
vendorFlavors = None
```

#### isBluetoothSupported: `bool`

```python
isBluetoothSupported = None
```

#### globalPrivacyControl: `Optional[Any]`

```python
globalPrivacyControl = None
```

#### pdfViewerEnabled: `bool`

```python
pdfViewerEnabled = None
```

#### installedApps: `List[Any]`

```python
installedApps = None
```

## NavigatorFingerprint

```python
@dataclass
class NavigatorFingerprint()
```

Navigator fingerprint data structure.

#### userAgent: `str`

```python
userAgent = None
```

#### userAgentData: `UserAgentData`

```python
userAgentData = None
```

#### doNotTrack: `str`

```python
doNotTrack = None
```

#### appCodeName: `str`

```python
appCodeName = None
```

#### appName: `str`

```python
appName = None
```

#### appVersion: `str`

```python
appVersion = None
```

#### oscpu: `str`

```python
oscpu = None
```

#### webdriver: `str`

```python
webdriver = None
```

#### language: `str`

```python
language = None
```

#### languages: `List[str]`

```python
languages = None
```

#### platform: `str`

```python
platform = None
```

#### deviceMemory: `Optional[int]`

```python
deviceMemory = None
```

#### hardwareConcurrency: `int`

```python
hardwareConcurrency = None
```

#### product: `str`

```python
product = None
```

#### productSub: `str`

```python
productSub = None
```

#### vendor: `str`

```python
vendor = None
```

#### vendorSub: `str`

```python
vendorSub = None
```

#### maxTouchPoints: `Optional[int]`

```python
maxTouchPoints = None
```

#### extraProperties: `ExtraProperties`

```python
extraProperties = None
```

## VideoCard

```python
@dataclass
class VideoCard()
```

Video card information data structure.

#### renderer: `str`

```python
renderer = None
```

#### vendor: `str`

```python
vendor = None
```

## Fingerprint

```python
@dataclass
class Fingerprint()
```

Main fingerprint data structure.

#### screen: `ScreenFingerprint`

```python
screen = None
```

#### navigator: `NavigatorFingerprint`

```python
navigator = None
```

#### videoCodecs: `Dict[str, str]`

```python
videoCodecs = None
```

#### audioCodecs: `Dict[str, str]`

```python
audioCodecs = None
```

#### pluginsData: `Dict[str, str]`

```python
pluginsData = None
```

#### battery: `Optional[Dict[str, str]]`

```python
battery = None
```

#### videoCard: `VideoCard`

```python
videoCard = None
```

#### multimediaDevices: `List[str]`

```python
multimediaDevices = None
```

#### fonts: `List[str]`

```python
fonts = None
```

#### mockWebRTC: `bool`

```python
mockWebRTC = None
```

#### slim: `Optional[bool]`

```python
slim = None
```

## FingerprintFormat

```python
@dataclass
class FingerprintFormat()
```

Complete fingerprint format including fingerprint data and headers.

#### fingerprint: `Fingerprint`

```python
fingerprint = None
```

#### headers: `Dict[str, str]`

```python
headers = None
```

### load

```python
@classmethod
def load(cls, data: Union[dict, str]) -> 'FingerprintFormat'
```

Load fingerprint from dictionary or JSON string.

This is the recommended public API for loading fingerprint data.

**Arguments**:

    data: Either a dictionary or JSON string containing fingerprint data


**Returns**:

    FingerprintFormat: Loaded fingerprint format object


**Raises**:

    ValueError: If data is invalid or cannot be parsed


**Example**:

```python
# From dictionary
fingerprint = FingerprintFormat.load({"fingerprint": {...}, "headers": {...}})

# From JSON string
fingerprint = FingerprintFormat.load('{"fingerprint": {...}, "headers": {...}}')
```

### create

```python
@classmethod
def create(cls,
           screen: ScreenFingerprint,
           navigator: NavigatorFingerprint,
           video_card: VideoCard,
           headers: Dict[str, str],
           video_codecs: Optional[Dict[str, str]] = None,
           audio_codecs: Optional[Dict[str, str]] = None,
           plugins_data: Optional[Dict[str, str]] = None,
           battery: Optional[Dict[str, str]] = None,
           multimedia_devices: Optional[List[str]] = None,
           fonts: Optional[List[str]] = None,
           mock_webrtc: bool = False,
           slim: Optional[bool] = None) -> 'FingerprintFormat'
```

Create FingerprintFormat directly using component classes.

**Arguments**:

    screen: ScreenFingerprint object
    navigator: NavigatorFingerprint object
    video_card: VideoCard object
    headers: Headers dictionary
    video_codecs: Video codecs dictionary (optional)
    audio_codecs: Audio codecs dictionary (optional)
    plugins_data: Plugins data dictionary (optional)
    battery: Battery information dictionary (optional)
    multimedia_devices: List of multimedia devices (optional)
    fonts: List of available fonts (optional)
    mock_webrtc: Whether WebRTC is mocked (default: False)
    slim: Slim mode flag (optional)


**Returns**:

    FingerprintFormat: Complete fingerprint format object

## BrowserFingerprintGenerator

```python
class BrowserFingerprintGenerator()
```

Browser fingerprint generator class for extracting comprehensive browser fingerprint data.
This class uses Playwright to launch a local browser and collect fingerprint information
including screen properties, navigator data, codecs, plugins, WebGL info, and HTTP headers.

### generate\_fingerprint

```python
async def generate_fingerprint() -> Optional[FingerprintFormat]
```

Extract comprehensive browser fingerprint using Playwright.

**Returns**:

    Optional[FingerprintFormat]: FingerprintFormat object containing fingerprint and headers, or None if generation failed

### generate\_fingerprint\_to\_file

```python
async def generate_fingerprint_to_file(
        output_filename: str = "fingerprint_output.json") -> bool
```

Extract comprehensive browser fingerprint and save to file.

**Arguments**:

    output_filename: Name of the file to save fingerprint data


**Returns**:

    bool: True if fingerprint generation and saving succeeded, False otherwise

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
