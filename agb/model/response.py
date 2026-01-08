"""
API response models for AGB SDK.
"""

from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from agb.session import Session


class ApiResponse:
    """Base class for all API responses, containing RequestID"""

    def __init__(self, request_id: str = ""):
        """
        Initialize an ApiResponse with a request_id.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
        """
        self.request_id = request_id

    def get_request_id(self) -> str:
        """
        Returns the unique identifier for the API request.

        Returns:
            str: The request ID.
        """
        return self.request_id


class SessionResult(ApiResponse):
    """Result of operations returning a single Session."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
        session: Optional["Session"] = None,
    ):
        """
        Initialize a SessionResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            session (Optional[Session], optional): The session object. Defaults to None.
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message
        self.session = session


class DeleteResult(ApiResponse):
    """Result of delete operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
    ):
        """
        Initialize a DeleteResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the delete operation was successful.
                Defaults to False.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message


class OperationResult(ApiResponse):
    """Result of general operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        data: Any = None,
        error_message: str = "",
    ):
        """
        Initialize an OperationResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            data (Any, optional): Data returned by the operation. Defaults to None.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.data = data
        self.error_message = error_message


class BoolResult(ApiResponse):
    """Result of operations returning a boolean value."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        data: Optional[bool] = None,
        error_message: str = "",
    ):
        """
        Initialize a BoolResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            data (Optional[bool], optional): The boolean result. Defaults to None.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.data = data
        self.error_message = error_message


class GetSessionData:
    """Data returned by GetSession API."""

    def __init__(
        self,
        app_instance_id: str = "",
        resource_id: str = "",
        session_id: str = "",
        success: bool = False,
        resource_url: str = "",
        status: str = "",
    ):
        """
        Initialize GetSessionData.

        Args:
            app_instance_id (str): Application instance ID.
            resource_id (str): Resource ID.
            session_id (str): Session ID.
            success (bool): Success status.
            resource_url (str): Resource URL for accessing the session.
            status (str): Status of the session.
        """
        self.app_instance_id = app_instance_id
        self.resource_id = resource_id
        self.session_id = session_id
        self.success = success
        self.resource_url = resource_url
        self.status = status


class GetSessionResult(ApiResponse):
    """Result of GetSession operations."""

    def __init__(
        self,
        request_id: str = "",
        http_status_code: int = 0,
        code: str = "",
        success: bool = False,
        data: Optional[GetSessionData] = None,
        error_message: str = "",
    ):
        """
        Initialize a GetSessionResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            http_status_code (int, optional): HTTP status code. Defaults to 0.
            code (str, optional): Response code. Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            data (Optional[GetSessionData], optional): Session data. Defaults to None.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.http_status_code = http_status_code
        self.code = code
        self.success = success
        self.data = data
        self.error_message = error_message


class SessionListResult(ApiResponse):
    """Result of operations returning a list of Sessions."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
        session_ids: Optional[List[str]] = None,
        next_token: str = "",
        max_results: int = 0,
        total_count: int = 0,
    ):
        """
        Initialize a SessionListResult.

        Args:
            request_id (str): The request ID.
            success (bool): Whether the operation was successful.
            error_message (str): Error message if the operation failed.
            session_ids (Optional[List[str]]): List of session IDs.
            next_token (str): Token for the next page of results.
            max_results (int): Number of results per page.
            total_count (int): Total number of results available.
        """
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message
        self.session_ids = session_ids if session_ids is not None else []
        self.next_token = next_token
        self.max_results = max_results
        self.total_count = total_count


class WindowInfoResult(ApiResponse):
    """Result of window info operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        window: Any = None,
        error_message: str = "",
    ):
        super().__init__(request_id)
        self.success = success
        self.window = window
        self.error_message = error_message


class AppOperationResult(ApiResponse):
    """Result of application operations like start/stop."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
    ):
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message


class ProcessListResult(ApiResponse):
    """Result of operations returning a list of Processes."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        data: Optional[List[Any]] = None,
        error_message: str = "",
    ):
        super().__init__(request_id)
        self.success = success
        self.data = data if data is not None else []
        self.error_message = error_message


class InstalledAppListResult(ApiResponse):
    """Result of operations returning a list of InstalledApps."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        data: Optional[List[Any]] = None,
        error_message: str = "",
    ):
        super().__init__(request_id)
        self.success = success
        self.data = data if data is not None else []
        self.error_message = error_message


