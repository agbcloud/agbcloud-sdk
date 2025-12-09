# Computer Automation Guide

## Overview

The AGB SDK provides comprehensive computer automation capabilities in the cloud. You can control desktop environments through mouse operations, keyboard input, screen capture, application management and window control. This guide covers everything from basic UI interactions to advanced desktop automation workflows.

## Quick Reference (1 minute)

```python
from agb import AGB
from agb.session_params import CreateSessionParams
from agb import MouseButton, ScrollDirection

agb = AGB()
params = CreateSessionParams(image_id="agb-linux-test-5")
session = agb.create(params).session

# Mouse operations
result = session.computer.click_mouse(500, 300, MouseButton.LEFT)
session.computer.move_mouse(600, 400)
session.computer.scroll(500, 500, ScrollDirection.DOWN, 3)

# Keyboard operations
session.computer.input_text("Hello, World!")
session.computer.press_keys(["Ctrl", "a"])

# Screen operations
screenshot_result = session.computer.screenshot()
screen_size = session.computer.get_screen_size()

# Application management
apps_result = session.computer.get_installed_apps()
start_result = session.computer.start_app(start_cmd)
session.computer.stop_app_by_pname(pname)

# Window management
windows_result = session.computer.list_root_windows()
if windows_result.success and windows_result.windows:
    window_id = windows_result.windows[0].window_id
    session.computer.activate_window(window_id)
    session.computer.maximize_window(window_id)

agb.delete(session)
```

## Basic Usage (5 minutes)

### Session Setup

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
params = CreateSessionParams(image_id="agb-linux-test-5")
result = agb.create(params)
session = result.session

if result.success:
    print(f"Session created: {session.session_id}")
else:
    print(f"Failed to create session: {result.error_message}")
    exit(1)
```

**Supported System Images:**
- `agb-linux-test-5` - Linux desktop environment with GUI for computer automation

## UI Operations (15 minutes)

### Mouse Operations

#### Click Operations

```python
from agb import MouseButton

# Left click
result = session.computer.click_mouse(x=500, y=300, button=MouseButton.LEFT)
if result.success:
    print("Left click successful")

# Right click (context menu)
result = session.computer.click_mouse(x=500, y=300, button=MouseButton.RIGHT)
if result.success:
    print("Right click successful")

# Middle click (scroll wheel)
result = session.computer.click_mouse(x=500, y=300, button=MouseButton.MIDDLE)
if result.success:
    print("Middle click successful")

# Double left click
result = session.computer.click_mouse(x=500, y=300, button=MouseButton.DOUBLE_LEFT)
if result.success:
    print("Double click successful")
```

**Supported Mouse Buttons:**
- `MouseButton.LEFT` - Single left click
- `MouseButton.RIGHT` - Right click (context menu)
- `MouseButton.MIDDLE` - Middle click (scroll wheel)
- `MouseButton.DOUBLE_LEFT` - Double left click

#### Move Mouse

```python
result = session.computer.move_mouse(x=600, y=400)
if result.success:
    print("Mouse moved successfully")

# Get current cursor position
cursor_result = session.computer.get_cursor_position()
if cursor_result.success:
    import json
    cursor_data = json.loads(cursor_result.data)
    print(f"Cursor at x={cursor_data['x']}, y={cursor_data['y']}")
```

#### Drag Operations

```python
from agb import MouseButton

# Drag with left button
result = session.computer.drag_mouse(
    from_x=100, 
    from_y=100, 
    to_x=200, 
    to_y=200, 
    button=MouseButton.LEFT
)
if result.success:
    print("Drag operation successful")

# Drag with right button
result = session.computer.drag_mouse(
    from_x=300, 
    from_y=300, 
    to_x=400, 
    to_y=400, 
    button=MouseButton.RIGHT
)
```

**Note:** `DOUBLE_LEFT` is not supported for drag operations. Use `LEFT`, `RIGHT`, or `MIDDLE` only.

#### Scroll Operations

```python
from agb import ScrollDirection

# Scroll up
result = session.computer.scroll(x=500, y=500, direction=ScrollDirection.UP, amount=3)
if result.success:
    print("Scrolled up successfully")

# Scroll down
result = session.computer.scroll(x=500, y=500, direction=ScrollDirection.DOWN, amount=5)
if result.success:
    print("Scrolled down successfully")

