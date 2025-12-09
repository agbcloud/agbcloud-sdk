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
from .functional_helpers import  FunctionalTestResult,validate_cursor_position,get_screen_center

def get_cursor_coordinates(cursor_result):
    """Extract x, y coordinates from cursor result."""
    try:
        cursor_data = cursor_result.data
        if isinstance(cursor_data, str):
            cursor_data = json.loads(cursor_data)
        return cursor_data.get('x', 0), cursor_data.get('y', 0)
    except Exception:
        return 0, 0

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
        session_params = CreateSessionParams(image_id="agb-linux-test-5")
        
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
            click_result = self.session.computer.click_mouse(target_x, target_y, MouseButton.LEFT)
            if not click_result.success:
                result.set_failure(f"Mouse click operation failed: {click_result.error_message}")
                return
            
            # Wait for click to complete
            time.sleep(1)
            
            # Step 2: Verify cursor position after click
            new_cursor = self.session.computer.get_cursor_position()
            if not new_cursor.success:
                result.set_failure(f"Failed to get cursor position after click: {new_cursor.error_message}")
                return
            
            new_x, new_y = get_cursor_coordinates(new_cursor)
            result.add_detail("click_new_cursor", {"x": new_x, "y": new_y})
            result.add_detail("click_target_position", {"x": target_x, "y": target_y})
            
            # Validate cursor moved to click position
            if not validate_cursor_position(new_cursor, target_x, target_y, self.cursor_tolerance):
                result.set_failure("Cursor position validation failed after click")
                print(f"❌ Mouse click failed: expected ({target_x},{target_y}), got ({new_x},{new_y})")
                return
            
            print(f"✅ Mouse clicked to ({new_x},{new_y}), target was ({target_x},{target_y})")
            
            # Test 2: Mouse Movement Validation
            print("Testing mouse movement functionality...")
            target_x, target_y = center_x - 100, center_y + 100
            
            print("target_position", {"x": target_x, "y": target_y})
            
            # Step 1: Move mouse to screen center
            move_result = self.session.computer.move_mouse(target_x, target_y)
            if not move_result.success:
                result.set_failure(f"Mouse move operation failed: {move_result.error_message}")
                return
            
            # Wait for movement to complete
            time.sleep(1)
            
            # Step 2: Verify cursor position changed
            new_cursor = self.session.computer.get_cursor_position()
            if not new_cursor.success:
                result.set_failure(f"Failed to get new cursor position: {new_cursor.error_message}")
                return
            
            new_x, new_y = get_cursor_coordinates(new_cursor)
            result.add_detail("move_new_cursor", {"x": new_x, "y": new_y})
            print("new_cursor", {"x": new_x, "y": new_y})
            result.add_detail("move_target_position", {"x": target_x, "y": target_y})
            
            # Validate cursor movement
            if not validate_cursor_position(new_cursor, target_x, target_y, self.cursor_tolerance):
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
            drag_result = self.session.computer.drag_mouse(from_x, from_y, to_x, to_y, MouseButton.LEFT)
            if not drag_result.success:
                result.set_failure(f"Mouse drag operation failed: {drag_result.error_message}")
                return
            
            # Wait for drag to complete
            time.sleep(1)
            
            # Step 2: Verify cursor position after drag
            new_cursor = self.session.computer.get_cursor_position()
            if not new_cursor.success:
                result.set_failure(f"Failed to get cursor position after drag: {new_cursor.error_message}")
                return
            
            new_x, new_y = get_cursor_coordinates(new_cursor)
            result.add_detail("drag_new_cursor", {"x": new_x, "y": new_y})
            result.add_detail("drag_from", {"x": from_x, "y": from_y})
            result.add_detail("drag_to", {"x": to_x, "y": to_y})
            
            # Validate cursor ended at drag destination
            if not validate_cursor_position(new_cursor, to_x, to_y, self.cursor_tolerance):
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
            
            # Test 1: input_text
            input_result = self.session.computer.input_text(test_text)
            if not input_result.success:
                result.set_failure(f"Failed to input text: {input_result.error_message}")
                return
            else:
                result.add_detail("input_text_success", True)
            
            time.sleep(0.5)
            
            # Test 2: press_keys (Ctrl+A) without hold
            select_result = self.session.computer.press_keys(["Ctrl", "a"], False)
            if not select_result.success:
                result.set_failure(f"Failed to press Ctrl+A: {select_result.error_message}")
                return
            else:
                result.add_detail("press_keys_success", True)
            
            time.sleep(0.5)
            
            # Test 3: press_keys (Delete) without hold
            delete_result = self.session.computer.press_keys(["Delete"], False)
            if not delete_result.success:
                result.set_failure(f"Failed to press Delete: {delete_result.error_message}")
                return
            else:
                result.add_detail("delete_keys_success", True)
            
            time.sleep(0.5)
            
            # Test 4: press_keys with hold=True (Shift key)
            hold_result = self.session.computer.press_keys(["Shift"], True)
            if not hold_result.success:
                result.set_failure(f"Failed to press and hold Shift: {hold_result.error_message}")
                return
            else:
                result.add_detail("press_keys_hold_success", True)
            
            time.sleep(0.5)
            
            # Test 5: release_keys (Release Shift key)
            release_result = self.session.computer.release_keys(["Shift"])
            if not release_result.success:
                result.set_failure(f"Failed to release Shift: {release_result.error_message}")
                return
            else:
                result.add_detail("release_keys_success", True)
            
            result.set_success("Keyboard API operations validated successfully")
            print("✅ Keyboard operations: input_text, press_keys(Ctrl+A), press_keys(Delete), press_keys(Shift, hold=True), release_keys(Shift) all successful")
                
        finally:
            result.duration = time.time() - start_time
            print(f"Test Result: {result}")
            self.assertTrue(result.success, result.message)
    
    def test_application_operation_validation(self):
        """Test complete app lifecycle: install list -> start -> verify -> list processes -> stop -> verify."""
        result = FunctionalTestResult("ApplicationOperationValidation")
        start_time = time.time()
        
        try:
            # Step 1: Get installed apps and validate data
            print("Step 1: Testing get_installed_apps functionality...")
            installed_apps_result = self.session.computer.get_installed_apps()
            if not installed_apps_result.success:
                result.set_failure(f"Failed to get installed apps: {installed_apps_result.error_message}")
                return
            
            # Validate data length > 0
            self.assertGreater(len(installed_apps_result.data), 0, "Installed apps data length should be greater than 0")
            print(f"Installed apps data: {installed_apps_result.data}")
            result.add_detail("installed_apps_data", installed_apps_result.data)
            
            # Find Google Chrome app in the list
            first_app = None
            for app in installed_apps_result.data:
                if hasattr(app, 'name') and app.name == "Google Chrome":
                    first_app = app
                    break
            
            # If Google Chrome not found, use the first app as fallback
            if first_app is None:
                print("Google Chrome not found in installed apps, using first app as fallback")
                first_app = installed_apps_result.data[0]
            else:
                print(f"Found Google Chrome app: {first_app.name}")
                result.add_detail("selected_app_name", "Google Chrome")
            
            # Get first app data and extract app name and start command
            start_cmd = first_app.start_cmd
            app_name = getattr(first_app, 'name', 'Unknown App')
            print(f"Selected app: {app_name}, start_cmd: {start_cmd}")
            result.add_detail("selected_app", {"name": app_name, "start_cmd": start_cmd})
            
            # Step 2: Start app and verify through active window
            print("Step 2: Testing start_app functionality...")
            start_app_result = self.session.computer.start_app(start_cmd)
            if not start_app_result.success:
                result.set_failure(f"Failed to start app: {start_app_result.error_message}")
                return
            
            print(f"Start app result: {start_app_result.data}")
            result.add_detail("start_app_data", start_app_result.data)
            
            # Get first item from start_app_result.data and print cmdline, pid, pname
            if len(start_app_result.data) > 0:
                first_process = start_app_result.data[0]
                cmdline = getattr(first_process, 'cmdline', 'N/A')
                pid = getattr(first_process, 'pid', 'N/A')
                pname = getattr(first_process, 'pname', 'N/A')
                print(f"First process details - cmdline: {cmdline}, pid: {pid}, pname: {pname}")
                result.add_detail("first_process_details", {"cmdline": cmdline, "pid": pid, "pname": pname})
            
            # Wait for app to fully start
            time.sleep(3)
            
            # Verify app started by checking active window
            print("Step 2 Verification: Checking if app window became active...")
            active_window_result = self.session.computer.get_active_window()
            if not active_window_result.success:
                result.set_failure(f"Failed to get active window: {active_window_result.error_message}")
                return
            
            if active_window_result.window:
                active_window_id = str(active_window_result.window.window_id)
                active_window_title = getattr(active_window_result.window, 'title', 'Unknown')
                print(f"✅ Active window found: ID={active_window_id}, Title={active_window_title}")
                result.add_detail("active_window_after_start", {
                    "window_id": active_window_id, 
                    "title": active_window_title
                })
            else:
                print("⚠️ No active window found after starting app")
                result.add_detail("active_window_after_start", None)
            
            # Step 3: List visible apps and validate
            print("Step 3: Testing list_visible_apps functionality...")
            visible_apps_result = self.session.computer.list_visible_apps()
            if not visible_apps_result.success:
                result.set_failure(f"Failed to list visible apps: {visible_apps_result.error_message}")
                return
            
            # Validate success is True
            self.assertTrue(visible_apps_result.success, "list_visible_apps success should be True")
            print(f"Visible apps data: {visible_apps_result.data}")
            result.add_detail("visible_apps_data", visible_apps_result.data)
            # Find the started app process in visible apps list by matching PID
            target_process = None
            for process in visible_apps_result.data:
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
            print("Step 4: Testing stop_app_by_pid functionality...")
            stop_result = self.session.computer.stop_app_by_pid(target_pid)
            if not stop_result.success:
                result.set_failure(f"Failed to stop app by PID: {stop_result.error_message}")
                return
            
            # Validate success is True
            self.assertTrue(stop_result.success, "stop_app_by_pid success should be True")
            print(f"✅ App stopped successfully using PID: {target_pid}")
            result.add_detail("stop_app_success", True)
            
            # Wait for app to fully stop
            time.sleep(3)
            
            # Step 4 Verification: Verify app is no longer in visible apps
            print("Step 4 Verification: Checking if app is no longer visible...")
            final_visible_apps_result = self.session.computer.list_visible_apps()
            if final_visible_apps_result.success:
                app_still_visible = False
                for process in final_visible_apps_result.data:
                    if process.pid == target_pid:
                        app_still_visible = True
                        break
                
                if app_still_visible:
                    print(f"⚠️ App with PID {target_pid} is still visible after stop command")
                    result.add_detail("app_stop_verification", "still_visible")
                else:
                    print(f"✅ App with PID {target_pid} is no longer visible")
                    result.add_detail("app_stop_verification", "not_visible")
            else:
                print("⚠️ Could not verify app stop status due to list_visible_apps failure")
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
            print("Step 1: Testing get_installed_apps functionality...")
            installed_apps_result = self.session.computer.get_installed_apps()
            if not installed_apps_result.success:
                result.set_failure(f"Failed to get installed apps: {installed_apps_result.error_message}")
                return
            
            print(f"Installed apps data: {installed_apps_result.data}")
            result.add_detail("installed_apps_data", installed_apps_result.data)
            
            if len(installed_apps_result.data) == 0:
                result.set_failure("No installed apps found")
                print("❌ No installed apps found")
                return
            
            # Find Google Chrome app in the list
            first_app = None
            for app in installed_apps_result.data:
                if hasattr(app, 'name') and app.name == "Google Chrome":
                    first_app = app
                    break
            
            # If Google Chrome not found, use the first app as fallback
            if first_app is None:
                print("Google Chrome not found in installed apps, using first app as fallback")
                first_app = installed_apps_result.data[0]
            else:
                print(f"Found Google Chrome app: {first_app.name}")
                result.add_detail("selected_app_name", "Google Chrome")
            print(f"First app: {first_app}")
            start_cmd = first_app.start_cmd
            print(f"First app start_cmd: {start_cmd}")
            result.add_detail("first_app_start_cmd", start_cmd)
            
            # Step 2: Start app and validate success
            print("Step 2: Testing start_app functionality...")
            start_app_result = self.session.computer.start_app(start_cmd)
            if not start_app_result.success:
                result.set_failure(f"Failed to start app: {start_app_result.error_message}")
                return
            
            # Validate success is True
            self.assertTrue(start_app_result.success, "start_app success should be True")
            print(f"Start app result success: {start_app_result.success}")
            
            # Print data and check length > 0
            print(f"Start app data: {start_app_result.data}")
            result.add_detail("start_app_data", start_app_result.data)
            
            # Validate data length > 0
            self.assertGreater(len(start_app_result.data), 0, "start_app data length should be greater than 0")
            print(f"Start app data length: {len(start_app_result.data)}")
            result.add_detail("start_app_data_length", len(start_app_result.data))
            
            # Get first process details for cleanup later
            first_process = start_app_result.data[0]
            app_pname = getattr(first_process, 'pname', None)
            print(f"Started app process name: {app_pname}")
            result.add_detail("started_app_pname", app_pname)
            
            print("✅ Application management operations completed successfully")
            time.sleep(3)
            # Step 3: List root windows and get the first window_id
            print("Step 3: Testing list_root_windows functionality...")
            windows_result = self.session.computer.list_root_windows()
            if not windows_result.success:
                result.set_failure(f"Failed to list root windows: {windows_result.error_message}")
                return
            
            print(f"Windows found: {windows_result.windows}")
            result.add_detail("windows_list", [{"window_id": w.window_id, "title": w.title} for w in windows_result.windows])
            
            if len(windows_result.windows) == 0:
                result.set_failure("No windows found, skipping window operations test")
                print("⚠️ No windows found, skipping remaining window operations")
                return
            
            # Get the first window's ID
            target_window = windows_result.windows[0]
            window_id = target_window.window_id
            print(f"Using window ID: {window_id}, Title: {target_window.title}")
            result.add_detail("target_window_id", window_id)
            result.add_detail("target_window_title", target_window.title)
            
            # Step 4: Activate window
            print("Step 4: Testing activate_window functionality...")
            activate_result = self.session.computer.activate_window(window_id)
            if not activate_result.success or not activate_result.data:
                result.set_failure(f"Failed to activate window: {activate_result.error_message}")
                print(f"❌ Window activation failed: {activate_result.error_message}")
                return
            
            print(f"✅ Window {window_id} activated successfully")
            result.add_detail("activate_success", True)
            
            # Step 5: Verify window is active
            print("Step 5: Testing get_active_window functionality...")
            active_window_result = self.session.computer.get_active_window()
            if not active_window_result.success:
                result.set_failure(f"Failed to get active window: {active_window_result.error_message}")
                return
            
            if active_window_result.window and active_window_result.window.window_id == window_id:
                print(f"✅ Window {window_id} is correctly active")
                result.add_detail("active_window_verification", True)
            else:
                active_id = str(active_window_result.window.window_id) if active_window_result.window else "None"
                result.set_failure(f"Active window verification failed: expected {window_id}, got {active_id}")
                print(f"❌ Active window mismatch: expected {window_id}, got {active_id}")
                return
            
            # Step 6: Enable focus mode and get cursor position
            print("Step 6: Testing focus_mode and get_cursor_position functionality...")
            focus_result = self.session.computer.focus_mode(True)
            if not focus_result.success or not focus_result.data:
                result.set_failure(f"Failed to enable focus mode: {focus_result.error_message}")
                return
            
            print("✅ Focus mode enabled successfully")
            result.add_detail("focus_mode_success", True)
            
            cursor_result = self.session.computer.get_cursor_position()
            if not cursor_result.success:
                result.set_failure(f"Failed to get cursor position: {cursor_result.error_message}")
                return
            
            cursor_x, cursor_y = get_cursor_coordinates(cursor_result)
            print(f"Current cursor position: ({cursor_x}, {cursor_y})")
            result.add_detail("cursor_position", {"x": cursor_x, "y": cursor_y})
            
            # Step 7: Minimize window
            print("Step 7: Testing minimize_window functionality...")
            minimize_result = self.session.computer.minimize_window(window_id)
            if not minimize_result.success or not minimize_result.data:
                result.set_failure(f"Failed to minimize window: {minimize_result.error_message}")
                return
            
            print(f"✅ Window {window_id} minimized successfully")
            result.add_detail("minimize_success", True)
            time.sleep(3)
           
            # Step 8: Maximize window
            print("Step 8: Testing maximize_window functionality...")
            maximize_result = self.session.computer.maximize_window(window_id)
            if not maximize_result.success or not maximize_result.data:
                result.set_failure(f"Failed to maximize window: {maximize_result.error_message}")
                return
            
            print(f"✅ Window {window_id} maximized successfully")
            result.add_detail("maximize_success", True)
            time.sleep(3)
            # Step 9: Restore window
            print("Step 9: Testing restore_window functionality...")
            restore_result = self.session.computer.restore_window(window_id)
            if not restore_result.success or not restore_result.data:
                result.set_failure(f"Failed to restore window: {restore_result.error_message}")
                return
            
            print(f"✅ Window {window_id} restored successfully")
            result.add_detail("restore_success", True)
            time.sleep(3)
            
            # Step 10: Resize window
            print("Step 10: Testing resize_window functionality...")
            resize_result = self.session.computer.resize_window(window_id, 300, 500)
            if not resize_result.success or not resize_result.data:
                result.set_failure(f"Failed to resize window: {resize_result.error_message}")
                return
            
            print(f"✅ Window {window_id} resized to 300x500 successfully")
            result.add_detail("resize_success", True)
            time.sleep(3)
            
            # Step 11: Fullscreen window
            print("Step 11: Testing fullscreen_window functionality...")
            fullscreen_result = self.session.computer.fullscreen_window(window_id)
            if not fullscreen_result.success or not fullscreen_result.data:
                result.set_failure(f"Failed to fullscreen window: {fullscreen_result.error_message}")
                return
            
            print(f"✅ Window {window_id} set to fullscreen successfully")
            result.add_detail("fullscreen_success", True)
            time.sleep(3)
            
            # Step 12: Close window and verify it's no longer active
            print("Step 12: Testing close_window functionality...")
            close_result = self.session.computer.close_window(window_id)
            if not close_result.success or not close_result.data:
                result.set_failure(f"Failed to close window: {close_result.error_message}")
                return
            
            print(f"✅ Window {window_id} closed successfully")
            result.add_detail("close_success", True)
            time.sleep(3)
            #Step 13: Verify window is no longer active
            print("Step 13: Testing list_root_windows functionality...")
            final_windows_result = self.session.computer.list_root_windows()
            if final_windows_result.success:
                window_still_exists = False
                for window in final_windows_result.windows:
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
            else:
                print("❌ Failed to verify window closure")
                result.add_detail("close_verification", False)
            
            
            # All tests passed
            result.set_success("All window operations validation successful")
            print("✅ All window operations (list, activate, minimize, maximize, restore, resize, fullscreen, close) validated successfully")
            
            #Step 14: Cleanup: Stop the started application
            print("Step 14: Cleanup: Stopping started application...")
            if app_pname:
                print(f"Cleanup: Stopping application with process name: {app_pname}")
                stop_result = self.session.computer.stop_app_by_pname(app_pname)
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
            print("Step 1: Testing get_installed_apps functionality...")
            installed_apps_result = self.session.computer.get_installed_apps()
            if not installed_apps_result.success:
                result.set_failure(f"Failed to get installed apps: {installed_apps_result.error_message}")
                return
            
            # Validate data length > 0
            self.assertGreater(len(installed_apps_result.data), 0, "Installed apps data length should be greater than 0")
            print(f"Installed apps data: {installed_apps_result.data}")
            result.add_detail("installed_apps_data", installed_apps_result.data)
            
            # Find Google Chrome app in the list
            first_app = None
            for app in installed_apps_result.data:
                if hasattr(app, 'name') and app.name == "Google Chrome":
                    first_app = app
                    break
            
            # If Google Chrome not found, use the first app as fallback
            if first_app is None:
                print("Google Chrome not found in installed apps, using first app as fallback")
                first_app = installed_apps_result.data[0]
            else:
                print(f"Found Google Chrome app: {first_app.name}")
                result.add_detail("selected_app_name", "Google Chrome")
            start_cmd = first_app.start_cmd
            print(f"First app start_cmd: {start_cmd}")
            result.add_detail("first_app_start_cmd", start_cmd)
            
            # Step 2: Start app and validate success
            print("Step 2: Testing start_app functionality...")
            start_app_result = self.session.computer.start_app(start_cmd)
            if not start_app_result.success:
                result.set_failure(f"Failed to start app: {start_app_result.error_message}")
                return
            
            # Validate data length > 0
            self.assertGreater(len(start_app_result.data), 0, "Start app data length should be greater than 0")
            print(f"Start app data: {start_app_result.data}")
            result.add_detail("start_app_data", start_app_result.data)
            
            # Get first item from start_app_result.data and print cmdline, pid, pname
            first_process = start_app_result.data[0]
            cmdline = getattr(first_process, 'cmdline', 'N/A')
            pid = getattr(first_process, 'pid', 'N/A')
            pname = getattr(first_process, 'pname', 'N/A')
            print(f"First process details - cmdline: {cmdline}, pid: {pid}, pname: {pname}")
            result.add_detail("first_process_details", {"cmdline": cmdline, "pid": pid, "pname": pname})
            
            # Wait for app to fully start
            time.sleep(3)
            
            # Step 3: Get screen size and calculate center coordinates
            print("Step 3: Testing get_screen_size functionality...")
            # Use helper function to get screen center coordinates
            center_x, center_y = get_screen_center(self.session)
            result.add_detail("scroll_center_coordinates", {"x": center_x, "y": center_y})
            
            # Step 4: Get active window and window_id
            print("Step 4: Testing get_active_window functionality...")
            active_window_result = self.session.computer.get_active_window()
            if not active_window_result.success or not active_window_result.window:
                result.set_failure(f"Failed to get active window: {active_window_result.error_message}")
                return
            
            window_id = active_window_result.window.window_id
            print(f"Active window_id: {window_id}")
            result.add_detail("active_window_id", window_id)
            
            # Step 5: Maximize window
            print("Step 5: Testing maximize_window functionality...")
            maximize_result = self.session.computer.maximize_window(window_id)
            if not maximize_result.success or not maximize_result.data:
                result.set_failure(f"Failed to maximize window: {maximize_result.error_message}")
                return
            
            # Validate success and data are True
            self.assertTrue(maximize_result.success, "maximize_window success should be True")
            self.assertTrue(maximize_result.data, "maximize_window data should be True")
            print(f"✅ Window {window_id} maximized successfully")
            result.add_detail("maximize_success", True)
            
            # Wait for window to maximize
            time.sleep(2)
            
            # Step 6: Enable focus mode
            print("Step 6: Testing focus_mode functionality...")
            focus_result = self.session.computer.focus_mode(True)
            if not focus_result.success or not focus_result.data:
                result.set_failure(f"Failed to enable focus mode: {focus_result.error_message}")
                return
            
            # Validate success and data are True
            self.assertTrue(focus_result.success, "focus_mode success should be True")
            self.assertTrue(focus_result.data, "focus_mode data should be True")
            print("✅ Focus mode enabled successfully")
            result.add_detail("focus_mode_success", True)
            
            # Step 7: Perform scroll operation
            print("Step 7: Testing scroll functionality...")
            scroll_result = self.session.computer.scroll(center_x, center_y, ScrollDirection.DOWN, 3)
            if not scroll_result.success or not scroll_result.data:
                result.set_failure(f"Failed to perform scroll: {scroll_result.error_message}")
                return
            
            # Validate success and data are True
            self.assertTrue(scroll_result.success, "scroll success should be True")
            self.assertTrue(scroll_result.data, "scroll data should be True")
            print(f"✅ Scroll operation at ({center_x}, {center_y}) completed successfully")
            result.add_detail("scroll_success", True)
            
            # Wait for scroll to complete
            time.sleep(2)
            
            # Step 8: Stop app and validate termination
            print("Step 8: Testing stop_app_by_pname functionality...")
            stop_result = self.session.computer.stop_app_by_pname(pname)
            if not stop_result.success:
                result.set_failure(f"Failed to stop app: {stop_result.error_message}")
                return
            
            # Validate success is True
            self.assertTrue(stop_result.success, "stop_app_by_pid success should be True")
            print(f"✅ App stopped successfully using pname: {pname}")
            result.add_detail("stop_app_success", True)
            
            # Wait for app to fully stop
            time.sleep(3)
            
            # Verify app termination by checking if no visible apps remain
            print("Step 9 Verification: Checking if no visible apps remain after stopping...")
            final_visible_apps_result = self.session.computer.list_visible_apps()
            
            if final_visible_apps_result.success:
                visible_apps_count = len(final_visible_apps_result.data)
                if visible_apps_count == 0:
                    print("✅ No visible apps found after stopping app - termination successful")
                    result.add_detail("app_stop_verification", "no_visible_apps")
                else:
                    print(f"⚠️ {visible_apps_count} visible apps still found after stop command")
                    result.add_detail("app_stop_verification", f"{visible_apps_count}_apps_still_visible")
            else:
                print("❌ Failed to verify app termination due to list_visible_apps failure")
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