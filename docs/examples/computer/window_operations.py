#!/usr/bin/env python3
"""
Window Operations Example

This example demonstrates comprehensive window management operations:
- Listing and discovering windows
- Window activation and focus management
- Window state changes (minimize, maximize, restore)
- Window resizing and positioning
- Fullscreen operations
- Window closing and cleanup
"""

import os
import time
import requests
from agb import AGB
from agb.session_params import CreateSessionParams


def save_screenshot_to_file(screenshot_url, filename):
    """Download and save screenshot from URL to local PNG file."""
    try:
        print(f"    💾 Downloading screenshot to {filename}...")
        response = requests.get(screenshot_url, timeout=30)
        response.raise_for_status()

        # Create screenshots directory if it doesn't exist
        os.makedirs("screenshots", exist_ok=True)
        filepath = os.path.join("screenshots", filename)

        with open(filepath, "wb") as f:
            f.write(response.content)

        print(f"    ✅ Screenshot saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"    ❌ Failed to save screenshot: {e}")
        return None


def take_and_save_screenshot(session, description="screenshot", filename=None):
    """Take a screenshot and save it to local PNG file.

    Args:
        session: AGB session object
        description: Description of the screenshot for logging
        filename: Optional custom filename, if not provided, will generate based on description

    Returns:
        tuple: (screenshot_url, local_filepath) or (None, None) if failed
    """
    print(f"  📸 Taking {description}...")

    try:
        # Take screenshot
        screenshot_result = session.computer.screenshot()
        if screenshot_result.success and screenshot_result.data:
            screenshot_url = screenshot_result.data
            print(f"  ✅ Screenshot captured: {screenshot_url}")

            # Generate filename if not provided
            if filename is None:
                # Replace spaces and special characters with underscores
                safe_description = (
                    description.replace(" ", "_").replace("/", "_").replace("\\", "_")
                )
                filename = f"{safe_description}.png"

            # Save screenshot to local PNG file
            local_path = save_screenshot_to_file(screenshot_url, filename)
            if local_path:
                print(f"  📁 Screenshot saved as PNG: {local_path}")
                return screenshot_url, local_path
            else:
                print("  ⚠️  Failed to save screenshot to local file")
                return screenshot_url, None
        else:
            print(f"  ❌ Screenshot failed: {screenshot_result.error_message}")
            return None, None

    except Exception as e:
        print(f"  ❌ Screenshot exception: {str(e)}")
        return None, None


def main():
    """Main function demonstrating window operations."""

    # Get API key from environment
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        raise ValueError("AGB_API_KEY environment variable not set")

    print("🪟 Starting window operations example...")

    # Initialize AGB client
    agb = AGB(api_key=api_key)
    session = None

    try:
        # Create a session with computer support
        print("📦 Creating computer session...")
        params = CreateSessionParams(image_id="agb-computer-use-ubuntu-2204")
        result = agb.create(params)

        if not result.success:
            raise RuntimeError(f"Failed to create session: {result.error_message}")

        session = result.session
        print(f"✅ Session created: {session.session_id}")

        # Wait for session to be ready
        time.sleep(3)

        # Example 1: Application Management and Window Discovery
        print("\n🚀 Example 1: Application Management and Window Discovery")

        # Get installed apps
        print("  Getting installed applications...")
        installed_apps_result = session.computer.get_installed_apps()
        if installed_apps_result.success and len(installed_apps_result.data) > 0:
            print(
                f"  ✅ Found {len(installed_apps_result.data)} installed applications"
            )

            # Find a suitable app to work with (prefer Google Chrome, fallback to first app)
            target_app = None
            for app in installed_apps_result.data:
                if hasattr(app, "name") and app.name == "Calculator":
                    target_app = app
                    print(f"  🎯 Selected Google Chrome for demonstration")
                    break

            if target_app is None:
                target_app = installed_apps_result.data[0]
                app_name = getattr(target_app, "name", "Unknown App")
                print(f"  🎯 Selected {app_name} for demonstration")

            start_cmd = target_app.start_cmd
            app_name = getattr(target_app, "name", "Unknown App")

            # Start the application
            print(f"  Starting {app_name}...")
            start_result = session.computer.start_app(start_cmd)
            if start_result.success and len(start_result.data) > 0:
                print(f"  ✅ Application started successfully")

                # Get process information for cleanup
                first_process = start_result.data[0]
                app_pname = getattr(first_process, "pname", None)

                # Wait for app to fully start
                time.sleep(3)

                # Example 2: Window Listing and Selection
                print("\n📋 Example 2: Window Listing and Selection")

                # List all root windows
                print("  Listing all root windows...")
                windows_result = session.computer.list_root_windows()
                if windows_result.success and len(windows_result.windows) > 0:
                    print(f"  ✅ Found {len(windows_result.windows)} windows")

                    # Display window information
                    for i, window in enumerate(windows_result.windows):
                        print(
                            f"    Window {i+1}: ID={window.window_id}, Title='{window.title}'"
                        )

                    # Select the first window for operations
                    target_window = windows_result.windows[0]
                    window_id = target_window.window_id
                    window_title = target_window.title
                    print(
                        f"  🎯 Selected window: ID={window_id}, Title='{window_title}'"
                    )

                    # Example 3: Window Activation and Focus
                    print("\n🎯 Example 3: Window Activation and Focus")

                    # Activate the selected window
                    print("  Activating selected window...")
                    activate_result = session.computer.activate_window(window_id)
                    if activate_result.success and activate_result.data:
                        print("  ✅ Window activated successfully")

                        # Verify window is active
                        active_window_result = session.computer.get_active_window()
                        if active_window_result.success and active_window_result.window:
                            active_id = active_window_result.window.window_id
                            if str(active_id) == str(window_id):
                                print("  ✅ Window activation verified")
                            else:
                                print(
                                    f"  ⚠️  Active window mismatch: expected {window_id}, got {active_id}"
                                )
                        else:
                            print("  ⚠️  Could not verify active window")
                    else:
                        print(
                            f"  ❌ Window activation failed: {activate_result.error_message}"
                        )

                    time.sleep(2)

                    # Enable focus mode for better control
                    print("  Enabling focus mode...")
                    focus_result = session.computer.focus_mode(True)
                    if focus_result.success and focus_result.data:
                        print("  ✅ Focus mode enabled")
                    else:
                        print(f"  ⚠️  Focus mode failed: {focus_result.error_message}")

                    # Example 4: Window State Management
                    print("\n📐 Example 4: Window State Management")

                    # Minimize window
                    print("  Minimizing window...")
                    minimize_result = session.computer.minimize_window(window_id)
                    if minimize_result.success and minimize_result.data:
                        print("  ✅ Window minimized successfully")
                        time.sleep(2)
                    else:
                        print(
                            f"  ❌ Window minimize failed: {minimize_result.error_message}"
                        )

                    # Take screenshot after minimizing
                    screenshot_url, local_path = take_and_save_screenshot(
                        session,
                        "window minimization",
                        "window_minimized_screenshot.png",
                    )

                    # Maximize window
                    print("  Maximizing window...")
                    maximize_result = session.computer.maximize_window(window_id)
                    if maximize_result.success and maximize_result.data:
                        print("  ✅ Window maximized successfully")
                        time.sleep(2)
                    else:
                        print(
                            f"  ❌ Window maximize failed: {maximize_result.error_message}"
                        )

                    # Take screenshot after maximizing
                    take_and_save_screenshot(
                        session,
                        "window maximization",
                        "window_maximized_screenshot.png",
                    )
                    # Restore window to normal state
                    print("  Restoring window to normal state...")
                    restore_result = session.computer.restore_window(window_id)
                    if restore_result.success and restore_result.data:
                        print("  ✅ Window restored successfully")
                        time.sleep(3)
                    else:
                        print(
                            f"  ❌ Window restore failed: {restore_result.error_message}"
                        )

                    # Take screenshot after restore
                    take_and_save_screenshot(
                        session, "window restore", "window_restore_screenshot.png"
                    )
                    # Example 5: Window Resizing
                    print("\n📏 Example 5: Window Resizing")

                    # Resize window to specific dimensions
                    new_width, new_height = 800, 600
                    print(f"  Resizing window to {new_width}x{new_height}...")
                    resize_result = session.computer.resize_window(
                        window_id, new_width, new_height
                    )
                    if resize_result.success and resize_result.data:
                        print(
                            f"  ✅ Window resized to {new_width}x{new_height} successfully"
                        )
                        time.sleep(2)
                    else:
                        print(
                            f"  ❌ Window resize failed: {resize_result.error_message}"
                        )
                    # Take screenshot after resize
                    take_and_save_screenshot(
                        session, "window resize", "window_resize_screenshot.png"
                    )
                    # Example 6: Fullscreen Operations
                    print("\n🖥️  Example 6: Fullscreen Operations")

                    # Set window to fullscreen
                    print("  Setting window to fullscreen...")
                    fullscreen_result = session.computer.fullscreen_window(window_id)
                    if fullscreen_result.success and fullscreen_result.data:
                        print("  ✅ Window set to fullscreen successfully")
                        time.sleep(3)  # Let user see fullscreen effect
                    else:
                        print(
                            f"  ❌ Fullscreen failed: {fullscreen_result.error_message}"
                        )

                    time.sleep(2)

                    # Example 7: Window Information and Validation
                    print("\n📊 Example 7: Window Information and Validation")

                    # Get current cursor position
                    cursor_result = session.computer.get_cursor_position()
                    if cursor_result.success:
                        print("  ✅ Cursor position retrieved successfully")
                    else:
                        print(
                            f"  ⚠️  Cursor position retrieval failed: {cursor_result.error_message}"
                        )

                    # Verify window still exists
                    final_windows_result = session.computer.list_root_windows()
                    if final_windows_result.success:
                        window_exists = False
                        for window in final_windows_result.windows:
                            if window.window_id == window_id:
                                window_exists = True
                                break

                        if window_exists:
                            print("  ✅ Target window still exists")
                        else:
                            print("  ⚠️  Target window no longer exists")

                    # Example 8: Window Cleanup
                    print("\n🧹 Example 8: Window Cleanup")

                    # Close the window
                    print("  Closing window...")
                    close_result = session.computer.close_window(window_id)
                    if close_result.success and close_result.data:
                        print("  ✅ Window closed successfully")
                        time.sleep(2)

                        # Verify window is closed
                        verification_result = session.computer.list_root_windows()
                        if verification_result.success:
                            window_still_exists = False
                            for window in verification_result.windows:
                                if window.window_id == window_id:
                                    window_still_exists = True
                                    break

                            if not window_still_exists:
                                print("  ✅ Window closure verified")
                            else:
                                print("  ⚠️  Window still exists after close")
                        else:
                            print("  ⚠️  Could not verify window closure")
                    else:
                        print(f"  ❌ Window close failed: {close_result.error_message}")
            else:
                print(f"  ❌ Failed to start application: {start_result.error_message}")
        else:
            print("  ❌ No installed applications found")

        print("\n📊 Window Operations Summary:")
        print("  • Application discovery and launching")
        print("  • Window listing and identification")
        print("  • Window activation and focus management")
        print("  • Window state changes (minimize, maximize, restore)")
        print("  • Window resizing to various dimensions")
        print("  • Fullscreen mode operations")
        print("  • Window information retrieval")
        print("  • Window cleanup and closure")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        raise

    finally:
        # Clean up session
        if session:
            agb.delete(session)
            print("🧹 Session cleaned up")

    print("🎉 Window operations example completed successfully!")


if __name__ == "__main__":
    main()
