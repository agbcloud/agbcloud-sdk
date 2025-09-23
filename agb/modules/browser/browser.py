import asyncio
import time
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional

from agb.api.base_service import BaseService
from agb.api.models import InitBrowserRequest
from agb.config import BROWSER_DATA_PATH
from agb.exceptions import BrowserError
from agb.modules.browser.browser_agent import BrowserAgent

if TYPE_CHECKING:
    from agb.session import Session


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
        proxies: Optional[List[BrowserProxy]] = None,
    ):
        self.use_stealth = use_stealth
        self.user_agent = user_agent
        self.viewport = viewport
        self.screen = screen
        self.fingerprint = fingerprint
        self.proxies = proxies

        # Validate proxies list items
        if proxies is not None:
            if not isinstance(proxies, list):
                raise ValueError("proxies must be a list")
            if len(proxies) > 1:
                raise ValueError("proxies list length must be limited to 1")

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
        if self.proxies is not None:
            option_map["proxies"] = [proxy.to_map() for proxy in self.proxies]
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
        return instance


class Browser(BaseService):
    """
    Browser provides browser-related operations for the session.
    """

    def __init__(self, session: "Session"):
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
            return True
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
                    print("Browser instance was successfully initialized.")
                    return True
                else:
                    print("Browser initialization failed: No port in response")
                    return False
            else:
                print(f"Browser initialization failed: {response.get_error_message()}")
                return False

        except Exception as e:
            print("Failed to initialize browser instance:", e)
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
            return True
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
                    print("Browser instance successfully initialized")
                    return True
                else:
                    print("Browser initialization failed: No port in response")
                    return False
            else:
                print(f"Browser initialization failed: {response.get_error_message()}")
                return False

        except Exception as e:
            print("Failed to initialize browser instance:", e)
            self._initialized = False
            self._endpoint_url = None
            self._option = None
            return False

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
