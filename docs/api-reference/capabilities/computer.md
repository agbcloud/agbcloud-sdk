# Computer API Reference

## Related Tutorial

- [Computer Automation Guide](/computer/overview.md) - Complete guide to computer UI automation and control

## Overview

The Computer module provides comprehensive computer UI automation capabilities including mouse operations,keyboard input, screen capture, window management, and application control.


## Requirements

- Requires appropriate system permissions for UI automation
- May require specific desktop environment configuration



Computer module main class - container for all computer automation controllers.

## Computer

```python
class Computer(BaseService)
```

Handles computer UI automation operations in the AGB cloud environment.

This class acts as a container for specialized controllers:
- mouse: Mouse operations (click, move, drag, scroll)
- keyboard: Keyboard operations (type, press, release)
- window: Window management (list, activate, close, resize, etc.)
- app: Application management (start, stop, list installed/visible)
- screen: Screen operations (capture, size)

### click\_mouse

```python
def click_mouse(x: int, y: int, button=None, **kwargs)
```

Deprecated: Use computer.mouse.click() instead.

### move\_mouse

```python
def move_mouse(x: int, y: int, **kwargs)
```

Deprecated: Use computer.mouse.move() instead.

### drag\_mouse

```python
def drag_mouse(from_x: int,
               from_y: int,
               to_x: int,
               to_y: int,
               button=None,
               **kwargs)
```

Deprecated: Use computer.mouse.drag() instead.

### scroll

```python
def scroll(x: int, y: int, direction=None, amount: int = 1, **kwargs)
```

Deprecated: Use computer.mouse.scroll() instead.

### get\_cursor\_position

```python
def get_cursor_position()
```

Deprecated: Use computer.mouse.get_position() instead.

### input\_text

```python
def input_text(text: str, **kwargs)
```

Deprecated: Use computer.keyboard.type() instead.

### press\_keys

```python
def press_keys(keys, hold: bool = False, **kwargs)
```

Deprecated: Use computer.keyboard.press() instead.

### release\_keys

```python
def release_keys(keys, **kwargs)
```

Deprecated: Use computer.keyboard.release() instead.

### list\_root\_windows

```python
def list_root_windows(timeout_ms: int = 3000, **kwargs)
```

Deprecated: Use computer.window.list_root_windows() instead.

### get\_active\_window

```python
def get_active_window(**kwargs)
```

Deprecated: Use computer.window.get_active_window() instead.

### activate\_window

```python
def activate_window(window_id: int, **kwargs)
```

Deprecated: Use computer.window.activate() instead.

### close\_window

```python
def close_window(window_id: int, **kwargs)
```

Deprecated: Use computer.window.close() instead.

### maximize\_window

```python
def maximize_window(window_id: int, **kwargs)
```

Deprecated: Use computer.window.maximize() instead.

### minimize\_window

```python
def minimize_window(window_id: int, **kwargs)
```

Deprecated: Use computer.window.minimize() instead.

### restore\_window

```python
def restore_window(window_id: int, **kwargs)
```

Deprecated: Use computer.window.restore() instead.

### resize\_window

```python
def resize_window(window_id: int, width: int, height: int, **kwargs)
```

Deprecated: Use computer.window.resize() instead.

### fullscreen\_window

```python
def fullscreen_window(window_id: int, **kwargs)
```

Deprecated: Use computer.window.fullscreen() instead.

### focus\_mode

```python
def focus_mode(on: bool, **kwargs)
```

Deprecated: Use computer.window.focus_mode() instead.

### get\_installed\_apps

```python
def get_installed_apps(start_menu: bool = True,
                       desktop: bool = False,
                       ignore_system_apps: bool = True,
                       **kwargs)
```

Deprecated: Use computer.app.list_installed() instead.

### list\_visible\_apps

```python
def list_visible_apps(**kwargs)
```

Deprecated: Use computer.app.get_visible() instead.

### start\_app

```python
def start_app(start_cmd: str,
              work_directory: str = "",
              activity: str = "",
              **kwargs)
```

Deprecated: Use computer.app.start() instead.

### stop\_app\_by\_pname

```python
def stop_app_by_pname(pname: str, **kwargs)
```

Deprecated: Use computer.app.stop_by_pname() instead.

### stop\_app\_by\_pid

```python
def stop_app_by_pid(pid: int, **kwargs)
```

Deprecated: Use computer.app.stop_by_pid() instead.

### stop\_app\_by\_cmd

```python
def stop_app_by_cmd(stop_cmd: str, **kwargs)
```

Deprecated: Use computer.app.stop_by_cmd() instead.

### get\_screen\_size

```python
def get_screen_size(**kwargs)
```

Deprecated: Use computer.screen.get_size() instead.

### screenshot

```python
def screenshot(**kwargs)
```