# Horizontal scrolling
result = session.computer.scroll(x=500, y=500, direction=ScrollDirection.LEFT, amount=2)
result = session.computer.scroll(x=500, y=500, direction=ScrollDirection.RIGHT, amount=2)
```

**Supported Scroll Directions:**
- `ScrollDirection.UP` - Scroll up
- `ScrollDirection.DOWN` - Scroll down
- `ScrollDirection.LEFT` - Scroll left
- `ScrollDirection.RIGHT` - Scroll right

### Keyboard Operations

#### Text Input

```python
result = session.computer.input_text("Hello AgentBay!")
if result.success:
    print("Text input successful")
```

#### Key Combinations

```python
# Press Ctrl+A to select all
result = session.computer.press_keys(keys=["Ctrl", "a"])
if result.success:
    print("Select all command sent")

# Press Ctrl+C to copy
result = session.computer.press_keys(keys=["Ctrl", "c"])

# Press Ctrl+V to paste
result = session.computer.press_keys(keys=["Ctrl", "v"])
```

#### Hold and Release Keys

```python
# Hold Ctrl key
result = session.computer.press_keys(keys=["Ctrl"], hold=True)
if result.success:
    print("Ctrl key held")

# Release Ctrl key
result = session.computer.release_keys(keys=["Ctrl"])
if result.success:
    print("Ctrl key released")
```

### Screen Operations

#### Take Screenshot

```python
result = session.computer.screenshot()
if result.success:
    screenshot_url = result.data
    print(f"Screenshot URL: {screenshot_url}")
    # The URL points to the screenshot image in cloud storage
```

#### Get Screen Information

```python
result = session.computer.get_screen_size()
if result.success:
    import json
    screen_data = json.loads(result.data)
    print(f"Screen size: {screen_data['width']}x{screen_data['height']}")
    print(f"DPI scaling: {screen_data['dpiScalingFactor']}")
```

## Application Management (15 minutes)

### Discovering Installed Applications

```python
result = session.computer.get_installed_apps(
    start_menu=True,
    desktop=False,
    ignore_system_apps=True
)

if result.success:
    apps = result.data
    print(f"Found {len(apps)} installed applications")
    
    for app in apps[:5]:  # Show first 5 apps
        print(f"Name: {app.name}")
        print(f"Start Command: {app.start_cmd}")
        print(f"Stop Command: {app.stop_cmd if app.stop_cmd else 'N/A'}")
        print(f"Work Directory: {app.work_directory if app.work_directory else 'N/A'}")
        print("---")
```

**Parameters:**
- `start_menu` (bool): Include applications from Start Menu
- `desktop` (bool): Include desktop shortcuts
- `ignore_system_apps` (bool): Filter out system applications

### Starting Applications

#### Method 1: Start by Command

```python
result = session.computer.start_app(start_cmd)

if result.success:
    processes = result.data
    print(f"Application started with {len(processes)} processes")
    
    for process in processes:
        print(f"Process: {process.pname} (PID: {process.pid})")
```

#### Method 2: Start with Working Directory

```python
start_cmd = "notepad.exe"
work_directory = "C:\\Users\\Public\\Documents"

result = session.computer.start_app(
    start_cmd=start_cmd,
    work_directory=work_directory
)

if result.success:
    print("Application started with custom working directory")
```

#### Method 3: Start from Installed Apps List

```python
# Find and start a specific application
apps_result = session.computer.get_installed_apps()

if apps_result.success:
    target_app = None
    for app in apps_result.data:
        if "Google Chrome" in app.name.lower():
            target_app = app
            break
    
    if target_app:
        print(f"Starting {target_app.name}...")
        start_result = session.computer.start_app(target_app.start_cmd)
        
        if start_result.success:
            print("Application started successfully!")
```

### Monitoring Running Applications

```python
result = session.computer.list_visible_apps()

if result.success:
    visible_apps = result.data
    print(f"Found {len(visible_apps)} visible applications")
    
    for app in visible_apps:
        print(f"App: {app.pname} (PID: {app.pid})")
        if app.cmdline:
            print(f"Command: {app.cmdline}")
        print("---")
```

### Stopping Applications

#### Method 1: Stop by Process Name

```python
result = session.computer.stop_app_by_pname("notepad.exe")

if result.success:
    print("Application stopped successfully")
else:
    print(f"Failed to stop application: {result.error_message}")
```

#### Method 2: Stop by Process ID

```python
# Get PID from start_app or list_visible_apps
start_result = session.computer.start_app(start_cmd)

