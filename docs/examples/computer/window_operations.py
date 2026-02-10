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
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from agb import AGB
from agb.session_params import CreateSessionParams


def save_screenshot_to_file(screenshot_url, filename):
    """Download and save screenshot from URL to local PNG file with retry mechanism."""
    try:
        print(f"    💾 Downloading screenshot to {filename}...")

        # Configure retry strategy for OSS downloads
        # Retry on connection errors, SSL errors, and server errors
        retry_strategy = Retry(
            total=3,  # Maximum number of retries
            backoff_factor=2,  # Exponential backoff: 2, 4, 8 seconds
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
            allowed_methods=["GET"],  # Only retry GET requests
            # Retry on connection errors and SSL errors
            connect=3,
            read=3,
            redirect=3,
        )

        # Create session with retry adapter
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        # Download timeout: 60 seconds (large images may take longer)
        download_timeout = 60

        response = session.get(screenshot_url, timeout=download_timeout, verify=True)
        response.raise_for_status()

        # Create screenshots directory if it doesn't exist
        os.makedirs("screenshots", exist_ok=True)
        filepath = os.path.join("screenshots", filename)

        with open(filepath, "wb") as f:
            f.write(response.content)

        print(f"    ✅ Screenshot saved to: {filepath}")
        return filepath
    except requests.exceptions.SSLError as e:
        print(f"    ❌ SSL error while downloading screenshot: {e}")
        print(f"    💡 This may be due to network issues or OSS server connection problems.")
        print(f"    💡 Try running the script again, or check your network connection.")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"    ❌ Connection error while downloading screenshot: {e}")
        print(f"    💡 This may be due to network issues or the OSS URL may have expired.")
        print(f"    💡 Try running the script again.")
        return None
    except requests.exceptions.Timeout as e:
        print(f"    ❌ Timeout while downloading screenshot: {e}")
        print(f"    💡 The download took too long. Try running the script again.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"    ❌ HTTP error while downloading screenshot: {e}")
        print(f"    💡 HTTP status: {e.response.status_code if e.response else 'Unknown'}")
        return None
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
        try:
            screenshot_result = session.computer.screen.capture()
            if not screenshot_result.success or not screenshot_result.data:
                print(f"  ⚠️  Screenshot failed: {screenshot_result.error_message}")
                return None, None

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
        except Exception as e:
            print(f"  ❌ Screenshot failed: {e}")
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
        try:
            apps_result = session.computer.app.list_installed()
            if not apps_result.success or not apps_result.data:
                print(f"  ❌ Failed to get installed apps: {apps_result.error_message}")
            elif apps_result.data:
                apps = apps_result.data
                print(f"  ✅ Found {len(apps)} installed applications")

                # Find a suitable app to work with (prefer Calculator, fallback to first app)
                target_app = None
                for app in apps:
                    if hasattr(app, "name") and app.name == "Calculator":
                        target_app = app
                        print(f"  🎯 Selected Calculator for demonstration")
                        break

                if target_app is None:
                    target_app = apps[0]
                    app_name = getattr(target_app, "name", "Unknown App")
                    print(f"  🎯 Selected {app_name} for demonstration")

                start_cmd = target_app.start_cmd
                app_name = getattr(target_app, "name", "Unknown App")

                # Start the application
                print(f"  Starting {app_name}...")
                try:
                    start_result = session.computer.app.start(start_cmd)
                    if not start_result.success or not start_result.data:
                        print(f"  ❌ Failed to start application: {start_result.error_message}")
                    elif start_result.data:
                        processes = start_result.data
                        print(f"  ✅ Application started successfully")

                        # Get process information for cleanup
                        first_process = processes[0]
                        app_pname = getattr(first_process, "pname", None)

                        # Wait for app to fully start
                        time.sleep(3)

                        # Example 2: Window Listing and Selection
                        print("\n📋 Example 2: Window Listing and Selection")

                        # List all root windows
                        print("  Listing all root windows...")
                        try:
                            windows_result = session.computer.window.list_root_windows()
                            if not windows_result.success or not windows_result.windows:
                                print(f"  ❌ Failed to list windows: {windows_result.error_message}")
                            elif windows_result.windows:
                                windows = windows_result.windows
                                print(f"  ✅ Found {len(windows)} windows")

                                # Display window information
                                for i, window in enumerate(windows):
                                    print(
                                        f"    Window {i+1}: ID={window.window_id}, Title='{window.title}'"
                                    )

                                # Select the first window for operations
                                target_window = windows[0]
                                window_id = target_window.window_id
                                window_title = target_window.title
                                print(
                                    f"  🎯 Selected window: ID={window_id}, Title='{window_title}'"
                                )

                                # Example 3: Window Activation and Focus
                                print("\n🎯 Example 3: Window Activation and Focus")

                                # Activate the selected window
                                print("  Activating selected window...")
                                activate_result = session.computer.window.activate(window_id)
                                if activate_result.success:
                                    print("  ✅ Window activated successfully")

                                    # Verify window is active
                                    try:
                                        active_window_result = session.computer.window.get_active_window()
                                        if not active_window_result.success:
                                            print(f"  ⚠️  Could not get active window: {active_window_result.error_message}")
                                        elif active_window_result.window:
                                            active_window = active_window_result.window
                                            active_id = active_window.window_id
                                            if str(active_id) == str(window_id):
                                                print("  ✅ Window activation verified")
                                            else:
                                                print(
                                                    f"  ⚠️  Active window mismatch: expected {window_id}, got {active_id}"
                                                )
                                        else:
                                            print("  ⚠️  Could not verify active window: no active window returned")
                                    except Exception as e:
                                        print(f"  ⚠️  Could not verify active window: {e}")
                                else:
                                    print(
                                        f"  ❌ Window activation failed: {activate_result.error_message}"
                                    )

                                time.sleep(2)

                                # Enable focus mode for better control
                                print("  Enabling focus mode...")
                                focus_result = session.computer.window.focus_mode(True)
                                if focus_result.success:
                                    print("  ✅ Focus mode enabled")
                                else:
                                    print(f"  ⚠️  Focus mode failed: {focus_result.error_message}")

                                # Example 4: Window State Management
                                print("\n📐 Example 4: Window State Management")

                                # Minimize window
                                print("  Minimizing window...")
                                minimize_result = session.computer.window.minimize(window_id)
                                if minimize_result.success:
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
                                maximize_result = session.computer.window.maximize(window_id)
                                if maximize_result.success:
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
                                restore_result = session.computer.window.restore(window_id)
                                if restore_result.success:
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
                                resize_result = session.computer.window.resize(
                                    window_id, new_width, new_height
                                )
                                if resize_result.success:
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
                                fullscreen_result = session.computer.window.fullscreen(window_id)
                                if fullscreen_result.success:
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
                                try:
                                    position_result = session.computer.mouse.get_position()
                                    if position_result.success and position_result.data:
                                        if isinstance(position_result.data, dict):
                                            x = position_result.data.get('x', 0)
                                            y = position_result.data.get('y', 0)
                                        else:
                                            x, y = 0, 0
                                        print(f"  ✅ Cursor position: x={x}, y={y}")
                                    else:
                                        print(f"  ⚠️  Cursor position retrieval failed: {position_result.error_message}")
                                except Exception as e:
                                    print(f"  ⚠️  Cursor position retrieval failed: {e}")

                                # Verify window still exists
                                try:
                                    final_windows_result = session.computer.window.list_root_windows()
                                    if final_windows_result.success and final_windows_result.windows:
                                        final_windows = final_windows_result.windows
                                        window_exists = False
                                        for window in final_windows:
                                            if window.window_id == window_id:
                                                window_exists = True
                                                break

                                        if window_exists:
                                            print("  ✅ Target window still exists")
                                        else:
                                            print("  ⚠️  Target window no longer exists")
                                    else:
                                        print(f"  ⚠️  Failed to list windows: {final_windows_result.error_message}")
                                except Exception as e:
                                    print(f"  ⚠️  Failed to list windows: {e}")

                                # Example 8: Window Cleanup
                                print("\n🧹 Example 8: Window Cleanup")

                                # Close the window
                                print("  Closing window...")
                                close_result = session.computer.window.close(window_id)
                                if close_result.success:
                                    print("  ✅ Window closed successfully")
                                    time.sleep(2)

                                    # Verify window is closed
                                    try:
                                        verification_windows_result = session.computer.window.list_root_windows()
                                        if verification_windows_result.success and verification_windows_result.windows:
                                            verification_windows = verification_windows_result.windows
                                            window_still_exists = False
                                            for window in verification_windows:
                                                if window.window_id == window_id:
                                                    window_still_exists = True
                                                    break

                                            if not window_still_exists:
                                                print("  ✅ Window closure verified")
                                            else:
                                                print("  ⚠️  Window still exists after close")
                                        else:
                                            print(f"  ⚠️  Could not verify window closure: {verification_windows_result.error_message}")
                                    except Exception as e:
                                        print(f"  ⚠️  Could not verify window closure: {e}")
                                else:
                                    print(f"  ❌ Window close failed: {close_result.error_message}")
                            else:
                                print(f"  ⚠️  Failed to list windows or no windows found")
                        except Exception as e:
                            print(f"  ❌ Failed to list windows: {e}")
                    else:
                        print(f"  ❌ Failed to start application: no processes returned")
                except Exception as e:
                    print(f"  ❌ Failed to start application: {e}")
        except Exception as e:
            print(f"  ❌ Failed to get installed apps: {e}")

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
