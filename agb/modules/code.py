from agb.api.base_service import BaseService
from agb.model.response import ApiResponse
from agb.logger import get_logger, log_operation_start, log_operation_success, log_operation_error

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
                error_msg = f"Unsupported language: {language}. Supported languages are: {', '.join(supported_languages)}"
                log_operation_error("Code.run_code", error_msg)
                return CodeExecutionResult(
                    request_id="",
                    success=False,
                    error_message=error_msg,
                )

            log_operation_start("Code.run_code", f"Language={language}, TimeoutS={timeout_s}, Code={code}")
            args = {"code": code, "language": language, "timeout_s": timeout_s}
            result = self._call_mcp_tool("run_code", args)
            logger.debug(f"Run code response: {result}")

            if result.success:
                result_msg = f"RequestId={result.request_id}, ResultLength={len(result.data) if result.data else 0}"
                log_operation_success("Code.run_code", result_msg)
                return CodeExecutionResult(
                    request_id=result.request_id,
                    success=True,
                    result=result.data,
                )
            else:
                error_msg = result.error_message or "Failed to run code"
                log_operation_error("Code.run_code", error_msg)
                return CodeExecutionResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("Code.run_code", str(e), exc_info=True)
            return CodeExecutionResult(
                request_id="",
                success=False,
                error_message=f"Failed to run code: {e}",
            )
