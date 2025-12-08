import json
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, asdict
from playwright.async_api import async_playwright
from agb.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ScreenFingerprint:
    """Screen fingerprint data structure."""
    availHeight: int
    availWidth: int
    availTop: int
    availLeft: int
    colorDepth: int
    height: int
    pixelDepth: int
    width: int
    devicePixelRatio: float
    pageXOffset: int
    pageYOffset: int
    innerHeight: int
    outerHeight: int
    outerWidth: int
    innerWidth: int
    screenX: int
    clientWidth: int
    clientHeight: int
    hasHDR: bool


@dataclass
class Brand:
    """Brand information data structure."""
    brand: str
    version: str


@dataclass
class UserAgentData:
    """User agent data structure."""
    brands: List[Brand]
    mobile: bool
    platform: str
    architecture: str
    bitness: str
    fullVersionList: List[Brand]
    model: str
    platformVersion: str
    uaFullVersion: str


@dataclass
class ExtraProperties:
    """Navigator extra properties data structure."""
    vendorFlavors: List[str]
    isBluetoothSupported: bool
    globalPrivacyControl: Optional[Any]
    pdfViewerEnabled: bool
    installedApps: List[Any]


@dataclass
class NavigatorFingerprint:
    """Navigator fingerprint data structure."""
    userAgent: str
    userAgentData: UserAgentData
    doNotTrack: str
    appCodeName: str
    appName: str
    appVersion: str
    oscpu: str
    webdriver: str
    language: str
    languages: List[str]
    platform: str
    deviceMemory: Optional[int]
    hardwareConcurrency: int
    product: str
    productSub: str
    vendor: str
    vendorSub: str
    maxTouchPoints: Optional[int]
    extraProperties: ExtraProperties


@dataclass
class VideoCard:
    """Video card information data structure."""
    renderer: str
    vendor: str


@dataclass
class Fingerprint:
    """Main fingerprint data structure."""
    screen: ScreenFingerprint
    navigator: NavigatorFingerprint
    videoCodecs: Dict[str, str]
    audioCodecs: Dict[str, str]
    pluginsData: Dict[str, str]
    battery: Optional[Dict[str, str]]
    videoCard: VideoCard
    multimediaDevices: List[str]
    fonts: List[str]
    mockWebRTC: bool
    slim: Optional[bool]