class WindowListResult(ApiResponse):
    """Result of window listing operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        windows: Optional[List[Any]] = None,
        error_message: str = "",
    ):
        super().__init__(request_id)
        self.success = success
        self.windows = windows or []
        self.error_message = error_message


class UploadResult:
    """Result of file upload operations."""

    def __init__(
        self,
        success: bool = False,
        request_id_upload_url: Optional[str] = None,
        request_id_sync: Optional[str] = None,
        http_status: Optional[int] = None,
        etag: Optional[str] = None,
        bytes_sent: int = 0,
        path: str = "",
        error_message: Optional[str] = None,
    ):
        """
        Initialize an UploadResult.

        Args:
            success (bool): Whether the upload was successful.
            request_id_upload_url (Optional[str]): Request ID for upload URL request.
            request_id_sync (Optional[str]): Request ID for sync request.
            http_status (Optional[int]): HTTP status code from upload.
            etag (Optional[str]): ETag from upload response.
            bytes_sent (int): Number of bytes sent.
            path (str): Remote path where file was uploaded.
            error_message (Optional[str]): Error message if upload failed.
        """
        self.success = success
        self.request_id_upload_url = request_id_upload_url
        self.request_id_sync = request_id_sync
        self.http_status = http_status
        self.etag = etag
        self.bytes_sent = bytes_sent
        self.path = path
        self.error_message = error_message


class DownloadResult:
    """Result of file download operations."""

    def __init__(
        self,
        success: bool = False,
        request_id_download_url: Optional[str] = None,
        request_id_sync: Optional[str] = None,
        http_status: Optional[int] = None,
        bytes_received: int = 0,
        path: str = "",
        local_path: str = "",
        error_message: Optional[str] = None,
    ):
        """
        Initialize a DownloadResult.

        Args:
            success (bool): Whether the download was successful.
            request_id_download_url (Optional[str]): Request ID for download URL request.
            request_id_sync (Optional[str]): Request ID for sync request.
            http_status (Optional[int]): HTTP status code from download.
            bytes_received (int): Number of bytes received.
            path (str): Remote path where file was downloaded from.
            local_path (str): Local path where file was saved.
            error_message (Optional[str]): Error message if download failed.
        """
        self.success = success
        self.request_id_download_url = request_id_download_url
        self.request_id_sync = request_id_sync
        self.http_status = http_status
        self.bytes_received = bytes_received
        self.path = path
        self.local_path = local_path
        self.error_message = error_message


class ExecutionResult:
    """Code execution result item"""

    def __init__(
        self,
        text: Optional[str] = None,
        html: Optional[str] = None,
        markdown: Optional[str] = None,
        png: Optional[str] = None,
        jpeg: Optional[str] = None,
        svg: Optional[str] = None,
        json: Optional[Any] = None,
        latex: Optional[str] = None,
        chart: Optional[Any] = None,
        is_main_result: bool = False,
    ):
        """
        Initialize an ExecutionResult.

        Args:
            text (Optional[str]): Plain text output
            html (Optional[str]): HTML output
            markdown (Optional[str]): Markdown output
            png (Optional[str]): PNG image data
            jpeg (Optional[str]): JPEG image data
            svg (Optional[str]): SVG image data
            json (Optional[Any]): JSON data
            latex (Optional[str]): LaTeX output
            chart (Optional[Any]): Chart data
            is_main_result (bool): Whether this is the main result
        """
        self.text = text
        self.html = html
        self.markdown = markdown
        self.png = png
        self.jpeg = jpeg
        self.svg = svg
        self.json = json
        self.latex = latex
        self.chart = chart
        self.is_main_result = is_main_result


class ExecutionLogs:
    """Execution logs"""

    def __init__(
        self, stdout: Optional[List[str]] = None, stderr: Optional[List[str]] = None
    ):
        """
        Initialize ExecutionLogs.

        Args:
            stdout (Optional[List[str]]): Standard output logs
            stderr (Optional[List[str]]): Standard error logs
        """
        self.stdout = stdout or []
        self.stderr = stderr or []

class BinaryFileContentResult(ApiResponse):
    """Result of binary file read operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        content: bytes = b"",
        error_message: str = "",
        size: Optional[int] = None,
    ):
        """
        Initialize a BinaryFileContentResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            content (bytes, optional): Binary file content. Defaults to b"".
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
            size (int, optional): Size of the file in bytes. Defaults to None.
        """
        super().__init__(request_id)
        self.success = success
        self.content = content
        self.error_message = error_message
        self.size = size

class EnhancedCodeExecutionResult(ApiResponse):
    """Enhanced code execution result"""

    def __init__(
        self,
        request_id: str = "",
        execution_count: Optional[int] = None,
        execution_time: float = 0.0,
        logs: Optional[ExecutionLogs] = None,
        results: Optional[List[ExecutionResult]] = None,
        error_message: str = "",
        success: bool = True,
    ):
        """
        Initialize an EnhancedCodeExecutionResult.

        Args:
            request_id (str): Request ID
            execution_count (Optional[int]): Execution count
            execution_time (float): Execution time in seconds
            logs (Optional[ExecutionLogs]): Execution logs
            results (Optional[List[ExecutionResult]]): Execution results
            error_message (str): Error message if any
            success (bool): Whether execution was successful
        """
        super().__init__(request_id)
        self.execution_count = execution_count
        self.execution_time = execution_time
        self.logs = logs or ExecutionLogs()
        self.results = results or []
        self.error_message = error_message or ""
        self.success = success


class SessionStatusResult(ApiResponse):
    """Result of Session.get_status() (status only)."""

    def __init__(
        self,
        request_id: str = "",
        http_status_code: int = 0,
        code: str = "",
        success: bool = False,
        status: str = "",
        error_message: str = "",
    ):
        super().__init__(request_id)
        self.http_status_code = http_status_code
        self.code = code
        self.success = success
        self.status = status
        self.error_message = error_message
