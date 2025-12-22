import asyncio
import time
import os
import base64
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional

from agb.api.base_service import BaseService
from agb.api.models import InitBrowserRequest
from agb.config import BROWSER_DATA_PATH, BROWSER_FINGERPRINT_PERSIST_PATH
from agb.exceptions import BrowserError
from agb.modules.browser.browser_agent import BrowserAgent
from agb.logger import get_logger, log_operation_start, log_operation_success, log_operation_error

logger = get_logger(__name__)

if TYPE_CHECKING:
    from agb.session import Session
    from agb.modules.browser.fingerprint import FingerprintFormat


class BrowserFingerprintContext:
    """
    Browser fingerprint context configuration.
    """
    def __init__(self, fingerprint_context_id: str):
        """
        Initialize FingerprintContext with context id.

        Args:
            fingerprint_context_id (str): ID of the fingerprint context for browser fingerprint.

        Raises:
            ValueError: If fingerprint_context_id is empty.
        """
        if not fingerprint_context_id or not fingerprint_context_id.strip():
            raise ValueError("fingerprint_context_id cannot be empty")

        self.fingerprint_context_id = fingerprint_context_id


class BrowserProxy:
    """
    Browser proxy configuration.
    Supports two types of proxy: custom proxy, built-in proxy.
    built-in proxy support two strategies: restricted and polling.
    """

    def __init__(
        self,
        proxy_type: Literal["custom", "built-in"],
        server: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        strategy: Optional[Literal["restricted", "polling"]] = None,
        pollsize: int = 10,
    ):
        """
        Initialize a BrowserProxy.

        Args:
            proxy_type: Type of proxy - "custom" or "built-in"
            server: Proxy server address (required for custom type)
            username: Proxy username (optional for custom type)
            password: Proxy password (optional for custom type)
            strategy: Strategy for built-in support "restricted" and "polling"
            pollsize: Pool size (optional for proxy_type built-in and strategy polling)

            example:
            # custom proxy
            proxy_type: custom
            server: "127.0.0.1:9090"
            username: "username"
            password: "password"

            # built-in proxy with polling strategy
            proxy_type: built-in
            strategy: "polling"
            pollsize: 10

            # built-in proxy with restricted strategy
            proxy_type: built-in
            strategy: "restricted"
        """
        self.type = proxy_type
        self.server = server
        self.username = username
        self.password = password
        self.strategy = strategy
        self.pollsize = pollsize

        # Validation
        if proxy_type not in ["custom", "built-in"]:
            raise ValueError("proxy_type must be custom or built-in")

        if proxy_type == "custom" and not server:
            raise ValueError("server is required for custom proxy type")

        if proxy_type == "built-in" and not strategy:
            raise ValueError("strategy is required for built-in proxy type")

        if proxy_type == "built-in" and strategy not in ["restricted", "polling"]:
            raise ValueError(
                "strategy must be restricted or polling for built-in proxy type"
            )

        if proxy_type == "built-in" and strategy == "polling" and pollsize <= 0:
            raise ValueError("pollsize must be greater than 0 for polling strategy")

    def to_map(self):
        proxy_map = {"type": self.type}

        if self.type == "custom":
            proxy_map["server"] = self.server
            if self.username:
                proxy_map["username"] = self.username
            if self.password:
                proxy_map["password"] = self.password
        elif self.type == "built-in":
            proxy_map["strategy"] = self.strategy
            if self.strategy == "polling":
                proxy_map["pollsize"] = self.pollsize

        return proxy_map

    @classmethod
    def from_map(cls, m: Optional[Dict[Any, Any]] = None):
        if not m:
            return None

        proxy_type = m.get("type")
        if not proxy_type:
            raise ValueError("type is required in proxy configuration")

        if proxy_type == "custom":
            return cls(
                proxy_type=proxy_type,
                server=m.get("server"),
                username=m.get("username"),
                password=m.get("password"),
            )
        elif proxy_type == "built-in":
            return cls(
                proxy_type=proxy_type,
                strategy=m.get("strategy"),
                pollsize=m.get("pollsize", 10),
            )
        else:
            raise ValueError(f"Unsupported proxy type: {proxy_type}")


