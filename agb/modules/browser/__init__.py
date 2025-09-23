"""
Browser automation operations for the AGB SDK.
"""

from .browser import (
    Browser,
    BrowserFingerprint,
    BrowserOption,
    BrowserProxy,
    BrowserScreen,
    BrowserViewport,
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
    "BrowserOption",
    "BrowserViewport",
    "BrowserScreen",
    "BrowserFingerprint",
    "BrowserProxy",
    "BrowserAgent",
    "ActOptions",
    "ActResult",
    "ObserveOptions",
    "ObserveResult",
    "ExtractOptions",
]
