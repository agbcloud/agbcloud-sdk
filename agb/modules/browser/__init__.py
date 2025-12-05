"""
Browser automation operations for the AGB SDK.
"""

from .browser import (
    Browser,
    BrowserFingerprintContext,
    BrowserFingerprint,
    BrowserOption,
    BrowserProxy,
    BrowserScreen,
    BrowserViewport,
)
from .fingerprint import (
    FingerprintFormat,
    BrowserFingerprintGenerator,
)
from .browser_agent import (
    ActOptions,
    ActResult,
    BrowserAgent,
    ExtractOptions,
    ObserveOptions,
    ObserveResult,
)

__all__ = [
    "Browser",
    "BrowserFingerprintContext",
    "BrowserOption",
    "BrowserViewport",
    "BrowserScreen",
    "BrowserFingerprint",
    "BrowserProxy",
    "FingerprintFormat",
    "BrowserFingerprintGenerator",
    "BrowserAgent",
    "ActOptions",
    "ActResult",
    "ObserveOptions",
    "ObserveResult",
    "ExtractOptions",
]
