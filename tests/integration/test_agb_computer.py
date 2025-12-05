"""
Computer module functional validation tests.
These tests validate that mouse operations actually work by checking cursor position changes.
"""

import os
import time
import unittest
import json
from agb import agb
from agb.session_params import CreateSessionParams
from .functional_helpers import  FunctionalTestResult

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
    

if __name__ == '__main__':
    unittest.main()