Deprecated: Use computer.screen.capture() instead.

Mouse controller for computer automation operations.

## MouseController

```python
class MouseController(BaseService)
```

Controller for mouse operations.

### click

```python
def click(x: int,
          y: int,
          button: Union[MouseButton, str] = MouseButton.LEFT) -> BoolResult
```

Clicks the mouse at the specified screen coordinates.

**Arguments**:

- `x` _int_ - X coordinate in pixels (0 is left edge of screen).
- `y` _int_ - Y coordinate in pixels (0 is top edge of screen).
- `button` _Union[MouseButton, str], optional_ - Mouse button to click. Options:
  - MouseButton.LEFT or "left": Single left click
  - MouseButton.RIGHT or "right": Right click (context menu)
  - MouseButton.MIDDLE or "middle": Middle click (scroll wheel)
  Defaults to MouseButton.LEFT.


**Returns**:

    BoolResult: Object containing success status and error message if any.


**Raises**:

    ValueError: If button is not one of the valid options.

### move

```python
def move(x: int, y: int) -> BoolResult
```

Moves the mouse to the specified coordinates.

**Arguments**:

- `x` _int_ - X coordinate.
- `y` _int_ - Y coordinate.


**Returns**:

    BoolResult: Result object containing success status and error message if any.

### drag

```python
def drag(x1: int,
         y1: int,
         x2: int,
         y2: int,
         button: Union[MouseButton, str] = MouseButton.LEFT) -> BoolResult
```

Drags the mouse from one point to another.

**Arguments**:

- `x1` _int_ - Starting X coordinate.
- `y1` _int_ - Starting Y coordinate.
- `x2` _int_ - Ending X coordinate.
- `y2` _int_ - Ending Y coordinate.
- `button` _Union[MouseButton, str], optional_ - Button type. Can be MouseButton enum or string.
  Valid values: MouseButton.LEFT, MouseButton.RIGHT, MouseButton.MIDDLE
  or their string equivalents. Defaults to MouseButton.LEFT.
    Note: DOUBLE_LEFT is not supported for drag operations.


**Returns**:

    BoolResult: Result object containing success status and error message if any.


**Raises**:

    ValueError: If button is not a valid option.


**Notes**:

  - Performs a click-and-drag operation from start to end coordinates
  - Useful for selecting text, moving windows, or drawing
  - DOUBLE_LEFT button is not supported for drag operations
  - Use LEFT, RIGHT, or MIDDLE button only

### scroll

```python
def scroll(x: int,
           y: int,
           direction: Union[ScrollDirection, str] = ScrollDirection.UP,
           amount: int = 1) -> BoolResult
```

Scrolls the mouse wheel at the specified coordinates.

**Arguments**:

- `x` _int_ - X coordinate.
- `y` _int_ - Y coordinate.
- `direction` _Union[ScrollDirection, str], optional_ - Scroll direction. Can be ScrollDirection enum or string.
  Valid values: ScrollDirection.UP, ScrollDirection.DOWN, ScrollDirection.LEFT, ScrollDirection.RIGHT
  or their string equivalents. Defaults to ScrollDirection.UP.
- `amount` _int, optional_ - Scroll amount. Defaults to 1.


**Returns**:

    BoolResult: Result object containing success status and error message if any.


**Raises**:

    ValueError: If direction is not a valid option.


**Notes**:

  - Scroll operations are performed at the specified coordinates
  - The amount parameter controls how many scroll units to move
  - Larger amounts result in faster scrolling
  - Useful for navigating long documents or web pages

### get\_position

```python
def get_position() -> OperationResult
```

Gets the current cursor position.

**Returns**:

    OperationResult: Result object containing cursor position data
  with keys 'x' and 'y', and error message if any.


**Notes**:

  - Returns the absolute screen coordinates
  - Useful for verifying mouse movements
  - Position is in pixels from top-left corner (0, 0)

Keyboard controller for computer automation operations.

## KeyboardController

```python
class KeyboardController(BaseService)
```

Controller for keyboard operations.

### type

```python
def type(text: str) -> BoolResult
```

Types text into the currently focused input field.

**Arguments**:

- `text` _str_ - Text to input.


**Returns**:

    BoolResult: Result object containing success status and error message if any.


**Notes**:

  - Text is typed at the current focus location
  - Useful for filling forms or typing in text fields
  - Make sure the target input field is focused before calling

### press

```python
def press(keys: List[str], hold: bool = False) -> BoolResult
```

Presses the specified keys.

**Arguments**:

- `keys` _List[str]_ - List of keys to press (e.g., ["Ctrl", "a"]).
- `hold` _bool, optional_ - Whether to hold the keys. Defaults to False.
  When hold=True, remember to call release() afterwards.