@dataclass
class FingerprintFormat:
    """Complete fingerprint format including fingerprint data and headers."""
    fingerprint: Fingerprint
    headers: Dict[str, str]

    @classmethod
    def load(cls, data: Union[dict, str]) -> 'FingerprintFormat':
        """
        Load fingerprint from dictionary or JSON string.

        This is the recommended public API for loading fingerprint data.

        Args:
            data: Either a dictionary or JSON string containing fingerprint data

        Returns:
            FingerprintFormat: Loaded fingerprint format object

        Raises:
            ValueError: If data is invalid or cannot be parsed

        Example:
            ```python
            # From dictionary
            fingerprint = FingerprintFormat.load({"fingerprint": {...}, "headers": {...}})

            # From JSON string
            fingerprint = FingerprintFormat.load('{"fingerprint": {...}, "headers": {...}}')
            ```
        """
        if isinstance(data, str):
            return cls._from_json(data)
        elif isinstance(data, dict):
            return cls._from_dict(data)
        else:
            raise ValueError(f"Invalid data type: expected dict or str, got {type(data)}")

    def _to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return asdict(self)

    def _to_json(self, indent: int = 2, ensure_ascii: bool = False) -> str:
        """Convert to JSON string format."""
        return json.dumps(self._to_dict(), indent=indent, ensure_ascii=ensure_ascii)

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> 'FingerprintFormat':
        """Create FingerprintFormat from dictionary data."""
        if not data or not isinstance(data, dict):
            raise ValueError("Invalid data: expected a dictionary")

        fingerprint_dict = data.get('fingerprint') or {}
        headers_dict = data.get('headers') or {}

        # Convert nested dictionaries to dataclass instances
        screen_dict = fingerprint_dict.get('screen') or {}
        try:
            screen = ScreenFingerprint(**screen_dict)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Failed to create ScreenFingerprint: {e}")

        # Handle UserAgentData - safely get navigator data
        nav_dict = fingerprint_dict.get('navigator') or {}
        user_agent_data_dict = nav_dict.get('userAgentData') or {}

        # Handle brands and fullVersionList safely
        brands_data = user_agent_data_dict.get('brands', [])
        brands = []
        if isinstance(brands_data, list):
            for brand_data in brands_data:
                if isinstance(brand_data, dict):
                    brands.append(Brand(
                        brand=brand_data.get('brand', ''),
                        version=brand_data.get('version', '')
                    ))

        full_version_list_data = user_agent_data_dict.get('fullVersionList', [])
        full_version_list = []
        if isinstance(full_version_list_data, list):
            for brand_data in full_version_list_data:
                if isinstance(brand_data, dict):
                    full_version_list.append(Brand(
                        brand=brand_data.get('brand', ''),
                        version=brand_data.get('version', '')
                    ))

        user_agent_data = UserAgentData(
            brands=brands,
            mobile=user_agent_data_dict.get('mobile', False),
            platform=user_agent_data_dict.get('platform', ''),
            architecture=user_agent_data_dict.get('architecture', ''),
            bitness=user_agent_data_dict.get('bitness', ''),
            fullVersionList=full_version_list,
            model=user_agent_data_dict.get('model', ''),
            platformVersion=user_agent_data_dict.get('platformVersion', ''),
            uaFullVersion=user_agent_data_dict.get('uaFullVersion', '')
        )

        # Handle ExtraProperties
        extra_props_dict = nav_dict.get('extraProperties') or {}
        extra_props = ExtraProperties(
            vendorFlavors=extra_props_dict.get('vendorFlavors', []),
            isBluetoothSupported=extra_props_dict.get('isBluetoothSupported', False),
            globalPrivacyControl=extra_props_dict.get('globalPrivacyControl'),
            pdfViewerEnabled=extra_props_dict.get('pdfViewerEnabled', True),
            installedApps=extra_props_dict.get('installedApps', [])
        )

        # Create NavigatorFingerprint
        navigator = NavigatorFingerprint(
            userAgent=nav_dict.get('userAgent', ''),
            userAgentData=user_agent_data,
            doNotTrack=nav_dict.get('doNotTrack', ''),
            appCodeName=nav_dict.get('appCodeName', ''),
            appName=nav_dict.get('appName', ''),
            appVersion=nav_dict.get('appVersion', ''),
            oscpu=nav_dict.get('oscpu', ''),
            webdriver=nav_dict.get('webdriver', ''),
            language=nav_dict.get('language', ''),
            languages=nav_dict.get('languages', []),
            platform=nav_dict.get('platform', ''),
            deviceMemory=nav_dict.get('deviceMemory'),
            hardwareConcurrency=nav_dict.get('hardwareConcurrency', 8),
            product=nav_dict.get('product', ''),
            productSub=nav_dict.get('productSub', ''),
            vendor=nav_dict.get('vendor', ''),
            vendorSub=nav_dict.get('vendorSub', ''),
            maxTouchPoints=nav_dict.get('maxTouchPoints'),
            extraProperties=extra_props
        )

        # Create VideoCard
        video_card_dict = fingerprint_dict.get('videoCard') or {}
        try:
            video_card = VideoCard(**video_card_dict)
        except (TypeError, ValueError) as e:
            logger.warning(f"Failed to create VideoCard: {e}, using defaults")
            video_card = VideoCard(renderer="Unknown", vendor="Unknown")

        # Create main Fingerprint
        fingerprint = Fingerprint(
            screen=screen,
            navigator=navigator,
            videoCodecs=fingerprint_dict.get('videoCodecs', {}),
            audioCodecs=fingerprint_dict.get('audioCodecs', {}),
            pluginsData=fingerprint_dict.get('pluginsData', {}),
            battery=fingerprint_dict.get('battery'),
            videoCard=video_card,
            multimediaDevices=fingerprint_dict.get('multimediaDevices', []),
            fonts=fingerprint_dict.get('fonts', []),
            mockWebRTC=fingerprint_dict.get('mockWebRTC', False),
            slim=fingerprint_dict.get('slim')
        )

        return cls(fingerprint=fingerprint, headers=headers_dict)

    @classmethod
    def _from_json(cls, json_str: str) -> 'FingerprintFormat':
        """Create FingerprintFormat from JSON string."""
        data = json.loads(json_str)
        return cls._from_dict(data)

    @classmethod
    def create(
        cls,
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
        slim: Optional[bool] = None
    ) -> 'FingerprintFormat':
        """
        Create FingerprintFormat directly using component classes.

        Args:
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

        Returns:
            FingerprintFormat: Complete fingerprint format object
        """
        fingerprint = Fingerprint(
            screen=screen,
            navigator=navigator,
            videoCodecs=video_codecs or {},
            audioCodecs=audio_codecs or {},
            pluginsData=plugins_data or {},
            battery=battery,
            videoCard=video_card,
            multimediaDevices=multimedia_devices or [],
            fonts=fonts or [],
            mockWebRTC=mock_webrtc,
            slim=slim
        )

        return cls(fingerprint=fingerprint, headers=headers)