if start_result.success:
    target_pid = start_result.data[0].pid  # Get first process PID
    
    stop_result = session.computer.stop_app_by_pid(target_pid)
    if stop_result.success:
        print(f"Successfully stopped process {target_pid}")
```

#### Method 3: Stop by Command

```python
# Using stop command from installed apps
apps_result = session.computer.get_installed_apps()

if apps_result.success:
    for app in apps_result.data:
        if app.stop_cmd and "Google Chrome" in app.name.lower():
            stop_result = session.computer.stop_app_by_cmd(app.stop_cmd)
            if stop_result.success:
                print(f"Stopped {app.name} using stop command")
            break
```

## Window Management (20 minutes)

**Important:** Window management operations require that applications are already running. You must start an application first before you can manage its windows.

### Discovering Windows

```python
# First, start an application to have windows to manage
start_result = session.computer.start_app(start_cmd)
if not start_result.success:
    print("Failed to start application")
    exit(1)

# Wait a moment for the application to fully load
import time
time.sleep(2)

# List all root windows
result = session.computer.list_root_windows(timeout_ms=5000)

if result.success:
    windows = result.windows
    print(f"Found {len(windows)} windows")
    
    for window in windows:
        print(f"Title: {window.title}")
        print(f"Window ID: {window.window_id}")
        print(f"Process: {window.pname if window.pname else 'N/A'}")
        print(f"PID: {window.pid if window.pid else 'N/A'}")
        print("---")
```

### Getting Active Window

```python
result = session.computer.get_active_window()

if result.success and result.window:
    window = result.window
    print(f"Active window: {window.title}")
    print(f"Window ID: {window.window_id}")
    print(f"Size: {window.width}x{window.height}")
else:
    print("No active window found")
```

### Window Control Operations

#### Activate Window

```python
# Get available windows
windows_result = session.computer.list_root_windows()

if windows_result.success and windows_result.windows:
    window_id = windows_result.windows[0].window_id
    
    result = session.computer.activate_window(window_id)
    if result.success:
        print("Window activated successfully")
```

#### Maximize Window

```python
windows_result = session.computer.list_root_windows()

if windows_result.success and windows_result.windows:
    window_id = windows_result.windows[0].window_id
    
    result = session.computer.maximize_window(window_id)
    if result.success:
        print("Window maximized successfully")
```

#### Minimize Window

```python
windows_result = session.computer.list_root_windows()

if windows_result.success and windows_result.windows:
    window_id = windows_result.windows[0].window_id
    
    result = session.computer.minimize_window(window_id)
    if result.success:
        print("Window minimized successfully")
```

#### Restore Window

```python
windows_result = session.computer.list_root_windows()

if windows_result.success and windows_result.windows:
    window_id = windows_result.windows[0].window_id
    
    result = session.computer.restore_window(window_id)
    if result.success:
        print("Window restored successfully")
```

#### Resize Window

```python
windows_result = session.computer.list_root_windows()

if windows_result.success and windows_result.windows:
    window_id = windows_result.windows[0].window_id
    
    result = session.computer.resize_window(window_id, 800, 600)
    if result.success:
        print("Window resized to 800x600")
```

#### Fullscreen Window

```python
windows_result = session.computer.list_root_windows()

if windows_result.success and windows_result.windows:
    window_id = windows_result.windows[0].window_id
    
    result = session.computer.fullscreen_window(window_id)
    if result.success:
        print("Window set to fullscreen")
```

#### Close Window

```python
# Note: Use with caution as it permanently closes windows
windows_result = session.computer.list_root_windows()

if windows_result.success and windows_result.windows:
    window_id = windows_result.windows[0].window_id
    
    result = session.computer.close_window(window_id)
    if result.success:
        print("Window closed successfully")
```

#### Focus Mode

```python
# Enable focus mode to reduce distractions
result = session.computer.focus_mode(on=True)
if result.success:
    print("Focus mode enabled")

# Disable focus mode
result = session.computer.focus_mode(on=False)
if result.success:
    print("Focus mode disabled")
```

### Complete Window Management Workflow

```python
import time

