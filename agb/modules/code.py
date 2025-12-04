from agb.api.base_service import BaseService
from agb.model.response import ApiResponse
from agb.logger import get_logger

logger = get_logger(__name__)


class CodeExecutionResult(ApiResponse):
    """Result of code execution operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        result: str = "",
        error_message: str = "",
    ):
        """
        Initialize a CodeExecutionResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
            success (bool, optional): Whether the operation was successful.
            result (str, optional): The execution result.
            error_message (str, optional): Error message if the operation failed.
        """
        super().__init__(request_id)
        self.success = success
        self.result = result
        self.error_message = error_message


class Code(BaseService):
    """
    Handles code execution operations in the AGB cloud environment.
    """

    def run_code(
        self, code: str, language: str, timeout_s: int = 60
    ) -> CodeExecutionResult:
        """
        Execute code in the specified language with a timeout.

        Args:
            code (str): The code to execute.
            language (str): The programming language of the code. Supported languages are:
                'python', 'javascript', 'java', 'r'.
            timeout_s (int): The timeout for the code execution in seconds. Default is 60s.

        Returns:
            CodeExecutionResult: Result object containing success status, execution
                result, and error message if any.

        Raises:
            CommandError: If the code execution fails or if an unsupported language is
                specified.
        """
        try:
            # Convert language to lowercase for consistent processing
            language = language.lower()

            # Validate language
            supported_languages = ["python", "javascript", "java", "r"]
            if language not in supported_languages:
                return CodeExecutionResult(
                    request_id="",
                    success=False,
                    error_message=f"Unsupported language: {language}. Supported "
                    f"languages are: {', '.join(supported_languages)}",
                )

            args = {"code": code, "language": language, "timeout_s": timeout_s}
            result = self._call_mcp_tool("run_code", args)
            logger.debug(f"Run code response: {result}")

            if result.success:
                return CodeExecutionResult(
                    request_id=result.request_id,
                    success=True,
                    result=result.data,
                )
            else:
                return CodeExecutionResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to run code",
                )
        except Exception as e:
            return CodeExecutionResult(
                request_id="",
                success=False,
                error_message=f"Failed to run code: {e}",
            )