class BrowserViewport:
    """
    Browser viewport options.
    """

    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height

    def to_map(self):
        viewport_map = dict()
        if self.width is not None:
            viewport_map["width"] = self.width
        if self.height is not None:
            viewport_map["height"] = self.height
        return viewport_map

    @classmethod
    def from_map(cls, m: Optional[Dict[Any, Any]] = None):
        instance = cls()
        m = m or dict()
        if m.get("width") is not None:
            width_val = m.get("width")
            if isinstance(width_val, int):
                instance.width = width_val
        if m.get("height") is not None:
            height_val = m.get("height")
            if isinstance(height_val, int):
                instance.height = height_val
        return instance


class BrowserScreen:
    """
    Browser screen options.
    """

    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height

    def to_map(self):
        screen_map = dict()
        if self.width is not None:
            screen_map["width"] = self.width
        if self.height is not None:
            screen_map["height"] = self.height
        return screen_map

    @classmethod
    def from_map(cls, m: Optional[Dict[Any, Any]] = None):
        instance = cls()
        m = m or dict()
        if m.get("width") is not None:
            width_val = m.get("width")
            if isinstance(width_val, int):
                instance.width = width_val
        if m.get("height") is not None:
            height_val = m.get("height")
            if isinstance(height_val, int):
                instance.height = height_val
        return instance


class BrowserFingerprint:
    """
    Browser fingerprint options.
    """

    def __init__(
        self,
        devices: Optional[List[Literal["desktop", "mobile"]]] = None,
        operating_systems: Optional[
            List[Literal["windows", "macos", "linux", "android", "ios"]]
        ] = None,
        locales: Optional[List[str]] = None,
    ):
        self.devices = devices
        self.operating_systems = operating_systems
        self.locales = locales

        # Validation

        if devices is not None:
            if not isinstance(devices, list):
                raise ValueError("devices must be a list")
            for device in devices:
                if device not in ["desktop", "mobile"]:
                    raise ValueError("device must be desktop or mobile")

        if operating_systems is not None:
            if not isinstance(operating_systems, list):
                raise ValueError("operating_systems must be a list")
            for operating_system in operating_systems:
                if operating_system not in [
                    "windows",
                    "macos",
                    "linux",
                    "android",
                    "ios",
                ]:
                    raise ValueError(
                        "operating_system must be windows, macos, linux, android or ios"
                    )

    def to_map(self):
        fingerprint_map = dict()
        if self.devices is not None:
            fingerprint_map["devices"] = self.devices
        if self.operating_systems is not None:
            fingerprint_map["operatingSystems"] = self.operating_systems
        if self.locales is not None:
            fingerprint_map["locales"] = self.locales
        return fingerprint_map

    @classmethod
    def from_map(cls, m: Optional[Dict[Any, Any]] = None):
        instance = cls()
        m = m or dict()
        if m.get("devices") is not None:
            devices_val = m.get("devices")
            if isinstance(devices_val, list):
                instance.devices = devices_val
        if m.get("operatingSystems") is not None:
            os_val = m.get("operatingSystems")
            if isinstance(os_val, list):
                instance.operating_systems = os_val
        if m.get("locales") is not None:
            locales_val = m.get("locales")
            if isinstance(locales_val, list):
                instance.locales = locales_val
        return instance


