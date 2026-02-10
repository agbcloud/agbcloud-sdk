"""
Computer module for UI automation operations.
"""

from enum import Enum
from typing import List, Optional, Any, Dict

# Type definitions
class MouseButton(str, Enum):
    """Mouse button types for click and drag operations."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"
    DOUBLE_LEFT = "double_left"


class ScrollDirection(str, Enum):
    """Scroll direction for scroll operations."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class Window:
    """Represents a window in the system."""

    def __init__(
        self,
        window_id: int,
        title: str,
        absolute_upper_left_x: Optional[int] = None,
        absolute_upper_left_y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        pid: Optional[int] = None,
        pname: Optional[str] = None,
        child_windows: Optional[List["Window"]] = None,
    ):
        self.window_id = window_id
        self.title = title
        self.absolute_upper_left_x = absolute_upper_left_x
        self.absolute_upper_left_y = absolute_upper_left_y
        self.width = width
        self.height = height
        self.pid = pid
        self.pname = pname
        self.child_windows = child_windows or []

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "Window":
        child_windows = []
        if "child_windows" in data and data["child_windows"]:
            child_windows = [cls._from_dict(child) for child in data["child_windows"]]
        return cls(
            window_id=data.get("window_id", 0),
            title=data.get("title", ""),
            absolute_upper_left_x=data.get("absolute_upper_left_x"),
            absolute_upper_left_y=data.get("absolute_upper_left_y"),
            width=data.get("width"),
            height=data.get("height"),
            pid=data.get("pid"),
            pname=data.get("pname"),
            child_windows=child_windows,
        )


class InstalledApp:
    """Represents an installed application."""

    def __init__(
        self,
        name: str,
        start_cmd: str,
        stop_cmd: Optional[str] = None,
        work_directory: Optional[str] = None,
    ):
        self.name = name
        self.start_cmd = start_cmd
        self.stop_cmd = stop_cmd
        self.work_directory = work_directory

    @classmethod
    def _from_dict(cls, data: dict) -> "InstalledApp":
        return cls(
            name=data.get("name", ""),
            start_cmd=data.get("start_cmd", ""),
            stop_cmd=data.get("stop_cmd"),
            work_directory=data.get("work_directory"),
        )


class Process:
    """Represents a running process."""

    def __init__(self, pname: str, pid: int, cmdline: Optional[str] = None):
        self.pname = pname
        self.pid = pid
        self.cmdline = cmdline

    @classmethod
    def _from_dict(cls, data: dict) -> "Process":
        return cls(
            pname=data.get("pname", ""),
            pid=data.get("pid", 0),
            cmdline=data.get("cmdline"),
        )


# Import sub-controllers and main class
try:
    from .mouse import MouseController
    from .keyboard import KeyboardController
    from .window import WindowManager
    from .app import ApplicationManager
    from .screen import ScreenController
    from .computer import Computer
except ImportError:
    # Handle case where sub-controllers are not yet created
    pass

__all__ = [
    "MouseButton",
    "ScrollDirection",
    "Window",
    "InstalledApp",
    "Process",
    "MouseController",
    "KeyboardController",
    "WindowManager",
    "ApplicationManager",
    "ScreenController",
    "Computer",
]