def manage_application_window(session, app_name: str):
    """Complete workflow for managing an application window"""
    
    # Step 1: Start the application
    print(f"Starting {app_name}...")
    start_result = session.computer.start_app(app_name)
    if not start_result.success:
        print(f"Failed to start {app_name}")
        return False
    
    # Step 2: Wait for application to load
    time.sleep(3)
    
    # Step 3: Find the application window
    windows_result = session.computer.list_root_windows()
    if not windows_result.success:
        print("Failed to list windows")
        return False
    
    target_window = None
    for window in windows_result.windows:
        if app_name.lower().replace('.exe', '') in window.title.lower():
            target_window = window
            break
    
    if not target_window:
        print(f"Window for {app_name} not found")
        return False
    
    print(f"Found window: {target_window.title}")
    
    # Step 4: Perform window operations
    window_id = target_window.window_id
    
    # Activate the window
    session.computer.activate_window(window_id)
    print("Window activated")
    time.sleep(1)
    
    # Maximize the window
    session.computer.maximize_window(window_id)
    print("Window maximized")
    time.sleep(1)
    
    # Resize the window
    session.computer.resize_window(window_id, 1024, 768)
    print("Window resized")
    time.sleep(1)
    
    # Restore the window
    session.computer.restore_window(window_id)
    print("Window restored")
    
    return True

# Usage example - Get app from installed apps list
apps_result = session.computer.get_installed_apps()
if apps_result.success and apps_result.data:
    # Find a suitable app (e.g., notepad or text editor)
    target_app = None
    for app in apps_result.data:
        if "Google Chrome" in app.name.lower() :
            target_app = app
            break
    
    if target_app:
        success = manage_application_window(session, target_app.start_cmd)
        if success:
            print("Window management completed successfully")
    else:
        print("No suitable application found in installed apps")
else:
    print("Failed to get installed applications")
```

## Advanced Usage (20 minutes)

### Automated Desktop Workflows

```python
def automated_text_editing_workflow(session):
    """Automated workflow for text editing"""
    
    # Get installed apps and find a text editor
    apps_result = session.computer.get_installed_apps()
    if not apps_result.success:
        print("Failed to get installed applications")
        return False
    
    # Find a suitable text editor
    first_app = None
    for app in apps_result.data:
        if "Google Chrome" in app.name.lower():
            first_app = app
            break
    
    if not first_app:
        print("No suitable text editor found in installed apps")
        return False
    
    # Start text editor using the proper start command
    start_result = session.computer.start_app(first_app.start_cmd)
    if not start_result.success:
        print(f"Failed to start {first_app.name}")
        return False
    
    time.sleep(2)
    
    # Find and activate the window
    windows_result = session.computer.list_root_windows()
    first_app_window = None
    
    for window in windows_result.windows:
        if "Google Chrome" in window.title.lower():
            first_app_window = window
            break
    
    if first_app_window:
        # Check if window has valid window_id before performing operations
        if hasattr(first_app_window, 'window_id') and first_app_window.window_id:
            session.computer.activate_window(first_app_window.window_id)
            session.computer.maximize_window(first_app_window.window_id)
        else:
            print(f"Warning: Found window '{first_app_window.title}' but it has no valid window_id")
    
    # Type some text
    text_content = """Hello from AGB Computer Automation!

This text was automatically typed using the AGB SDK.

Features demonstrated:
1. Application launching
2. Window management
3. Text input
4. Keyboard shortcuts
"""
    
    session.computer.input_text(text_content)
    time.sleep(1)
    
    # Select all text
    session.computer.press_keys(["Ctrl", "a"])
    time.sleep(0.5)
    
    # Copy text
    session.computer.press_keys(["Ctrl", "c"])
    time.sleep(0.5)
    
    # Move to end and paste
    session.computer.press_keys(["Ctrl", "End"])
    session.computer.press_keys(["Enter", "Enter"])
    session.computer.input_text("Copied content:")
    session.computer.press_keys(["Enter"])
    session.computer.press_keys(["Ctrl", "v"])
    
    print("Automated text editing workflow completed")
    return True

# Run the workflow
automated_text_editing_workflow(session)
```
## Best Practices

### 1. Session Management

```python
# ✅ Good: Always clean up sessions
def safe_automation_task():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-linux-test-5")
    result = agb.create(params)
    
    if not result.success:
        print(f"Failed to create session: {result.error_message}")
        return False
    
    session = result.session
    
    try:
        # Perform automation tasks
        result = session.computer.click_mouse(100, 100)
        return result.success
    
    finally:
        # Always delete session
        agb.delete(session)
        print("Session cleaned up")