class BrowserOption:
    """
    browser initialization options.
    """

    def __init__(
        self,
        use_stealth: bool = False,
        user_agent: Optional[str] = None,
        viewport: Optional[BrowserViewport] = None,
        screen: Optional[BrowserScreen] = None,
        fingerprint: Optional[BrowserFingerprint] = None,
        fingerprint_format: Optional["FingerprintFormat"] = None,
        fingerprint_persistent: bool = False,
        solve_captchas: bool = False,
        proxies: Optional[List[BrowserProxy]] = None,
        extension_path: Optional[str] = "/tmp/extensions/",
        cmd_args: Optional[list[str]] = None,
        default_navigate_url: Optional[str] = None,
        browser_type: Optional[Literal["chrome", "chromium"]] = None,
    ):
        self.use_stealth = use_stealth
        self.user_agent = user_agent
        self.viewport = viewport
        self.screen = screen
        self.fingerprint = fingerprint
        self.fingerprint_format = fingerprint_format
        self.solve_captchas = solve_captchas
        self.proxies = proxies
        self.extension_path = extension_path
        self.cmd_args = cmd_args
        self.default_navigate_url = default_navigate_url
        self.browser_type = browser_type

        # Check fingerprint persistent if provided
        if fingerprint_persistent:
            # Currently only support persistent fingerprint in docker env
            self.fingerprint_persist_path = os.path.join(BROWSER_FINGERPRINT_PERSIST_PATH, "fingerprint.json")
        else:
            self.fingerprint_persist_path = None

        # Validate proxies list items
        if proxies is not None:
            if not isinstance(proxies, list):
                raise ValueError("proxies must be a list")
            if len(proxies) > 1:
                raise ValueError("proxies list length must be limited to 1")
        # Validate extension_path if provided
        if extension_path is not None:
            if not isinstance(extension_path, str):
                raise ValueError("extension_path must be a string")
            if not extension_path.strip():
                raise ValueError("extension_path cannot be empty")

        # Validate cmd_args if provided
        if cmd_args is not None:
            if not isinstance(cmd_args, list):
                raise ValueError("cmd_args must be a list")

        # Validate browser_type
        if browser_type is not None and browser_type not in ["chrome", "chromium"]:
            raise ValueError("browser_type must be 'chrome' or 'chromium'")

    def to_map(self):
        option_map = dict()
        if self.use_stealth is not None:
            option_map["useStealth"] = self.use_stealth
        if self.user_agent is not None:
            option_map["userAgent"] = self.user_agent
        if self.viewport is not None:
            option_map["viewport"] = self.viewport.to_map()
        if self.screen is not None:
            option_map["screen"] = self.screen.to_map()
        if self.fingerprint is not None:
            option_map["fingerprint"] = self.fingerprint.to_map()
        if self.fingerprint_format is not None:
            # Encode fingerprint format to base64 string
            json_str = self.fingerprint_format._to_json()
            option_map['fingerprintRawData'] = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        if self.fingerprint_persist_path is not None:
            option_map['fingerprintPersistPath'] = self.fingerprint_persist_path
        if self.solve_captchas is not None:
            option_map['solveCaptchas'] = self.solve_captchas
        if self.proxies is not None:
            option_map["proxies"] = [proxy.to_map() for proxy in self.proxies]
        if self.extension_path is not None:
            option_map['extensionPath'] = self.extension_path
        if self.cmd_args is not None:
            option_map['cmdArgs'] = self.cmd_args
        if self.default_navigate_url is not None:
            option_map['defaultNavigateUrl'] = self.default_navigate_url
        if self.browser_type is not None:
            option_map['browserType'] = self.browser_type
        return option_map

    @classmethod
    def from_map(cls, m: Optional[Dict[Any, Any]] = None):
        instance = cls()
        m = m or dict()
        if m.get("useStealth") is not None:
            stealth_val = m.get("useStealth")
            if isinstance(stealth_val, bool):
                instance.use_stealth = stealth_val
        else:
            instance.use_stealth = False
        if m.get("userAgent") is not None:
            ua_val = m.get("userAgent")
            if isinstance(ua_val, str):
                instance.user_agent = ua_val
        if m.get("viewport") is not None:
            viewport_data = m.get("viewport")
            if isinstance(viewport_data, dict):
                instance.viewport = BrowserViewport.from_map(viewport_data)
        if m.get("screen") is not None:
            screen_data = m.get("screen")
            if isinstance(screen_data, dict):
                instance.screen = BrowserScreen.from_map(screen_data)
        if m.get("fingerprint") is not None:
            fingerprint_data = m.get("fingerprint")
            if isinstance(fingerprint_data, dict):
                instance.fingerprint = BrowserFingerprint.from_map(fingerprint_data)
        if m.get('fingerprintRawData') is not None:
            import base64
            from agb.modules.browser.fingerprint import FingerprintFormat
            fingerprint_raw = m.get('fingerprintRawData')
            if isinstance(fingerprint_raw, str):
                # Decode base64 encoded fingerprint data
                fingerprint_json = base64.b64decode(fingerprint_raw.encode('utf-8')).decode('utf-8')
                instance.fingerprint_format = FingerprintFormat._from_json(fingerprint_json)
            else:
                instance.fingerprint_format = fingerprint_raw
        if m.get('fingerprintPersistPath') is not None:
            fingerprint_persist_path = m.get('fingerprintPersistPath')
            if isinstance(fingerprint_persist_path, str):
                instance.fingerprint_persist_path = fingerprint_persist_path
        if m.get('solveCaptchas') is not None:
            instance.solve_captchas = m.get('solveCaptchas')
        else:
            instance.solve_captchas = False
        if m.get("proxies") is not None:
            proxy_list = m.get("proxies")
            if isinstance(proxy_list, list) and len(proxy_list) > 0:
                if len(proxy_list) > 1:
                    raise ValueError("proxies list length must be limited to 1")
                instance.proxies = [
                    BrowserProxy.from_map(proxy_data)
                    for proxy_data in proxy_list
                    if isinstance(proxy_data, dict)
                ]
        if m.get('cmdArgs') is not None:
            cmd_args = m.get('cmdArgs')
            if isinstance(cmd_args, list):
                instance.cmd_args = cmd_args
        if m.get('defaultNavigateUrl') is not None:
            default_navigate_url = m.get('defaultNavigateUrl')
            if isinstance(default_navigate_url, str):
                instance.default_navigate_url = default_navigate_url
        if m.get('browserType') is not None:
            browser_type = m.get('browserType')
            if isinstance(browser_type, str):
                instance.browser_type = browser_type
        return instance


