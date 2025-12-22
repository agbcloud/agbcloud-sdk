from agb.api.base_service import BaseService
from agb.model.response import ApiResponse
from agb.logger import get_logger, log_operation_start, log_operation_success, log_operation_error

logger = get_logger(__name__)


class CommandResult(ApiResponse):
    """Result of command execution operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        output: str = "",
        error_message: str = "",
    ):
        """
        Initialize a CommandResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
            success (bool, optional): Whether the operation was successful.
            output (str, optional): The command output.
            error_message (str, optional): Error message if the operation failed.
        """
        super().__init__(request_id)
        self.success = success
        self.output = output
        self.error_message = error_message


class Command(BaseService):
    """
    Handles command execution operations in the AGB cloud environment.
    """

    def execute_command(self, command: str, timeout_ms: int = 1000) -> CommandResult:
        """
        Execute a command in the cloud environment with a specified timeout.

        Args:
            command (str): The command to execute.
            timeout_ms (int): The timeout for the command execution in milliseconds. Defaults to 1000.

        Returns:
            CommandResult: Result object containing success status, command output,
                and error message if any.
        """
        try:
            log_operation_start("Command.execute_command", f"Command={command}, TimeoutMs={timeout_ms}")
            args = {"command": command, "timeout_ms": timeout_ms}

            result = self._call_mcp_tool("shell", args)
            logger.debug(f"Command executed response: {result}")

            if result.success:
                result_msg = f"RequestId={result.request_id}, OutputLength={len(result.data) if result.data else 0}"
                log_operation_success("Command.execute_command", result_msg)
                return CommandResult(
                    request_id=result.request_id,
                    success=True,
                    output=result.data,
                )
            else:
                error_msg = result.error_message or "Failed to execute command"
                log_operation_error("Command.execute_command", error_msg)
                return CommandResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("Command.execute_command", str(e), exc_info=True)
            return CommandResult(
                request_id="",
                success=False,
                error_message=f"Failed to execute command: {e}",
            )