**Returns**:

    BoolResult: Result object containing success status and error message if any.


**Notes**:

  - Key names are case-sensitive
  - Supports modifier keys like Ctrl, Alt, Shift
  - Can press multiple keys simultaneously for shortcuts
  - When hold=True, you must manually call release() to release the keys

### release

```python
def release(keys: List[str]) -> BoolResult
```

Releases the specified keys.

**Arguments**:

- `keys` _List[str]_ - List of keys to release (e.g., ["Ctrl", "a"]).


**Returns**:

    BoolResult: Result object containing success status and error message if any.


**Notes**:

  - Should be used after press() with hold=True
  - Key names are case-sensitive
  - Releases all keys specified in the list

Window manager for computer automation operations.

## WindowManager

```python
class WindowManager(BaseService)
```

Manager for window operations.

### list\_root\_windows

```python
def list_root_windows(timeout_ms: int = 3000) -> WindowListResult
```

Lists all root windows.

**Arguments**:

- `timeout_ms` _int, optional_ - Timeout in milliseconds. Defaults to 3000.


**Returns**:

    WindowListResult: Result object containing list of windows and error message if any.

### get\_active\_window

```python
def get_active_window() -> WindowInfoResult
```

Gets the currently active window.

**Returns**:

    WindowInfoResult: Result object containing active window info and error message if any.


**Notes**:

  - Returns the window that currently has focus
  - Active window receives keyboard input
  - Useful for determining which window is currently in use

### activate

```python
def activate(window_id: int) -> BoolResult
```

Activates the specified window.

**Arguments**:

- `window_id` _int_ - The ID of the window to activate.


**Returns**:

    BoolResult: Result object containing success status and error message if any.


**Notes**:

  - The window must exist in the system
  - Restoring returns a minimized or maximized window to its normal state
  - Works for windows that were previously minimized or maximized

### close

```python
def close(window_id: int) -> BoolResult
```

Closes the specified window.

**Arguments**:

- `window_id` _int_ - The ID of the window to close.


**Returns**:

    BoolResult: Result object containing success status and error message if any.


**Notes**:

  - The window must exist in the system
  - Use list_root_windows() to get available window IDs
  - Closing a window terminates it permanently

### maximize

```python
def maximize(window_id: int) -> BoolResult
```

Maximizes the specified window.

**Arguments**:

- `window_id` _int_ - The ID of the window to maximize.


**Returns**:

    BoolResult: Result object containing success status and error message if any.


**Notes**:

  - The window must exist in the system
  - Maximizing expands the window to fill the screen
  - Use restore() to return to previous size

### minimize

```python
def minimize(window_id: int) -> BoolResult
```

Minimizes the specified window.

**Arguments**:

- `window_id` _int_ - The ID of the window to minimize.


**Returns**:

    BoolResult: Result object containing success status and error message if any.


**Notes**:

  - The window must exist in the system
  - Minimizing hides the window in the taskbar
  - Use restore() or activate() to bring it back

### restore

```python
def restore(window_id: int) -> BoolResult
```

Restores the specified window.

**Arguments**:

- `window_id` _int_ - The ID of the window to restore.


**Returns**:

    BoolResult: Result object containing success status and error message if any.

### resize

```python
def resize(window_id: int, width: int, height: int) -> BoolResult
```

Resizes the specified window.

**Arguments**:

- `window_id` _int_ - The ID of the window to resize.
- `width` _int_ - New width of the window in pixels.
- `height` _int_ - New height of the window in pixels.


**Returns**:

    BoolResult: Result object containing success status and error message if any.


**Notes**:

  - The window must exist in the system
  - Width and height are in pixels
  - Some windows may have minimum or maximum size constraints

### fullscreen

```python
def fullscreen(window_id: int) -> BoolResult
```

Makes the specified window fullscreen.

**Arguments**:

- `window_id` _int_ - The ID of the window to make fullscreen.


**Returns**:

    BoolResult: Result object containing success status and error message if any.


**Notes**:

  - The window must exist in the system
  - Fullscreen mode hides window borders and taskbar
  - Different from maximize_window() which keeps window borders
  - Press F11 or ESC to exit fullscreen in most applications

### focus\_mode

```python
def focus_mode(on: bool) -> BoolResult
```

Toggles focus mode on or off.

**Arguments**:

- `on` _bool_ - True to enable focus mode, False to disable it.


**Returns**:

    BoolResult: Result object containing success status and error message if any.


**Notes**:

  - Focus mode helps reduce distractions by managing window focus
  - When enabled, may prevent background windows from stealing focus
  - Behavior depends on the window manager and OS settings

Application manager for computer automation operations.

## ApplicationManager

```python
class ApplicationManager(BaseService)
```

Manager for application operations.

### start