# Usage
success = safe_automation_task()
```

### 2. Error Handling and Retry Logic

```python
def robust_operation(session, operation_func, max_retries=3):
    """Perform operation with retry logic"""
    
    for attempt in range(max_retries):
        try:
            result = operation_func()
            if result.success:
                return result
            else:
                print(f"Attempt {attempt + 1} failed: {result.error_message}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
        except Exception as e:
            print(f"Attempt {attempt + 1} exception: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    return None

# Usage example
def click_operation():
    return session.computer.click_mouse(500, 300)

result = robust_operation(session, click_operation)
if result:
    print("Operation succeeded")
else:
    print("Operation failed after all retries")
```

### 3. Coordinate Validation

```python
def safe_click(session, x, y, button=MouseButton.LEFT):
    """Safely click with coordinate validation"""
    
    # Get screen size first
    screen_result = session.computer.get_screen_size()
    if not screen_result.success:
        print("Failed to get screen size")
        return False
    
    import json
    screen_data = json.loads(screen_result.data)
    max_x = screen_data['width']
    max_y = screen_data['height']
    
    # Validate coordinates
    if x < 0 or x >= max_x or y < 0 or y >= max_y:
        print(f"Invalid coordinates: ({x}, {y}). Screen size: {max_x}x{max_y}")
        return False
    
    # Perform click
    result = session.computer.click_mouse(x, y, button)
    return result.success

# Usage
success = safe_click(session, 500, 300)
```

### 4. Application State Management

```python
def ensure_application_ready(session, app_name, window_title_contains, timeout=30):
    """Ensure application is started and ready"""
    
    import time
    start_time = time.time()
    
    # Start application
    start_result = session.computer.start_app(app_name)
    if not start_result.success:
        return None
    
    # Wait for window to appear
    while time.time() - start_time < timeout:
        windows_result = session.computer.list_root_windows()
        if windows_result.success:
            for window in windows_result.windows:
                if hasattr(window, 'window_id') and window.window_id:
                    session.computer.activate_window(window.window_id)
                    return window
                else:
                    print(f"Warning: Found matching window '{window.title}' but it has no valid window_id")
                    continue
        
        time.sleep(1)
    
    print(f"Timeout waiting for {app_name} window")
    return None

# Usage
notepad_window = ensure_application_ready(session, "notepad.exe", "notepad")
if notepad_window:
    print(f"Notepad ready: {notepad_window.title}")
```

## Troubleshooting

### Common Issues

**Coordinate Issues**
```python
# Check screen size before clicking
screen_result = session.computer.get_screen_size()
if screen_result.success:
    import json
    screen_data = json.loads(screen_result.data)
    print(f"Screen dimensions: {screen_data['width']}x{screen_data['height']}")
    print(f"DPI scaling: {screen_data['dpiScalingFactor']}")
```

**Application Not Starting**
```python
# Check installed applications
apps_result = session.computer.get_installed_apps()
if apps_result.success:
    app_names = [app.name for app in apps_result.data]
    print("Available applications:", app_names)
    
    # Check if target app exists
    target_app = "notepad.exe"
    matching_apps = [app for app in apps_result.data if target_app.lower() in app.name.lower()]
    if matching_apps:
        print(f"Found matching apps: {[app.name for app in matching_apps]}")
    else:
        print(f"No apps found matching '{target_app}'")
```

**Window Not Found**
```python
# Debug window discovery
def debug_windows(session):
    result = session.computer.list_root_windows()
    if result.success:
        print(f"Found {len(result.windows)} windows:")
        for i, window in enumerate(result.windows):
            print(f"  {i+1}. Title: '{window.title}'")
            print(f"     ID: {window.window_id}")
            print(f"     Process: {window.pname}")
            print()
    else:
        print(f"Failed to list windows: {result.error_message}")

debug_windows(session)
```

**Timing Issues**
```python
import time

# Add delays between operations
session.computer.start_app(start_cmd)
time.sleep(3)  # Wait for app to start

session.computer.click_mouse(500, 300)
time.sleep(0.5)  # Wait for click to register

session.computer.input_text("Hello")
time.sleep(1)  # Wait for text input
```

**Session Health Check**
```python
def check_session_health(session):
    """Check if session is healthy"""
    try:
        # Try a simple operation
        result = session.computer.get_screen_size()
        if result.success:
            print("Session is healthy")
            return True
        else:
            print(f"Session issue: {result.error_message}")
            return False
    except Exception as e:
        print(f"Session error: {e}")
        return False

# Usage
if not check_session_health(session):
    print("Session needs to be recreated")
```

## Related Documentation

- **[Session Management Guide](session-management.md)** - Managing automation sessions
- **[API Reference](../api-reference/02_session.md)** - Complete computer automation API
