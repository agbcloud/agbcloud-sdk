"""
Computer module functional validation tests.
These tests validate that mouse operations actually work by checking cursor position changes.
"""

import os
import time
import unittest
import json
from agb import agb,MouseButton,ScrollDirection
from agb.session_params import CreateSessionParams
try:
    from .functional_helpers import FunctionalTestResult, validate_cursor_position, get_screen_center
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    # Add project root to path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from tests.integration.functional_helpers import FunctionalTestResult, validate_cursor_position, get_screen_center

def get_cursor_coordinates(position_result):
    """
    Extract x, y coordinates from OperationResult for logging purposes.

    Note: This is only needed for logging/debugging. For validation,
    use validate_cursor_position() directly with the OperationResult.
    """
    if not position_result.success:
        raise ValueError(f"Failed to get cursor position: {position_result.error_message}")

    data = position_result.data
    if isinstance(data, dict):
        return (data.get('x', 0), data.get('y', 0))
    elif isinstance(data, str):
        data = json.loads(data)
        return (data.get('x', 0), data.get('y', 0))
    else:
        return (data.get('x', 0) if hasattr(data, 'get') else 0,
                data.get('y', 0) if hasattr(data, 'get') else 0)

class TestComputerFunctionalValidation(unittest.TestCase):
    """Computer module functional validation tests."""

    def setUp(self):
        """Set up test fixtures."""
        # Skip if no API key provided
        api_key = os.environ.get("AGB_API_KEY")
        if not api_key:
            self.skipTest("AGB_API_KEY environment variable not set")

        # Create AGB client and session
        self.agb_client = agb.AGB(api_key=api_key)
        session_params = CreateSessionParams(image_id="agb-computer-use-ubuntu-2204")

        session_result = self.agb_client.create(session_params)
        if not session_result.success or session_result.session is None:
            error_msg = f"Session creation failed. Error: {session_result.error_message}, Success: {session_result.success}, Request ID: {session_result.request_id}"
            self.fail(error_msg)

        self.session = session_result.session
        self.cursor_tolerance = 5  # pixels

        print(f"Created Computer functional validation session: {self.session.session_id}")

        # Wait for session to be ready
        time.sleep(3)

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'session') and self.session:
            try:
                delete_result = self.session.delete()
                if delete_result and hasattr(delete_result, 'request_id') and delete_result.request_id:
                    print(f"Session {self.session.session_id} deleted successfully")
                # Wait for session to be fully deleted before next test
                time.sleep(2)
            except Exception as e:
                print(f"Error deleting session: {e}")

    def test_mouse_operation_validation(self):
        """Test comprehensive mouse operations including click, move, and drag functionality."""
        result = FunctionalTestResult("MouseOperationValidation")
        start_time = time.time()

        try:
            # Get screen center coordinates for all operations
            center_x, center_y = get_screen_center(self.session)

            # Test 1: Mouse Click Validation
            print("Testing mouse click functionality...")
            target_x, target_y = center_x, center_y

            # Step 1: Click at screen center
            click_result = self.session.computer.mouse.click(target_x, target_y, MouseButton.LEFT)
            if not click_result.success:
                result.set_failure(f"Mouse click operation failed: {click_result.error_message}")
                return

            # Wait for click to complete
            time.sleep(1)

            # Step 2: Verify cursor position after click
            try:
                position_result = self.session.computer.mouse.get_position()
                if not position_result.success:
                    result.set_failure(f"Failed to get cursor position after click: {position_result.error_message}")
                    return
                new_x, new_y = get_cursor_coordinates(position_result)
            except Exception as e:
                result.set_failure(f"Failed to get cursor position after click: {e}")
                return

            result.add_detail("click_new_cursor", {"x": new_x, "y": new_y})
            result.add_detail("click_target_position", {"x": target_x, "y": target_y})

            # Validate cursor moved to click position
            if not validate_cursor_position(position_result, target_x, target_y, self.cursor_tolerance):
                result.set_failure("Cursor position validation failed after click")
                print(f"❌ Mouse click failed: expected ({target_x},{target_y}), got ({new_x},{new_y})")
                return

            print(f"✅ Mouse clicked to ({new_x},{new_y}), target was ({target_x},{target_y})")

            # Test 2: Mouse Movement Validation
            print("Testing mouse movement functionality...")
            target_x, target_y = center_x - 100, center_y + 100

            print("target_position", {"x": target_x, "y": target_y})

            # Step 1: Move mouse to screen center
            move_result = self.session.computer.mouse.move(target_x, target_y)
            if not move_result.success:
                result.set_failure(f"Mouse move operation failed: {move_result.error_message}")
                return

            # Wait for movement to complete
            time.sleep(1)

            # Step 2: Verify cursor position changed
            try:
                position_result = self.session.computer.mouse.get_position()
                if not position_result.success:
                    result.set_failure(f"Failed to get new cursor position: {position_result.error_message}")
                    return
                new_x, new_y = get_cursor_coordinates(position_result)
            except Exception as e:
                result.set_failure(f"Failed to get new cursor position: {e}")
                return

            result.add_detail("move_new_cursor", {"x": new_x, "y": new_y})
            print("new_cursor", {"x": new_x, "y": new_y})
            result.add_detail("move_target_position", {"x": target_x, "y": target_y})

            # Validate cursor movement
            if not validate_cursor_position(position_result, target_x, target_y, self.cursor_tolerance):
                result.set_failure("Cursor position validation failed after move")
                print(f"❌ Mouse movement failed: expected ({target_x},{target_y}), got ({new_x},{new_y})")
                return

            print(f"✅ Mouse moved to ({new_x},{new_y}), target was ({target_x},{target_y})")

            # Test 3: Mouse Drag Validation
            print("Testing mouse drag functionality...")
            # Define drag positions around center
            from_x, from_y = center_x - 50, center_y - 50
            to_x, to_y = center_x + 50, center_y + 50

            # Step 1: Perform drag operation using screen-based positions
            drag_result = self.session.computer.mouse.drag(from_x, from_y, to_x, to_y, MouseButton.LEFT)
            if not drag_result.success:
                result.set_failure(f"Mouse drag operation failed: {drag_result.error_message}")
                return

            # Wait for drag to complete
            time.sleep(1)

            # Step 2: Verify cursor position after drag
            try:
                position_result = self.session.computer.mouse.get_position()
                if not position_result.success:
                    result.set_failure(f"Failed to get cursor position after drag: {position_result.error_message}")
                    return
                new_x, new_y = get_cursor_coordinates(position_result)
            except Exception as e:
                result.set_failure(f"Failed to get cursor position after drag: {e}")
                return

            result.add_detail("drag_new_cursor", {"x": new_x, "y": new_y})
            result.add_detail("drag_from", {"x": from_x, "y": from_y})
            result.add_detail("drag_to", {"x": to_x, "y": to_y})

            # Validate cursor ended at drag destination
            if not validate_cursor_position(position_result, to_x, to_y, self.cursor_tolerance):
                result.set_failure("Cursor position validation failed after drag")
                print(f"❌ Mouse drag failed: expected end at ({to_x},{to_y}), got ({new_x},{new_y})")
                return

            print(f"✅ Mouse dragged from ({from_x},{from_y}) to ({to_x},{to_y}), final position ({new_x},{new_y})")
            # All tests passed
            result.set_success("All mouse operations validation successful")
            print("✅ All mouse operations (click, move, drag) validated successfully")

        finally:
            result.duration = time.time() - start_time
            print(f"Test Result: {result}")
            self.assertTrue(result.success, result.message)

    def test_keyboard_input_validation(self):
        """Test keyboard input functionality by verifying API returns success.

        Note: Visual validation of keyboard input requires an active text input field.
        This test validates that keyboard operations execute successfully via the API.
        """
        result = FunctionalTestResult("KeyboardInputValidation")
        start_time = time.time()

        try:
            # Test keyboard input API operations
            test_text = "AGB Test"

            # Test 1: type text
            input_result = self.session.computer.keyboard.type(test_text)
            if not input_result.success:
                result.set_failure(f"Failed to input text: {input_result.error_message}")
                return
            else:
                result.add_detail("input_text_success", True)

            time.sleep(0.5)

            # Test 2: press (Ctrl+A)
            select_result = self.session.computer.keyboard.press(["Ctrl", "a"])
            if not select_result.success:
                result.set_failure(f"Failed to press Ctrl+A: {select_result.error_message}")
                return
            else:
                result.add_detail("press_keys_success", True)

            time.sleep(0.5)

            # Test 3: press (Delete)
            delete_result = self.session.computer.keyboard.press(["Delete"])
            if not delete_result.success:
                result.set_failure(f"Failed to press Delete: {delete_result.error_message}")
                return
            else:
                result.add_detail("delete_keys_success", True)

            time.sleep(0.5)

            # Test 4: press with hold (Shift key)
            hold_result = self.session.computer.keyboard.press(["Shift"], hold=True)
            if not hold_result.success:
                result.set_failure(f"Failed to press and hold Shift: {hold_result.error_message}")
                return
            else:
                result.add_detail("press_keys_hold_success", True)

            time.sleep(0.5)

            # Test 5: release (Release Shift key)
            release_result = self.session.computer.keyboard.release(["Shift"])
            if not release_result.success:
                result.set_failure(f"Failed to release Shift: {release_result.error_message}")
                return
            else:
                result.add_detail("release_keys_success", True)

            result.set_success("Keyboard API operations validated successfully")
            print("✅ Keyboard operations: type, press(Ctrl+A), press(Delete), press(Shift, hold=True), release(Shift) all successful")

        finally:
            result.duration = time.time() - start_time
            print(f"Test Result: {result}")
            self.assertTrue(result.success, result.message)

    def test_list_installed_start_menu_true_vs_false(self):
        """Create Ubuntu sandbox, call list_installed with start_menu=True and start_menu=False, compare results."""
        # Call list_installed(start_menu=True)
        result_with_start_menu = self.session.computer.app.list_installed(start_menu=True)
        self.assertTrue(
            result_with_start_menu.success,
            f"list_installed(start_menu=True) failed: {result_with_start_menu.error_message}",
        )
        apps_with_start_menu = result_with_start_menu.data or []
        names_with_start_menu = {getattr(app, "name", "") for app in apps_with_start_menu}

        # Call list_installed(start_menu=False)
        result_without_start_menu = self.session.computer.app.list_installed(start_menu=False)
        self.assertTrue(
            result_without_start_menu.success,
            f"list_installed(start_menu=False) failed: {result_without_start_menu.error_message}",
        )
        apps_without_start_menu = result_without_start_menu.data or []
        names_without_start_menu = {getattr(app, "name", "") for app in apps_without_start_menu}

        # Compare and report differences
        count_with = len(apps_with_start_menu)
        count_without = len(apps_without_start_menu)
        only_when_true = names_with_start_menu - names_without_start_menu
        only_when_false = names_without_start_menu - names_with_start_menu
        common = names_with_start_menu & names_without_start_menu

        print(f"list_installed(start_menu=True):  count={count_with}")
        print(f"list_installed(start_menu=False): count={count_without}")
        print(f"Common app names (in both): {len(common)}")
        print(f"Only when start_menu=True (start menu / app menu apps): {sorted(only_when_true)[:20]}{'...' if len(only_when_true) > 20 else ''}")
        print(f"Only when start_menu=False: {sorted(only_when_false)[:20]}{'...' if len(only_when_false) > 20 else ''}")

        # When start_menu=True we typically include start menu apps, so count can be >= count when False
        # (Behavior may vary by image; we only assert both calls succeeded and report the diff.)
        self.assertIsInstance(count_with, int)
        self.assertIsInstance(count_without, int)

    def test_deprecated_get_screen_size_on_real_session(self):
        """
        Integration test: call deprecated computer.get_screen_size() on real Ubuntu session.
        Verifies DeprecationWarning is emitted and the deprecated API still returns valid result.
        """
        with self.assertWarns(DeprecationWarning) as cm:
            result = self.session.computer.get_screen_size()

        self.assertIn("get_screen_size() is deprecated", str(cm.warning))
        self.assertIn("computer.screen.get_size", str(cm.warning))
        self.assertTrue(result.success, result.error_message or "get_screen_size failed")
        self.assertIsNotNone(result.data, "get_screen_size returned no data")
        if isinstance(result.data, dict):
            self.assertIn("width", result.data)
            self.assertIn("height", result.data)
            print(f"Deprecated get_screen_size(): success={result.success}, width={result.data.get('width')}, height={result.data.get('height')}")
        else:
            print(f"Deprecated get_screen_size(): success={result.success}, data type={type(result.data).__name__}")
        print(f"DeprecationWarning message: {cm.warning}")

    def test_app_visible_on_real_session(self):
        """
        Integration test: call app.get_visible() to list applications with visible windows.
        """
        # Start an application first to ensure a visible window exists.
        apps_result = self.session.computer.app.list_installed()
        self.assertTrue(
            apps_result.success,
            f"list_installed failed: {apps_result.error_message}",
        )
        installed_apps = apps_result.data or []
        self.assertTrue(installed_apps, "list_installed returned empty app list")
        start_cmd = getattr(installed_apps[3], "start_cmd", "")
        self.assertTrue(start_cmd, "installed app has empty start_cmd")

        start_result = self.session.computer.app.start(start_cmd)
        self.assertTrue(
            start_result.success,
            f"app.start failed: {start_result.error_message}",
        )
        self.assertTrue(start_result.data, "app.start returned no processes")

        # Give the app time to create a window.
        time.sleep(3)

        visible_result = self.session.computer.app.get_visible()
        self.assertTrue(
            visible_result.success,
            f"app.get_visible() failed: {visible_result.error_message}",
        )
        visible_apps = visible_result.data or []
        print(f"app.get_visible() returned {len(visible_apps)} apps")
        for app in visible_apps[:5]:
            pname = getattr(app, "pname", "")
            pid = getattr(app, "pid", "")
            cmdline = getattr(app, "cmdline", "")
            print(f"- {pname} (PID: {pid}) {cmdline}")

    def test_application_operation_validation(self):
        """Test complete app lifecycle: install list -> start -> verify -> list processes -> stop -> verify."""
        result = FunctionalTestResult("ApplicationOperationValidation")
        start_time = time.time()

        try:
            # Step 1: Get installed apps and validate data
            print("Step 1: Testing get installed apps functionality...")
            try:
                installed_apps_result = self.session.computer.app.list_installed()
                if not installed_apps_result.success:
                    result.set_failure(f"Failed to get installed apps: {installed_apps_result.error_message}")
                    return
                installed_apps = installed_apps_result.data
            except Exception as e:
                result.set_failure(f"Failed to get installed apps: {e}")
                return

            # Validate data length > 0
            self.assertGreater(len(installed_apps), 0, "Installed apps data length should be greater than 0")
            print(f"Installed apps data: {installed_apps}")
            result.add_detail("installed_apps_data", installed_apps)

            # Find Google Chrome app in the list
            first_app = None
            for app in installed_apps:
                if hasattr(app, 'name') and app.name == "Google Chrome":
                    first_app = app
                    break

            # If Google Chrome not found, use the first app as fallback
            if first_app is None:
                print("Google Chrome not found in installed apps, using first app as fallback")
                first_app = installed_apps[0]
            else:
                print(f"Found Google Chrome app: {first_app.name}")
                result.add_detail("selected_app_name", "Google Chrome")

            # Get first app data and extract app name and start command
            start_cmd = first_app.start_cmd
            app_name = getattr(first_app, 'name', 'Unknown App')
            print(f"Selected app: {app_name}, start_cmd: {start_cmd}")
            result.add_detail("selected_app", {"name": app_name, "start_cmd": start_cmd})

            # Step 2: Start app and verify through active window
            print("Step 2: Testing start app functionality...")
            try:
                start_result = self.session.computer.app.start(start_cmd)
                if not start_result.success or not start_result.data:
                    result.set_failure(f"Failed to start app: {start_result.error_message}")
                    return
                processes = start_result.data
            except Exception as e:
                result.set_failure(f"Failed to start app: {e}")
                return

            print(f"Start app result: {processes}")
            result.add_detail("start_app_data", processes)

            # Get first item from processes and print cmdline, pid, pname
            if len(processes) > 0:
                first_process = processes[0]
                cmdline = getattr(first_process, 'cmdline', 'N/A')
                pid = getattr(first_process, 'pid', 'N/A')
                pname = getattr(first_process, 'pname', 'N/A')
                print(f"First process details - cmdline: {cmdline}, pid: {pid}, pname: {pname}")
                result.add_detail("first_process_details", {"cmdline": cmdline, "pid": pid, "pname": pname})

            # Wait for app to fully start
            time.sleep(3)

            # Verify app started by checking active window
            print("Step 2 Verification: Checking if app window became active...")
            try:
                active_window_result = self.session.computer.window.get_active_window()
                if not active_window_result.success:
                    print(f"⚠️ Failed to get active window: {active_window_result.error_message}")
                    result.add_detail("active_window_after_start", None)
                else:
                    active_window = active_window_result.window
                    if active_window:
                        active_window_id = str(active_window.window_id)
                        active_window_title = getattr(active_window, 'title', 'Unknown')
                        print(f"✅ Active window found: ID={active_window_id}, Title={active_window_title}")
                        result.add_detail("active_window_after_start", {
                            "window_id": active_window_id,
                            "title": active_window_title
                        })
                    else:
                        print("⚠️ No active window found after starting app")
                        result.add_detail("active_window_after_start", None)
            except Exception as e:
                print(f"⚠️ Failed to get active window: {e}")
                result.add_detail("active_window_after_start", None)

            # Step 3: List visible apps and validate
            print("Step 3: Testing list visible apps functionality...")
            try:
                visible_apps_result = self.session.computer.app.get_visible()
                if not visible_apps_result.success:
                    result.set_failure(f"Failed to list visible apps: {visible_apps_result.error_message}")
                    return
                visible_apps = visible_apps_result.data
            except Exception as e:
                result.set_failure(f"Failed to list visible apps: {e}")
                return

            print(f"Visible apps data: {visible_apps}")
            result.add_detail("visible_apps_data", visible_apps)
            # Find the started app process in visible apps list by matching PID
            target_process = None
            for process in visible_apps:
                # Match by PID from the started process
                process_pid = getattr(process, 'pid', None)
                if process_pid == pid:
                    target_process = process
                    break

            if target_process is None:
                result.set_failure("Could not find started app in visible apps list")
                print("❌ Started app not found in visible apps list")
                return

            target_pid = target_process.pid
            print(f"✅ Found target process: PID={target_pid}, Name={getattr(target_process, 'pname', 'Unknown')}")
            result.add_detail("target_process", {
                "pid": target_pid,
                "process_name": getattr(target_process, 'process_name', 'Unknown'),
                "cmd": getattr(target_process, 'cmd', '')
            })

            # Step 4: Stop app by PID and validate
            print("Step 4: Testing stop app by PID functionality...")
            stop_result = self.session.computer.app.stop_by_pid(target_pid)
            if not stop_result.success:
                result.set_failure(f"Failed to stop app by PID: {stop_result.error_message}")
                return

            # Validate success is True
            self.assertTrue(stop_result.success, "stop app by PID success should be True")
            print(f"✅ App stopped successfully using PID: {target_pid}")
            result.add_detail("stop_app_success", True)

            # Wait for app to fully stop
            time.sleep(3)

            # Step 4 Verification: Verify app is no longer in visible apps
            print("Step 4 Verification: Checking if app is no longer visible...")
            try:
                final_visible_apps_result = self.session.computer.app.get_visible()
                if not final_visible_apps_result.success:
                    print(f"⚠️ Failed to get visible apps: {final_visible_apps_result.error_message}")
                    result.add_detail("app_stop_verification", "verification_failed")
                else:
                    final_visible_apps = final_visible_apps_result.data
                    app_still_visible = False
                    for process in final_visible_apps:
                        if process.pid == target_pid:
                            app_still_visible = True
                            break

                    if app_still_visible:
                        print(f"⚠️ App with PID {target_pid} is still visible after stop command")
                        result.add_detail("app_stop_verification", "still_visible")
                    else:
                        print(f"✅ App with PID {target_pid} is no longer visible")
                        result.add_detail("app_stop_verification", "not_visible")
            except Exception as e:
                print(f"⚠️ Could not verify app stop status: {e}")
                result.add_detail("app_stop_verification", "verification_failed")

            # All tests passed
            result.set_success("All application operation validation successful")
            print("✅ All application operations (list, start, verify, list processes, stop, verify) validated successfully")

        finally:
            result.duration = time.time() - start_time
            print(f"Test Result: {result}")
            self.assertTrue(result.success, result.message)

    def test_window_operation_validation(self):
        """Test comprehensive window operations including list, activate, minimize, maximize, resize, fullscreen, and close functionality."""
        result = FunctionalTestResult("WindowOperationValidation")
        start_time = time.time()

        try:
            # Step 1: Get installed apps and print data
            print("Step 1: Testing get installed apps functionality...")
            try:
                installed_apps_result = self.session.computer.app.list_installed()
                if not installed_apps_result.success:
                    result.set_failure(f"Failed to get installed apps: {installed_apps_result.error_message}")
                    return
                installed_apps = installed_apps_result.data
            except Exception as e:
                result.set_failure(f"Failed to get installed apps: {e}")
                return

            print(f"Installed apps data: {installed_apps}")
            result.add_detail("installed_apps_data", installed_apps)

            if len(installed_apps) == 0:
                result.set_failure("No installed apps found")
                print("❌ No installed apps found")
                return

            # Find Google Chrome app in the list
            first_app = None
            for app in installed_apps:
                if hasattr(app, 'name') and app.name == "Google Chrome":
                    first_app = app
                    break

            # If Google Chrome not found, use the first app as fallback
            if first_app is None:
                print("Google Chrome not found in installed apps, using first app as fallback")
                first_app = installed_apps[0]
            else:
                print(f"Found Google Chrome app: {first_app.name}")
                result.add_detail("selected_app_name", "Google Chrome")
            print(f"First app: {first_app}")
            start_cmd = first_app.start_cmd
            print(f"First app start_cmd: {start_cmd}")
            result.add_detail("first_app_start_cmd", start_cmd)

            # Step 2: Start app and validate success
            print("Step 2: Testing start app functionality...")
            try:
                start_result = self.session.computer.app.start(start_cmd)
                if not start_result.success or not start_result.data:
                    result.set_failure(f"Failed to start app: {start_result.error_message}")
                    return
                processes = start_result.data
            except Exception as e:
                result.set_failure(f"Failed to start app: {e}")
                return

            # Print data and check length > 0
            print(f"Start app data: {processes}")
            result.add_detail("start_app_data", processes)

            # Validate data length > 0
            self.assertGreater(len(processes), 0, "start app data length should be greater than 0")
            print(f"Start app data length: {len(processes)}")
            result.add_detail("start_app_data_length", len(processes))

            # Get first process details for cleanup later
            first_process = processes[0]
            app_pname = getattr(first_process, 'pname', None)
            print(f"Started app process name: {app_pname}")
            result.add_detail("started_app_pname", app_pname)

            print("✅ Application management operations completed successfully")
            time.sleep(3)
            # Step 3: List root windows and get the first window_id
            print("Step 3: Testing list root windows functionality...")
            try:
                windows_result = self.session.computer.window.list_root_windows()
                if not windows_result.success:
                    result.set_failure(f"Failed to list root windows: {windows_result.error_message}")
                    return
                windows = windows_result.windows
            except Exception as e:
                result.set_failure(f"Failed to list root windows: {e}")
                return

            print(f"Windows found: {windows}")
            result.add_detail("windows_list", [{"window_id": w.window_id, "title": w.title} for w in windows])

            if len(windows) == 0:
                result.set_failure("No windows found, skipping window operations test")
                print("⚠️ No windows found, skipping remaining window operations")
                return

            # Get the first window's ID
            target_window = windows[0]
            window_id = target_window.window_id
            print(f"Using window ID: {window_id}, Title: {target_window.title}")
            result.add_detail("target_window_id", window_id)
            result.add_detail("target_window_title", target_window.title)

            # Step 4: Activate window
            print("Step 4: Testing activate window functionality...")
            activate_result = self.session.computer.window.activate(window_id)
            if not activate_result.success:
                result.set_failure(f"Failed to activate window: {activate_result.error_message}")
                print(f"❌ Window activation failed: {activate_result.error_message}")
                return

            print(f"✅ Window {window_id} activated successfully")
            result.add_detail("activate_success", True)

            # Step 5: Verify window is active
            print("Step 5: Testing get active window functionality...")
            try:
                active_window_result = self.session.computer.window.get_active_window()
                if not active_window_result.success:
                    print(f"⚠️ Failed to get active window: {active_window_result.error_message}")
                    result.add_detail("active_window_verification", False)
                else:
                    active_window = active_window_result.window
                    if active_window and active_window.window_id == window_id:
                        print(f"✅ Window {window_id} is correctly active")
                        result.add_detail("active_window_verification", True)
                    else:
                        active_id = str(active_window.window_id) if active_window else "None"
                        result.set_failure(f"Active window verification failed: expected {window_id}, got {active_id}")
                        print(f"❌ Active window mismatch: expected {window_id}, got {active_id}")
                        return
            except Exception as e:
                result.set_failure(f"Failed to get active window: {e}")
                return

            # Step 6: Enable focus mode and get cursor position
            print("Step 6: Testing focus mode and get cursor position functionality...")
            focus_result = self.session.computer.window.focus_mode(True)
            if not focus_result.success:
                result.set_failure(f"Failed to enable focus mode: {focus_result.error_message}")
                return

            print("✅ Focus mode enabled successfully")
            result.add_detail("focus_mode_success", True)

            try:
                position_result = self.session.computer.mouse.get_position()
                if not position_result.success:
                    result.set_failure(f"Failed to get cursor position: {position_result.error_message}")
                else:
                    cursor_x, cursor_y = get_cursor_coordinates(position_result)
                    print(f"Current cursor position: ({cursor_x}, {cursor_y})")
                    result.add_detail("cursor_position", {"x": cursor_x, "y": cursor_y})
            except Exception as e:
                result.set_failure(f"Failed to get cursor position: {e}")
                return

            # Step 7: Minimize window
            print("Step 7: Testing minimize window functionality...")
            minimize_result = self.session.computer.window.minimize(window_id)
            if not minimize_result.success:
                result.set_failure(f"Failed to minimize window: {minimize_result.error_message}")
                return

            print(f"✅ Window {window_id} minimized successfully")
            result.add_detail("minimize_success", True)
            time.sleep(3)

            # Step 8: Maximize window
            print("Step 8: Testing maximize window functionality...")
            maximize_result = self.session.computer.window.maximize(window_id)
            if not maximize_result.success:
                result.set_failure(f"Failed to maximize window: {maximize_result.error_message}")
                return

            print(f"✅ Window {window_id} maximized successfully")
            result.add_detail("maximize_success", True)
            time.sleep(3)
            # Step 9: Restore window
            print("Step 9: Testing restore window functionality...")
            restore_result = self.session.computer.window.restore(window_id)
            if not restore_result.success:
                result.set_failure(f"Failed to restore window: {restore_result.error_message}")
                return

            print(f"✅ Window {window_id} restored successfully")
            result.add_detail("restore_success", True)
            time.sleep(3)

            # Step 10: Resize window
            print("Step 10: Testing resize window functionality...")
            resize_result = self.session.computer.window.resize(window_id, 300, 500)
            if not resize_result.success:
                result.set_failure(f"Failed to resize window: {resize_result.error_message}")
                return

            print(f"✅ Window {window_id} resized to 300x500 successfully")
            result.add_detail("resize_success", True)
            time.sleep(3)

            # Step 11: Fullscreen window
            print("Step 11: Testing fullscreen window functionality...")
            fullscreen_result = self.session.computer.window.fullscreen(window_id)
            if not fullscreen_result.success:
                result.set_failure(f"Failed to fullscreen window: {fullscreen_result.error_message}")
                return

            print(f"✅ Window {window_id} set to fullscreen successfully")
            result.add_detail("fullscreen_success", True)
            time.sleep(3)

            # Step 12: Close window and verify it's no longer active
            print("Step 12: Testing close window functionality...")
            close_result = self.session.computer.window.close(window_id)
            if not close_result.success:
                result.set_failure(f"Failed to close window: {close_result.error_message}")
                return

            print(f"✅ Window {window_id} closed successfully")
            result.add_detail("close_success", True)
            time.sleep(3)
            #Step 13: Verify window is no longer active
            print("Step 13: Testing list root windows functionality...")
            try:
                final_windows_result = self.session.computer.window.list_root_windows()
                if not final_windows_result.success:
                    print(f"⚠️ Failed to list windows: {final_windows_result.error_message}")
                    result.add_detail("window_close_verification", "verification_failed")
                else:
                    final_windows = final_windows_result.windows
                    window_still_exists = False
                    for window in final_windows:
                        if window.window_id == window_id:
                            window_still_exists = True
                            break

                    if window_still_exists:
                        result.set_failure(f"Window {window_id} still exists after closing")
                        print(f"❌ Window {window_id} still exists after closing")
                        return
                    else:
                        print(f"✅ Window {window_id} has been successfully closed")
                        result.add_detail("close_verification", True)
            except Exception as e:
                print(f"❌ Failed to verify window closure: {e}")
                result.add_detail("close_verification", False)


            # All tests passed
            result.set_success("All window operations validation successful")
            print("✅ All window operations (list, activate, minimize, maximize, restore, resize, fullscreen, close) validated successfully")

            #Step 14: Cleanup: Stop the started application
            print("Step 14: Cleanup: Stopping started application...")
            if app_pname:
                print(f"Cleanup: Stopping application with process name: {app_pname}")
                stop_result = self.session.computer.app.stop_by_pname(app_pname)
                if stop_result.success:
                    print(f"✅ Application {app_pname} stopped successfully")
                    result.add_detail("cleanup_stop_app_success", True)
                else:
                    print(f"⚠️ Failed to stop application {app_pname}: {stop_result.error_message}")
                    result.add_detail("cleanup_stop_app_success", False)
                    result.add_detail("cleanup_stop_app_error", stop_result.error_message)

                # Wait for app to fully stop
                time.sleep(2)
            else:
                print("⚠️ No process name available for cleanup")
                result.add_detail("cleanup_stop_app_success", False)
                result.add_detail("cleanup_stop_app_error", "No process name available")

        finally:
            result.duration = time.time() - start_time
            print(f"Test Result: {result}")
            self.assertTrue(result.success, result.message)

    def test_scroll_operation_validation(self):
        """Test comprehensive scroll operations including app management, window operations, and scroll functionality."""
        result = FunctionalTestResult("ScrollOperationValidation")
        start_time = time.time()

        try:
            # Step 1: Get installed apps and validate data
            print("Step 1: Testing get installed apps functionality...")
            try:
                installed_apps_result = self.session.computer.app.list_installed()
                if not installed_apps_result.success:
                    result.set_failure(f"Failed to get installed apps: {installed_apps_result.error_message}")
                    return
                installed_apps = installed_apps_result.data
            except Exception as e:
                result.set_failure(f"Failed to get installed apps: {e}")
                return

            # Validate data length > 0
            self.assertGreater(len(installed_apps), 0, "Installed apps data length should be greater than 0")
            print(f"Installed apps data: {installed_apps}")
            result.add_detail("installed_apps_data", installed_apps)

            # Find Google Chrome app in the list
            first_app = None
            for app in installed_apps:
                if hasattr(app, 'name') and app.name == "Google Chrome":
                    first_app = app
                    break

            # If Google Chrome not found, use the first app as fallback
            if first_app is None:
                print("Google Chrome not found in installed apps, using first app as fallback")
                first_app = installed_apps[0]
            else:
                print(f"Found Google Chrome app: {first_app.name}")
                result.add_detail("selected_app_name", "Google Chrome")
            start_cmd = first_app.start_cmd
            print(f"First app start_cmd: {start_cmd}")
            result.add_detail("first_app_start_cmd", start_cmd)

            # Step 2: Start app and validate success
            print("Step 2: Testing start app functionality...")
            try:
                start_result = self.session.computer.app.start(start_cmd)
                if not start_result.success or not start_result.data:
                    result.set_failure(f"Failed to start app: {start_result.error_message}")
                    return
                processes = start_result.data
            except Exception as e:
                result.set_failure(f"Failed to start app: {e}")
                return

            # Validate data length > 0
            self.assertGreater(len(processes), 0, "Start app data length should be greater than 0")
            print(f"Start app data: {processes}")
            result.add_detail("start_app_data", processes)

            # Get first item from processes and print cmdline, pid, pname
            first_process = processes[0]
            cmdline = getattr(first_process, 'cmdline', 'N/A')
            pid = getattr(first_process, 'pid', 'N/A')
            pname = getattr(first_process, 'pname', 'N/A')
            print(f"First process details - cmdline: {cmdline}, pid: {pid}, pname: {pname}")
            result.add_detail("first_process_details", {"cmdline": cmdline, "pid": pid, "pname": pname})

            # Wait for app to fully start
            time.sleep(3)

            # Step 3: Get screen size and calculate center coordinates
            print("Step 3: Testing get screen size functionality...")
            # Use helper function to get screen center coordinates
            center_x, center_y = get_screen_center(self.session)
            result.add_detail("scroll_center_coordinates", {"x": center_x, "y": center_y})

            # Step 4: Get active window and window_id
            print("Step 4: Testing get active window functionality...")
            try:
                active_window_result = self.session.computer.window.get_active_window()
                if not active_window_result.success or not active_window_result.window:
                    result.set_failure(f"Failed to get active window: {active_window_result.error_message if active_window_result.success else 'no active window'}")
                    return
                active_window = active_window_result.window
            except Exception as e:
                result.set_failure(f"Failed to get active window: {e}")
                return

            window_id = active_window.window_id
            print(f"Active window_id: {window_id}")
            result.add_detail("active_window_id", window_id)

            # Step 5: Maximize window
            print("Step 5: Testing maximize window functionality...")
            maximize_result = self.session.computer.window.maximize(window_id)
            if not maximize_result.success:
                result.set_failure(f"Failed to maximize window: {maximize_result.error_message}")
                return

            # Validate success is True
            self.assertTrue(maximize_result.success, "maximize window success should be True")
            print(f"✅ Window {window_id} maximized successfully")
            result.add_detail("maximize_success", True)

            # Wait for window to maximize
            time.sleep(2)

            # Step 6: Enable focus mode
            print("Step 6: Testing focus mode functionality...")
            focus_result = self.session.computer.window.focus_mode(True)
            if not focus_result.success:
                result.set_failure(f"Failed to enable focus mode: {focus_result.error_message}")
                return

            # Validate success is True
            self.assertTrue(focus_result.success, "focus mode success should be True")
            print("✅ Focus mode enabled successfully")
            result.add_detail("focus_mode_success", True)

            # Step 7: Perform scroll operation
            print("Step 7: Testing scroll functionality...")
            scroll_result = self.session.computer.mouse.scroll(center_x, center_y, ScrollDirection.DOWN, 3)
            if not scroll_result.success:
                result.set_failure(f"Failed to perform scroll: {scroll_result.error_message}")
                return

            # Validate success is True
            self.assertTrue(scroll_result.success, "scroll success should be True")
            print(f"✅ Scroll operation at ({center_x}, {center_y}) completed successfully")
            result.add_detail("scroll_success", True)

            # Wait for scroll to complete
            time.sleep(2)

            # Step 8: Stop app and validate termination
            print("Step 8: Testing stop app by pname functionality...")
            stop_result = self.session.computer.app.stop_by_pname(pname)
            if not stop_result.success:
                result.set_failure(f"Failed to stop app: {stop_result.error_message}")
                return

            # Validate success is True
            self.assertTrue(stop_result.success, "stop app by pname success should be True")
            print(f"✅ App stopped successfully using pname: {pname}")
            result.add_detail("stop_app_success", True)

            # Wait for app to fully stop
            time.sleep(3)

            # Verify app termination by checking if no visible apps remain
            print("Step 9 Verification: Checking if no visible apps remain after stopping...")
            try:
                final_visible_apps_result = self.session.computer.app.get_visible()
                if not final_visible_apps_result.success:
                    print(f"❌ Failed to verify app termination: {final_visible_apps_result.error_message}")
                    result.add_detail("app_stop_verification", "verification_failed")
                else:
                    final_visible_apps = final_visible_apps_result.data
                    visible_apps_count = len(final_visible_apps)
                    if visible_apps_count == 0:
                        print("✅ No visible apps found after stopping app - termination successful")
                        result.add_detail("app_stop_verification", "no_visible_apps")
                    else:
                        print(f"⚠️ {visible_apps_count} visible apps still found after stop command")
                        result.add_detail("app_stop_verification", f"{visible_apps_count}_apps_still_visible")
            except Exception as e:
                print(f"❌ Failed to verify app termination: {e}")
                result.add_detail("app_stop_verification", "verification_failed")

            # All tests passed
            result.set_success("All scroll operation validation successful")
            print("✅ All scroll operations (app management, window operations, scroll) validated successfully")

        finally:
            result.duration = time.time() - start_time
            print(f"Test Result: {result}")
            self.assertTrue(result.success, result.message)
if __name__ == '__main__':
    unittest.main()