```python
def start(start_cmd: str,
          work_directory: str = "",
          activity: str = "") -> ProcessListResult
```

Starts the specified application.

**Arguments**:

- `start_cmd` _str_ - The command to start the application (executable name or full path, may include arguments).
- `work_directory` _str, optional_ - Working directory for the application. Defaults to "".
- `activity` _str, optional_ - Activity name to launch (for mobile apps). Defaults to "".


**Returns**:

    ProcessListResult: Result object containing list of processes started and error message if any.


**Notes**:

  - The start_cmd can be an executable name or full path
  - work_directory is optional and defaults to the system default
  - activity parameter is for mobile apps (Android)
  - Returns process information for all started processes

### stop\_by\_pname

```python
def stop_by_pname(pname: str) -> AppOperationResult
```

Stops an application by process name.

**Arguments**:

- `pname` _str_ - The process name of the application to stop.


**Returns**:

    AppOperationResult: Result object containing success status and error message if any.


**Notes**:

  - The process name should match exactly (case-sensitive on some systems)
  - This will stop all processes matching the given name
  - If multiple instances are running, all will be terminated
  - The .exe extension may be required on Windows

### stop\_by\_pid

```python
def stop_by_pid(pid: int) -> AppOperationResult
```

Stops an application by process ID.

**Arguments**:

- `pid` _int_ - The process ID of the application to stop.


**Returns**:

    AppOperationResult: Result object containing success status and error message if any.


**Notes**:

  - PID must be a valid process ID
  - More precise than stopping by name (only stops specific process)
  - The process must be owned by the session or have appropriate permissions
  - PID can be obtained from start() or visible()

### stop\_by\_cmd

```python
def stop_by_cmd(stop_cmd: str) -> AppOperationResult
```

Stops an application by executing a shell command (e.g. kill by PID).

**Arguments**:

- `stop_cmd` _str_ - A shell command to stop/kill the process, e.g. "kill -9 1234"
  where 1234 is the process ID. Get the PID from app.start() or app.get_visible().
  This is NOT the stop_cmd field from list_installed (that field may be absent).


**Returns**:

    AppOperationResult: Result object containing success status and error message if any.

### list\_installed

```python
def list_installed(start_menu: bool = True,
                   desktop: bool = False,
                   ignore_system_apps: bool = True) -> InstalledAppListResult
```

Gets the list of installed applications.

**Arguments**:

- `start_menu` _bool, optional_ - Whether to include start menu applications. Defaults to True.
- `desktop` _bool, optional_ - Whether to include desktop applications. Defaults to False.
- `ignore_system_apps` _bool, optional_ - Whether to ignore system applications. Defaults to True.


**Returns**:

    InstalledAppListResult: Result object containing list of installed apps and error message if any.


**Notes**:

  - start_menu parameter includes applications from Start Menu
  - desktop parameter includes shortcuts from Desktop
  - ignore_system_apps parameter filters out system applications
  - Each app object contains name, start_cmd, and optionally work_directory

### get\_visible

```python
def get_visible() -> ProcessListResult
```

Lists all applications with visible windows.

Returns detailed process information for applications that have visible windows,
including process ID, name, command line, and other system information.
This is useful for system monitoring and process management tasks.

**Returns**:

    ProcessListResult: Result object containing list of visible applications
  with detailed process information.


**Notes**:

  - Only returns applications with visible windows
  - Hidden or minimized windows may not appear
  - Useful for monitoring currently active applications
  - Process information includes PID, name, and command line

Screen controller for computer automation operations.

## ScreenController

```python
class ScreenController(BaseService)
```

Controller for screen operations.

### capture

```python
def capture() -> OperationResult
```

Takes a screenshot of the current screen.

**Returns**:

    OperationResult: Result object containing the path to the screenshot
  and error message if any.


**Notes**:

  - Returns an OSS URL to the screenshot image
  - Screenshot captures the entire screen
  - Useful for debugging and verification
  - Image format is typically PNG


**See Also**:

  get_size

### get\_size

```python
def get_size() -> OperationResult
```

Gets the screen size and DPI scaling factor.

**Returns**:

    OperationResult: Result object containing screen size data (keys 'width', 'height', 'dpiScalingFactor')
  in result.data, and error message if any.


**Notes**:

  - Returns the full screen dimensions in pixels
  - DPI scaling factor affects coordinate calculations on high-DPI displays
  - Use this to determine valid coordinate ranges for mouse operations

## Best Practices

1. Use appropriate timeouts for window operations
2. Take screenshots for debugging and verification
3. Handle coordinate calculations properly for different screen resolutions
4. Verify window existence before attempting window operations
5. Use proper key combinations and timing for keyboard operations
6. Clean up application processes after automation tasks
7. Handle application startup and shutdown gracefully

## Related Resources

- [Session API Reference](../session.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