class Browser(BaseService):
    """
    Browser provides browser-related operations for the session.
    """

    def __init__(self, session):
        self.session = session
        self._endpoint_url: Optional[str] = None
        self._initialized = False
        self._option: Optional[BrowserOption] = None
        self.agent = BrowserAgent(self.session, self)
        self.endpoint_router_port: Optional[int] = None

    def initialize(self, option: "BrowserOption") -> bool:
        """
        Initialize the browser instance with the given options.
        Returns True if successful, False otherwise.
        """
        if self.is_initialized():
            logger.info(
                f"Browser.initialize: Browser already initialized, skipping. "
                f"SessionId={self.session.get_session_id()}, "
                f"Port={self.endpoint_router_port}"
            )
            return True
        log_operation_start("Browser.initialize", f"SessionId={self.session.get_session_id()}")
        try:
            request = InitBrowserRequest(
                authorization=f"Bearer {self.session.get_api_key()}",
                session_id=self.session.get_session_id(),
                persistent_path=BROWSER_DATA_PATH,
                browser_option=option.to_map(),
            )

            # Use the new HTTP client implementation
            response = self.session.get_client().init_browser(request)

            # Check if response is successful
            if response.is_successful():
                # Get port from response
                port = response.get_port()
                if port is not None:
                    self._initialized = True
                    self.endpoint_router_port = port
                    self._option = option
                    result_msg = f"Port={port}, RequestId={response.request_id}"
                    log_operation_success("Browser.initialize", result_msg)
                    return True
                else:
                    error_msg = "Browser initialization failed: No port in response"
                    log_operation_error("Browser.initialize", error_msg)
                    return False
            else:
                error_msg = f"Browser initialization failed: {response.get_error_message()}"
                log_operation_error("Browser.initialize", error_msg)
                return False

        except Exception as e:
            log_operation_error("Browser.initialize", str(e), exc_info=True)
            self._initialized = False
            self._endpoint_url = None
            self._option = None
            return False

    async def initialize_async(self, option: "BrowserOption") -> bool:
        """
        Initialize the browser instance with the given options asynchronously.
        Returns True if successful, False otherwise.
        """
        if self.is_initialized():
            logger.info(
                f"Browser.initialize_async: Browser already initialized, skipping. "
                f"SessionId={self.session.get_session_id()}, "
                f"Port={self.endpoint_router_port}"
            )
            return True
        log_operation_start("Browser.initialize_async", f"SessionId={self.session.get_session_id()}")
        try:
            request = InitBrowserRequest(
                authorization=f"Bearer {self.session.get_api_key()}",
                session_id=self.session.get_session_id(),
                persistent_path=BROWSER_DATA_PATH,
                browser_option=option.to_map(),
            )
            response = await self.session.get_client().init_browser_async(request)

            # Check if response is successful
            if response.is_successful():
                # Get port from response
                port = response.get_port()
                if port is not None:
                    self.endpoint_router_port = port
                    self._initialized = True
                    self._option = option
                    result_msg = f"Port={port}, RequestId={response.request_id}"
                    log_operation_success("Browser.initialize_async", result_msg)
                    return True
                else:
                    error_msg = "Browser initialization failed: No port in response"
                    log_operation_error("Browser.initialize_async", error_msg)
                    return False
            else:
                error_msg = f"Browser initialization failed: {response.get_error_message()}"
                log_operation_error("Browser.initialize_async", error_msg)
                return False

        except Exception as e:
            log_operation_error("Browser.initialize_async", str(e), exc_info=True)
            self._initialized = False
            self._endpoint_url = None
            self._option = None
            return False

    def destroy(self):
        """
        Destroy the browser instance.
        """
        self._stop_browser()


    async def screenshot(self, page, full_page: bool = False, **options) -> bytes:
        """
        Takes a screenshot of the specified page with enhanced options and error handling.
        This is the async version of the screenshot method.

        Args:
            page (Page): The Playwright Page object to take a screenshot of. This is a required parameter.
            full_page (bool): Whether to capture the full scrollable page. Defaults to False.
            **options: Additional screenshot options that will override defaults.
                      Common options include:
                      - type (str): Image type, either 'png' or 'jpeg' (default: 'png')
                      - quality (int): Quality of the image, between 0-100 (jpeg only)
                      - timeout (int): Maximum time in milliseconds (default: 60000)
                      - animations (str): How to handle animations (default: 'disabled')
                      - caret (str): How to handle the caret (default: 'hide')
                      - scale (str): Scale setting (default: 'css')

        Returns:
            bytes: Screenshot data as bytes.

        Raises:
            BrowserError: If browser is not initialized.
            RuntimeError: If screenshot capture fails.
        """
        # Check if browser is initialized
        if not self.is_initialized():
            raise BrowserError("Browser must be initialized before calling screenshot.")
        if page is None:
            raise ValueError("Page cannot be None")
        # Set default enhanced options
        enhanced_options = {
            "animations": "disabled",
            "caret": "hide",
            "scale": "css",
            "timeout": options.get("timeout", 60000),
            "full_page": full_page,  # Use the function parameter, not options
            "type": options.get("type", "png"),
        }

        # Update with user-provided options (but full_page is already set from function parameter)
        enhanced_options.update(options)

        try:
            # Wait for page to load
            # await page.wait_for_load_state("networkidle")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_load_state("domcontentloaded", timeout=30000)
            # Scroll to load all content (especially for lazy-loaded elements)
            await self._scroll_to_load_all_content_async(page)

            # Ensure images with data-src attributes are loaded
            await page.evaluate("""
                () => {
                    document.querySelectorAll('img[data-src]').forEach(img => {
                        if (!img.src && img.dataset.src) {
                            img.src = img.dataset.src;
                        }
                    });
                    // Also handle background-image[data-bg]
                    document.querySelectorAll('[data-bg]').forEach(el => {
                        if (!el.style.backgroundImage) {
                            el.style.backgroundImage = `url(${el.dataset.bg})`;
                        }
                    });
                }
            """)

            # Wait a bit for images to load
            await page.wait_for_timeout(1500)
            final_height = await page.evaluate("document.body.scrollHeight")
            await page.set_viewport_size({"width": 1920, "height": min(final_height, 10000)})

            # Take the screenshot
            screenshot_bytes = await page.screenshot(**enhanced_options)
            logger.info("Screenshot captured successfully.")
            return screenshot_bytes

        except Exception as e:
            # Convert exception to string safely to avoid comparison issues
            try:
                error_str = str(e)
            except:
                error_str = "Unknown error occurred"
            error_msg = f"Failed to capture screenshot: {error_str}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    async def _scroll_to_load_all_content_async(self, page, max_scrolls: int = 8, delay_ms: int = 1200):
        """Async version of _scroll_to_load_all_content."""
        last_height = 0
        for _ in range(max_scrolls):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(delay_ms)
            new_height = await page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
            if new_height == last_height:
                break
            last_height = new_height
    def _stop_browser(self):
        """
        Stop the browser instance, internal use only.
        """
        if self.is_initialized():
            self._call_mcp_tool("stopChrome", {})
        else:
            raise BrowserError("Browser is not initialized. Cannot stop browser.")

    def get_endpoint_url(self) -> str:
        """
        Returns the endpoint URL if the browser is initialized, otherwise raises an exception.
        When initialized, always fetches the latest CDP url from session.get_link().
        """
        if not self.is_initialized():
            raise BrowserError(
                "Browser is not initialized. Cannot access endpoint URL."
            )
        try:
            # Get CDP URL from session
            cdp_url_result = self.session.get_link()
            if cdp_url_result.success and cdp_url_result.data:
                self._endpoint_url = cdp_url_result.data
                return self._endpoint_url
            else:
                raise BrowserError(
                    f"Failed to get CDP URL: {cdp_url_result.error_message}"
                )
        except Exception as e:
            raise BrowserError(f"Failed to get endpoint URL from session: {e}")

    def get_option(self) -> Optional["BrowserOption"]:
        """
        Returns the current BrowserOption used to initialize the browser, or None if not set.
        """
        return self._option

    def is_initialized(self) -> bool:
        """
        Returns True if the browser was initialized, False otherwise.
        """
        return self._initialized
