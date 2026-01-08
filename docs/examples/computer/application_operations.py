#!/usr/bin/env python3
"""
Application Operations Example

This example demonstrates comprehensive application management operations:
- Discovering and listing installed applications
- Starting applications with different methods
- Monitoring running applications and processes
- Stopping applications by different identifiers
- Application lifecycle management
- Process validation and verification
"""

import os
import time
from agb import AGB
from agb.session_params import CreateSessionParams


def main():
    """Main function demonstrating application operations."""

    # Get API key from environment
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        raise ValueError("AGB_API_KEY environment variable not set")

    print("🚀 Starting application operations example...")

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

        # Example 1: Application Discovery
        print("\n🔍 Example 1: Application Discovery")

        # Get list of installed applications
        print("  Discovering installed applications...")
        installed_apps_result = session.computer.get_installed_apps()
        if installed_apps_result.success:
            apps = installed_apps_result.data
            print(f"  ✅ Found {len(apps)} installed applications")

            # Display information about available applications
            print("  📋 Available applications:")
            for i, app in enumerate(apps[:10]):  # Show first 10 apps
                app_name = getattr(app, "name", "Unknown")
                start_cmd = getattr(app, "start_cmd", "N/A")
                print(f"    {i+1}. {app_name} (Command: {start_cmd})")

            if len(apps) > 10:
                print(f"    ... and {len(apps) - 10} more applications")

            # Select Google Chrome for demonstration
            chrome_app = None

            # Find Google Chrome application
            for app in apps:
                if hasattr(app, "name") and app.name == "Google Chrome":
                    chrome_app = app
                    print(f"  🎯 Selected Google Chrome for demonstration")
                    break

            if not chrome_app:
                print("  ⚠️  Google Chrome not found in installed applications")
                return

            print(f"  🎯 Selected Google Chrome application for demonstration")

        else:
            print(
                f"  ❌ Failed to get installed apps: {installed_apps_result.error_message}"
            )
            return

        # Example 2: Application Starting
        print("\n🚀 Example 2: Application Starting")

        started_processes = []

        # Start Google Chrome application
        app_name = getattr(chrome_app, "name", "Google Chrome")
        start_cmd = chrome_app.start_cmd

        print(f"  Starting {app_name}...")
        print(f"    Command: {start_cmd}")

        start_result = session.computer.start_app(start_cmd)
        if start_result.success and len(start_result.data) > 0:
            print(f"    ✅ {app_name} started successfully")

            # Store process information for later operations
            for process in start_result.data:
                process_info = {
                    "app_name": app_name,
                    "pid": getattr(process, "pid", None),
                    "pname": getattr(process, "pname", None),
                    "cmdline": getattr(process, "cmdline", None),
                }
                started_processes.append(process_info)
                print(
                    f"      Process: PID={process_info['pid']}, Name={process_info['pname']}"
                )
        else:
            print(f"    ❌ Failed to start {app_name}: {start_result.error_message}")

        time.sleep(2)  # Wait for app to start

        print(f"  📊 Started {len(started_processes)} processes total")

        # Example 3: Running Application Discovery
        print("\n👀 Example 3: Running Application Discovery")

        # List currently visible/running applications
        print("  Listing visible applications...")
        visible_apps_result = session.computer.list_visible_apps()
        if visible_apps_result.success:
            visible_apps = visible_apps_result.data
            print(f"  ✅ Found {len(visible_apps)} visible applications")

            # Display visible applications
            print("  📋 Currently visible applications:")
            for i, process in enumerate(visible_apps[:15]):  # Show first 15
                pid = getattr(process, "pid", "N/A")
                pname = getattr(process, "pname", "Unknown")
                print(f"    {i+1}. PID: {pid}, Process: {pname}")

            if len(visible_apps) > 15:
                print(f"    ... and {len(visible_apps) - 15} more processes")

            # Verify our started processes are visible
            print("  🔍 Verifying started processes are visible...")
            for started_proc in started_processes:
                found = False
                for visible_proc in visible_apps:
                    if getattr(visible_proc, "pid", None) == started_proc["pid"]:
                        found = True
                        break

                if found:
                    print(
                        f"    ✅ {started_proc['app_name']} (PID: {started_proc['pid']}) is visible"
                    )
                else:
                    print(
                        f"    ⚠️  {started_proc['app_name']} (PID: {started_proc['pid']}) not found in visible apps"
                    )
        else:
            print(
                f"  ❌ Failed to list visible apps: {visible_apps_result.error_message}"
            )

        # Example 4: Application Interaction and Validation
        print("\n🎯 Example 4: Application Interaction and Validation")

        if started_processes:
            # Get active window to see if our apps created windows
            print("  Checking active window...")
            active_window_result = session.computer.get_active_window()
            if active_window_result.success and active_window_result.window:
                window_title = getattr(active_window_result.window, "title", "Unknown")
                window_id = active_window_result.window.window_id
                print(f"    ✅ Active window: '{window_title}' (ID: {window_id})")
            else:
                print("    ℹ️  No active window or failed to get active window")

            # List all root windows to see application windows
            print("  Listing application windows...")
            windows_result = session.computer.list_root_windows()
            if windows_result.success:
                windows = windows_result.windows
                print(f"    ✅ Found {len(windows)} application windows")

                for i, window in enumerate(windows[:10]):  # Show first 10 windows
                    title = getattr(window, "title", "Untitled")
                    window_id = window.window_id
                    print(f"      {i+1}. '{title}' (ID: {window_id})")
            else:
                print(f"    ❌ Failed to list windows: {windows_result.error_message}")

        time.sleep(3)  # Let applications fully initialize

        # Example 5: Application Stopping by PID
        print("\n🛑 Example 5: Application Stopping by PID")

        # Stop applications using PID
        pids_to_stop = []
        for process in started_processes[:1]:  # Stop first started process
            if process["pid"]:
                pids_to_stop.append(process)

        for process in pids_to_stop:
            app_name = process["app_name"]
            pid = process["pid"]

            print(f"  Stopping {app_name} by PID ({pid})...")
            stop_result = session.computer.stop_app_by_pid(pid)
            if stop_result.success:
                print(f"    ✅ {app_name} stopped successfully by PID")

                # Remove from started_processes list
                started_processes = [p for p in started_processes if p["pid"] != pid]
            else:
                print(
                    f"    ❌ Failed to stop {app_name} by PID: {stop_result.error_message}"
                )

            time.sleep(2)
        # Example 6: Advanced Application Management
        print("\n🔧 Example 6: Advanced Application Management")

        # Demonstrate starting and immediately managing an application
        if chrome_app:
            test_app = chrome_app
            print(f"  Testing advanced lifecycle with {test_app}...")
            app_name = getattr(test_app, "name", "Test App")
            start_cmd = test_app.start_cmd

            print(f"  Advanced lifecycle test with {app_name}...")

            # Start application
            print("    Starting application...")
            start_result = session.computer.start_app(start_cmd)
            if start_result.success and len(start_result.data) > 0:
                test_process = start_result.data[0]
                test_pid = getattr(test_process, "pid", None)
                test_pname = getattr(test_process, "pname", None)

                print(f"      ✅ Started: PID={test_pid}, Process={test_pname}")

                # Wait for application to initialize
                time.sleep(3)
                # Clean up - stop the test application
                print("    Cleaning up test application...")
                if test_pname:
                    cleanup_result = session.computer.stop_app_by_pname(test_pname)
                    if cleanup_result.success:
                        print("      ✅ Test application cleaned up successfully")
                    else:
                        print(
                            f"      ⚠️  Cleanup failed: {cleanup_result.error_message}"
                        )

                time.sleep(2)
            else:
                print(
                    f"    ❌ Failed to start test application: {start_result.error_message}"
                )

        print("\n📊 Application Operations Summary:")
        print("  • Application discovery and enumeration")
        print("  • Application starting with command execution")
        print("  • Running application monitoring and listing")
        print("  • Process identification and tracking")
        print("  • Application stopping by PID")
        print("  • Application stopping by process name")
        print("  • Application lifecycle verification")
        print("  • Window creation and management integration")
        print("  • Advanced application management workflows")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        raise

    finally:
        # Clean up session
        if session:
            agb.delete(session)
            print("🧹 Session cleaned up")

    print("🎉 Application operations example completed successfully!")


if __name__ == "__main__":
    main()