class BrowserFingerprintGenerator:
    """Browser fingerprint generator class for extracting comprehensive browser fingerprint data.
This class uses Playwright to launch a local browser and collect fingerprint information
including screen properties, navigator data, codecs, plugins, WebGL info, and HTTP headers."""

    def __init__(self, headless: bool = False, use_chrome_channel: bool = True):
        """
        Initialize the fingerprint generator.

        Args:
            headless: Whether to run browser in headless mode
            use_chrome_channel: Whether to use Chrome channel
        """
        self.headless = headless
        self.use_chrome_channel = use_chrome_channel

    async def generate_fingerprint(self) -> Optional[FingerprintFormat]:
        """
        Extract comprehensive browser fingerprint using Playwright.

        Returns:
            Optional[FingerprintFormat]: FingerprintFormat object containing fingerprint and headers, or None if generation failed
        """
        try:
            logger.info("Starting fingerprint generation")

            async with async_playwright() as p:
                # Launch Chrome browser with specific options
                launch_options = {
                    'headless': self.headless,
                    'args': ['--start-maximized']
                }

                if self.use_chrome_channel:
                    launch_options['channel'] = 'chrome'

                browser = await p.chromium.launch(**launch_options)
                context = await browser.new_context(no_viewport=True)
                page = await context.new_page()

                # Navigate to a test page to ensure proper loading
                await page.goto('about:blank')

                logger.info("Extracting comprehensive browser fingerprint...")

                # Extract comprehensive fingerprint data
                fingerprint_data = await self._extract_fingerprint_data(page)

                # Get request headers
                headers_data = await self._extract_headers_data(page)

                await browser.close()

                # Combine fingerprint and headers using FingerprintFormat
                fingerprint_format = FingerprintFormat._from_dict({
                    "fingerprint": fingerprint_data,
                    "headers": headers_data
                })

                logger.info("Fingerprint generation completed successfully!")
                return fingerprint_format

        except Exception as e:
            logger.error(f"Error generating fingerprint: {e}")
            return None

    async def generate_fingerprint_to_file(self, output_filename: str = "fingerprint_output.json") -> bool:
        """
        Extract comprehensive browser fingerprint and save to file.

        Args:
            output_filename: Name of the file to save fingerprint data

        Returns:
            bool: True if fingerprint generation and saving succeeded, False otherwise
        """
        try:
            logger.info(f"Starting fingerprint generation, output file: {output_filename}")

            # Generate fingerprint data (FingerprintFormat object)
            fingerprint_format = await self.generate_fingerprint()

            if fingerprint_format is None:
                logger.error("Failed to generate fingerprint data")
                return False

            # Convert to JSON string and save to file
            fingerprint_json = fingerprint_format._to_json(indent=2, ensure_ascii=False)
            success = await self._save_to_file(fingerprint_json, output_filename)

            if success:
                logger.info(f"Fingerprint generation completed successfully! Saved to {output_filename}")
                return True
            else:
                logger.error("Failed to save fingerprint data")
                return False

        except Exception as e:
            logger.error(f"Error generating fingerprint to file: {e}")
            return False

    async def _extract_fingerprint_data(self, page):
        """Extract fingerprint data from the page."""
        return await page.evaluate("""
        async () => {
            // Helper function to get audio codec support
            function getAudioCodecs() {
                const audio = document.createElement('audio');
                return {
                    ogg: audio.canPlayType('audio/ogg; codecs="vorbis"') || '',
                    mp3: audio.canPlayType('audio/mpeg') || '',
                    wav: audio.canPlayType('audio/wav; codecs="1"') || '',
                    m4a: audio.canPlayType('audio/x-m4a') || '',
                    aac: audio.canPlayType('audio/aac') || ''
                };
            }

            // Helper function to get video codec support
            function getVideoCodecs() {
                const video = document.createElement('video');
                return {
                    ogg: video.canPlayType('video/ogg; codecs="theora"') || '',
                    h264: video.canPlayType('video/mp4; codecs="avc1.42E01E"') || '',
                    webm: video.canPlayType('video/webm; codecs="vp8, vorbis"') || ''
                };
            }

            // Helper function to get plugins data
            function getPluginsData() {
                const plugins = [];
                const mimeTypes = [];

                for (let i = 0; i < navigator.plugins.length; i++) {
                    const plugin = navigator.plugins[i];
                    const pluginData = {
                        name: plugin.name,
                        description: plugin.description,
                        filename: plugin.filename,
                        mimeTypes: []
                    };

                    for (let j = 0; j < plugin.length; j++) {
                        const mimeType = plugin[j];
                        pluginData.mimeTypes.push({
                            type: mimeType.type,
                            suffixes: mimeType.suffixes,
                            description: mimeType.description,
                            enabledPlugin: plugin.name
                        });

                        mimeTypes.push(`${mimeType.description}~~${mimeType.type}~~${mimeType.suffixes}`);
                    }

                    plugins.push(pluginData);
                }

                return { plugins, mimeTypes };
            }

            // Helper function to get battery info
            async function getBatteryInfo() {
                try {
                    if ('getBattery' in navigator) {
                        const battery = await navigator.getBattery();
                        return {
                            charging: battery.charging,
                            chargingTime: battery.chargingTime,
                            dischargingTime: battery.dischargingTime,
                            level: battery.level
                        };
                    }
                } catch (e) {
                    console.log('Battery API not supported');
                }

                return {
                    charging: true,
                    chargingTime: 0,
                    dischargingTime: null,
                    level: 1
                };
            }

            // Helper function to get WebGL info
            function getWebGLInfo() {
                try {
                    const canvas = document.createElement('canvas');
                    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

                    if (gl) {
                        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                        return {
                            renderer: debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER),
                            vendor: debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR)
                        };
                    }
                } catch (e) {
                    console.log('WebGL not supported');
                }

                return {
                    renderer: "Adreno (TM) 735",
                    vendor: "Qualcomm"
                };
            }

            // Helper function to get multimedia devices
            async function getMultimediaDevices() {
                try {
                    if ('mediaDevices' in navigator && 'enumerateDevices' in navigator.mediaDevices) {
                        const devices = await navigator.mediaDevices.enumerateDevices();
                        const speakers = [];
                        const micros = [];
                        const webcams = [];

                        devices.forEach(device => {
                            const deviceInfo = {
                                deviceId: device.deviceId || '',
                                kind: device.kind,
                                label: device.label || '',
                                groupId: device.groupId || ''
                            };

                            if (device.kind === 'audiooutput') {
                                speakers.push(deviceInfo);
                            } else if (device.kind === 'audioinput') {
                                micros.push(deviceInfo);
                            } else if (device.kind === 'videoinput') {
                                webcams.push(deviceInfo);
                            }
                        });

                        return { speakers, micros, webcams };
                    }
                } catch (e) {
                    console.log('Media devices not accessible');
                }

                return {
                    speakers: [{ deviceId: '', kind: 'audiooutput', label: '', groupId: '' }],
                    micros: [{ deviceId: '', kind: 'audioinput', label: '', groupId: '' }],
                    webcams: []
                };
            }

            // Helper function to get available fonts
            function getFonts() {
                // This is a simplified version - in practice, font detection is more complex
                const testFonts = [
                    'Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana',
                    'Georgia', 'Palatino', 'Garamond', 'Bookman', 'Comic Sans MS',
                    'Trebuchet MS', 'Arial Black', 'Impact'
                ];

                const availableFonts = [];
                const testString = 'mmmmmmmmmmlli';
                const testSize = '72px';
                const baseWidth = {};
                const baseHeight = {};

                // Create a canvas for font testing
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');

                // Test with default fonts first
                const defaultFonts = ['monospace', 'sans-serif', 'serif'];
                defaultFonts.forEach(font => {
                    context.font = testSize + ' ' + font;
                    const metrics = context.measureText(testString);
                    baseWidth[font] = metrics.width;
                    baseHeight[font] = metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent;
                });

                // Test each font
                testFonts.forEach(font => {
                    let detected = false;
                    defaultFonts.forEach(baseFont => {
                        context.font = testSize + ' ' + font + ', ' + baseFont;
                        const metrics = context.measureText(testString);
                        const width = metrics.width;
                        const height = metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent;

                        if (width !== baseWidth[baseFont] || height !== baseHeight[baseFont]) {
                            detected = true;
                        }
                    });

                    if (detected) {
                        availableFonts.push(font);
                    }
                });

                return availableFonts;
            }

            // Get battery info
            const batteryInfo = await getBatteryInfo();

            // Get multimedia devices
            const multimediaDevices = await getMultimediaDevices();

            // Build the complete fingerprint object
            const fingerprint = {
                screen: {
                    availTop: screen.availTop,
                    availLeft: screen.availLeft,
                    pageXOffset: window.pageXOffset,
                    pageYOffset: window.pageYOffset,
                    screenX: window.screenX,
                    hasHDR: screen.colorDepth > 24,
                    width: screen.width,
                    height: screen.height,
                    availWidth: screen.availWidth,
                    availHeight: screen.availHeight,
                    clientWidth: document.documentElement.clientWidth,
                    clientHeight: document.documentElement.clientHeight,
                    innerWidth: window.innerWidth,
                    innerHeight: window.innerHeight,
                    outerWidth: window.outerWidth,
                    outerHeight: window.outerHeight,
                    colorDepth: screen.colorDepth,
                    pixelDepth: screen.pixelDepth,
                    devicePixelRatio: window.devicePixelRatio
                },
                navigator: {
                    userAgent: navigator.userAgent,
                    userAgentData: navigator.userAgentData ? {
                        brands: navigator.userAgentData.brands || [],
                        mobile: navigator.userAgentData.mobile || false,
                        platform: navigator.userAgentData.platform || ''
                    } : null,
                    language: navigator.language,
                    languages: navigator.languages || [],
                    platform: navigator.platform,
                    deviceMemory: navigator.deviceMemory || 8,
                    hardwareConcurrency: navigator.hardwareConcurrency || 8,
                    maxTouchPoints: navigator.maxTouchPoints || 0,
                    product: navigator.product,
                    productSub: navigator.productSub,
                    vendor: navigator.vendor,
                    vendorSub: navigator.vendorSub,
                    doNotTrack: navigator.doNotTrack,
                    appCodeName: navigator.appCodeName,
                    appName: navigator.appName,
                    appVersion: navigator.appVersion,
                    oscpu: navigator.oscpu,
                    extraProperties: {
                        vendorFlavors: ['chrome'],
                        globalPrivacyControl: navigator.globalPrivacyControl || null,
                        pdfViewerEnabled: navigator.pdfViewerEnabled || true,
                        installedApps: []
                    },
                    webdriver: false
                },
                audioCodecs: getAudioCodecs(),
                videoCodecs: getVideoCodecs(),
                pluginsData: getPluginsData(),
                battery: batteryInfo,
                videoCard: getWebGLInfo(),
                multimediaDevices: multimediaDevices,
                fonts: getFonts(),
                mockWebRTC: false,
                slim: false
            };

            return fingerprint;
        }
        """)

    async def _extract_headers_data(self, page):
        """Extract headers data from httpbin."""
        try:
            logger.info("Getting request headers...")
            await page.goto('https://httpbin.org/headers', wait_until='networkidle')

            # Extract headers from the response
            all_headers = await page.evaluate("""
            () => {
                try {
                    const preElement = document.querySelector('pre');
                    if (preElement) {
                        const data = JSON.parse(preElement.textContent);
                        return data.headers || {};
                    }
                } catch (e) {
                    console.log('Failed to parse headers:', e);
                }
                return {};
            }
            """)

            # Filter only the key headers from the example
            key_headers = [
                'sec-ch-ua',
                'sec-ch-ua-mobile',
                'sec-ch-ua-platform',
                'upgrade-insecure-requests',
                'user-agent',
                'accept',
                'sec-fetch-site',
                'sec-fetch-mode',
                'sec-fetch-user',
                'sec-fetch-dest',
                'accept-encoding',
                'accept-language'
            ]

            headers_data = {}
            # Convert all_headers keys to lowercase for case-insensitive matching
            all_headers_lower = {k.lower(): v for k, v in all_headers.items()}

            for header in key_headers:
                header_lower = header.lower()
                if header_lower in all_headers_lower:
                    headers_data[header] = all_headers_lower[header_lower]

            return headers_data

        except Exception as e:
            logger.warning(f"Failed to extract headers: {e}")
            return {}

    async def _save_to_file(self, json_data, filename):
        """Save JSON string data to a file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(json_data)
            logger.info(f"Fingerprint data saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save fingerprint data: {e}")
            return False
