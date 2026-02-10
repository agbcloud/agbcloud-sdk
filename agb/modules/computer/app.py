"""
Application manager for computer automation operations.
"""

import json
from typing import List, Optional

from agb.api.base_service import BaseService
from agb.model.response import AppOperationResult, ProcessListResult, InstalledAppListResult
from agb.logger import get_logger, log_operation_start, log_operation_success, log_operation_error
from agb.modules.computer import InstalledApp, Process

logger = get_logger(__name__)


class ApplicationManager(BaseService):
    """Manager for application operations."""

    def start(self, start_cmd: str, work_directory: str = "", activity: str = "") -> ProcessListResult:
        """
        Starts the specified application.

        Args:
            start_cmd (str): The command to start the application (executable name or full path, may include arguments).
            work_directory (str, optional): Working directory for the application. Defaults to "".
            activity (str, optional): Activity name to launch (for mobile apps). Defaults to "".

        Returns:
            ProcessListResult: Result object containing list of processes started and error message if any.

        Note:
            - The start_cmd can be an executable name or full path
            - work_directory is optional and defaults to the system default
            - activity parameter is for mobile apps (Android)
            - Returns process information for all started processes
        """
        op_details = f"StartCmd={start_cmd}"
        if work_directory:
            op_details += f", WorkDirectory={work_directory}"
        if activity:
            op_details += f", Activity={activity}"
        log_operation_start("ApplicationManager.start", op_details)

        try:
            args_dict = {"start_cmd": start_cmd}
            if work_directory:
                args_dict["work_directory"] = work_directory
            if activity:
                args_dict["activity"] = activity

            result = self._call_mcp_tool("start_app", args_dict)
            logger.debug(f"Start app response: {result}")

            if not result.success:
                error_msg = result.error_message or "Failed to start app"
                log_operation_error("ApplicationManager.start", error_msg)
                return ProcessListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )

            try:
                processes_json = json.loads(result.data)
                processes = []

                for process_data in processes_json:
                    process = Process._from_dict(process_data)
                    processes.append(process)

                result_msg = f"StartCmd={start_cmd}, ProcessesCount={len(processes)}, RequestId={result.request_id}"
                log_operation_success("ApplicationManager.start", result_msg)
                return ProcessListResult(
                    request_id=result.request_id,
                    success=True,
                    data=processes
                )
            except json.JSONDecodeError as e:
                log_operation_error("ApplicationManager.start", f"Failed to parse processes JSON: {str(e)}", exc_info=True)
                return ProcessListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=f"Failed to parse processes JSON: {e}",
                )
        except Exception as e:
            log_operation_error("ApplicationManager.start", str(e), exc_info=True)
            return ProcessListResult(
                success=False,
                error_message=f"Failed to start app: {e}"
            )

    def stop_by_pname(self, pname: str) -> AppOperationResult:
        """
        Stops an application by process name.

        Args:
            pname (str): The process name of the application to stop.

        Returns:
            AppOperationResult: Result object containing success status and error message if any.

        Note:
            - The process name should match exactly (case-sensitive on some systems)
            - This will stop all processes matching the given name
            - If multiple instances are running, all will be terminated
            - The .exe extension may be required on Windows
        """
        log_operation_start("ApplicationManager.stop_by_pname", f"PName={pname}")
        try:
            args = {"pname": pname}
            result = self._call_mcp_tool("stop_app_by_pname", args)
            logger.debug(f"Stop app by pname response: {result}")

            if result.success:
                result_msg = f"PName={pname}, RequestId={result.request_id}"
                log_operation_success("ApplicationManager.stop_by_pname", result_msg)
            else:
                error_msg = result.error_message or "Failed to stop app by pname"
                log_operation_error("ApplicationManager.stop_by_pname", error_msg)

            return AppOperationResult(
                request_id=result.request_id,
                success=result.success,
                error_message=result.error_message or ("Failed to stop app by pname" if not result.success else ""),
            )
        except Exception as e:
            log_operation_error("ApplicationManager.stop_by_pname", str(e), exc_info=True)
            return AppOperationResult(
                request_id="",
                success=False,
                error_message=f"Failed to stop app by pname: {e}"
            )

    def stop_by_pid(self, pid: int) -> AppOperationResult:
        """
        Stops an application by process ID.

        Args:
            pid (int): The process ID of the application to stop.

        Returns:
            AppOperationResult: Result object containing success status and error message if any.

        Note:
            - PID must be a valid process ID
            - More precise than stopping by name (only stops specific process)
            - The process must be owned by the session or have appropriate permissions
            - PID can be obtained from start() or visible()
        """
        log_operation_start("ApplicationManager.stop_by_pid", f"PID={pid}")
        try:
            args = {"pid": pid}
            result = self._call_mcp_tool("stop_app_by_pid", args)
            logger.debug(f"Stop app by pid response: {result}")

            if result.success:
                result_msg = f"PID={pid}, RequestId={result.request_id}"
                log_operation_success("ApplicationManager.stop_by_pid", result_msg)
            else:
                error_msg = result.error_message or "Failed to stop app by pid"
                log_operation_error("ApplicationManager.stop_by_pid", error_msg)

            return AppOperationResult(
                request_id=result.request_id,
                success=result.success,
                error_message=result.error_message or ("Failed to stop app by pid" if not result.success else ""),
            )
        except Exception as e:
            log_operation_error("ApplicationManager.stop_by_pid", str(e), exc_info=True)
            return AppOperationResult(
                request_id="",
                success=False,
                error_message=f"Failed to stop app by pid: {e}"
            )

    def stop_by_cmd(self, stop_cmd: str) -> AppOperationResult:
        """
        Stops an application by executing a shell command (e.g. kill by PID).

        Args:
            stop_cmd (str): A shell command to stop/kill the process, e.g. "kill -9 1234"
                where 1234 is the process ID. Get the PID from app.start() or app.get_visible().
                This is NOT the stop_cmd field from list_installed (that field may be absent).

        Returns:
            AppOperationResult: Result object containing success status and error message if any.
        """
        log_operation_start("ApplicationManager.stop_by_cmd", f"StopCmd={stop_cmd}")
        try:
            args = {"stop_cmd": stop_cmd}
            result = self._call_mcp_tool("stop_app_by_cmd", args)
            logger.debug(f"Stop app by cmd response: {result}")

            if result.success:
                result_msg = f"StopCmd={stop_cmd}, RequestId={result.request_id}"
                log_operation_success("ApplicationManager.stop_by_cmd", result_msg)
            else:
                error_msg = result.error_message or "Failed to stop app by cmd"
                log_operation_error("ApplicationManager.stop_by_cmd", error_msg)

            return AppOperationResult(
                request_id=result.request_id,
                success=result.success,
                error_message=result.error_message or ("Failed to stop app by cmd" if not result.success else ""),
            )
        except Exception as e:
            log_operation_error("ApplicationManager.stop_by_cmd", str(e), exc_info=True)
            return AppOperationResult(
                request_id="",
                success=False,
                error_message=f"Failed to stop app by cmd: {e}"
            )

    def list_installed(
        self,
        start_menu: bool = True,
        desktop: bool = False,
        ignore_system_apps: bool = True,
    ) -> InstalledAppListResult:
        """
        Gets the list of installed applications.

        Args:
            start_menu (bool, optional): Whether to include start menu applications. Defaults to True.
            desktop (bool, optional): Whether to include desktop applications. Defaults to False.
            ignore_system_apps (bool, optional): Whether to ignore system applications. Defaults to True.

        Returns:
            InstalledAppListResult: Result object containing list of installed apps and error message if any.

        Note:
            - start_menu parameter includes applications from Start Menu
            - desktop parameter includes shortcuts from Desktop
            - ignore_system_apps parameter filters out system applications
            - Each app object contains name, start_cmd, and optionally work_directory
        """
        try:
            args = {
                "start_menu": start_menu,
                "desktop": desktop,
                "ignore_system_apps": ignore_system_apps,
            }

            result = self._call_mcp_tool("get_installed_apps", args)
            logger.debug(f"Get installed apps response: {result}")

            if not result.success:
                return InstalledAppListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to get installed apps",
                )

            try:
                apps_json = json.loads(result.data)
                installed_apps = []

                for app_data in apps_json:
                    app = InstalledApp._from_dict(app_data)
                    installed_apps.append(app)

                return InstalledAppListResult(
                    request_id=result.request_id,
                    success=True,
                    data=installed_apps,
                )
            except json.JSONDecodeError as e:
                return InstalledAppListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=f"Failed to parse applications JSON: {e}",
                )
        except Exception as e:
            return InstalledAppListResult(
                success=False,
                error_message=f"Failed to get installed apps: {e}"
            )

    def get_visible(self) -> ProcessListResult:
        """
        Lists all applications with visible windows.

        Returns detailed process information for applications that have visible windows,
        including process ID, name, command line, and other system information.
        This is useful for system monitoring and process management tasks.

        Returns:
            ProcessListResult: Result object containing list of visible applications
                with detailed process information.

        Note:
            - Only returns applications with visible windows
            - Hidden or minimized windows may not appear
            - Useful for monitoring currently active applications
            - Process information includes PID, name, and command line
        """
        try:
            result = self._call_mcp_tool("list_visible_apps", {})
            logger.debug(f"List visible apps response: {result}")

            if not result.success:
                return ProcessListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to list visible apps",
                )

            try:
                processes_json = json.loads(result.data)
                processes = []

                for process_data in processes_json:
                    process = Process._from_dict(process_data)
                    processes.append(process)

                return ProcessListResult(
                    request_id=result.request_id,
                    success=True,
                    data=processes
                )
            except json.JSONDecodeError as e:
                return ProcessListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=f"Failed to parse processes JSON: {e}",
                )
        except Exception as e:
            return ProcessListResult(
                success=False,
                error_message=f"Failed to list visible apps: {e}"
            )
