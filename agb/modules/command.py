from agb.api.base_service import BaseService
from agb.model.response import ApiResponse
from agb.logger import get_logger

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
            args = {"command": command, "timeout_ms": timeout_ms}

            result = self._call_mcp_tool("shell", args)
            logger.debug(f"Command executed response: {result}")

            if result.success:
                return CommandResult(
                    request_id=result.request_id,
                    success=True,
                    output=result.data,
                )
            else:
                return CommandResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to execute command",
                )
        except Exception as e:
            return CommandResult(
                request_id="",
                success=False,
                error_message=f"Failed to execute command: {e}",
            )
