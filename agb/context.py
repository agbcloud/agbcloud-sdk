from typing import TYPE_CHECKING, List, Optional

from agb.api.models import (
    DeleteContextRequest,
    GetContextRequest,
    ListContextsRequest,
    ModifyContextRequest,
    DescribeContextFilesRequest,
    GetContextFileDownloadUrlRequest,
    GetContextFileUploadUrlRequest,
    DeleteContextFileRequest,
    ClearContextRequest,
)
from agb.model.response import ApiResponse, OperationResult
from agb.exceptions import ClearanceTimeoutError, AGBError
from .logger import get_logger, log_operation_start, log_operation_success, log_operation_error
import json
import time

# Initialize logger for this module
logger = get_logger("context")

if TYPE_CHECKING:
    from agb.agb import AGB


class Context:
    """
    Represents a persistent storage context in the AGB cloud environment.

    Attributes:
        id (str): The unique identifier of the context.
        name (str): The name of the context.
        created_at (str): Date and time when the Context was created.
        last_used_at (str): Date and time when the Context was last used.
    """

    def __init__(
        self,
        id: str,
        name: str,
        created_at: Optional[str] = None,
        last_used_at: Optional[str] = None,
    ):
        """
        Initialize a Context object.

        Args:
            id (str): The unique identifier of the context.
            name (str): The name of the context.
            created_at (Optional[str], optional): Date and time when the Context was
                created. Defaults to None.
            last_used_at (Optional[str], optional): Date and time when the Context was
                last used. Defaults to None.
        """
        self.id = id
        self.name = name
        self.created_at = created_at
        self.last_used_at = last_used_at


class ContextResult(ApiResponse):
    """Result of operations returning a Context."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        context_id: str = "",
        context: Optional[Context] = None,
        error_message: Optional[str] = None,
    ):
        """
        Initialize a ContextResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
            success (bool, optional): Whether the operation was successful.
            context_id (str, optional): The unique identifier of the context.
            context (Optional[Context], optional): The Context object.
        """
        super().__init__(request_id)
        self.success = success
        self.context_id = context_id
        self.context = context
        self.error_message = error_message


class ContextListResult(ApiResponse):
    """Result of operations returning a list of Contexts."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        contexts: Optional[List[Context]] = None,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
        total_count: Optional[int] = None,
        error_message: Optional[str] = None,
    ):
        """
        Initialize a ContextListResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
            success (bool, optional): Whether the operation was successful.
            contexts (Optional[List[Context]], optional): The list of context objects.
            next_token (Optional[str], optional): Token for the next page of results.
            max_results (Optional[int], optional): Maximum number of results per page.
            total_count (Optional[int], optional): Total number of contexts available.
        """
        super().__init__(request_id)
        self.success = success
        self.contexts = contexts if contexts is not None else []
        self.next_token = next_token
        self.max_results = max_results
        self.total_count = total_count
        self.error_message = error_message


class ContextFileEntry:
    """Represents a file item in a context."""

    def __init__(
        self,
        file_id: str,
        file_name: str,
        file_path: str,
        file_type: Optional[str] = None,
        gmt_create: Optional[str] = None,
        gmt_modified: Optional[str] = None,
        size: Optional[int] = None,
        status: Optional[str] = None,
    ):
        self.file_id = file_id
        self.file_name = file_name
        self.file_path = file_path
        self.file_type = file_type
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.size = size
        self.status = status


class FileUrlResult(ApiResponse):
    """Result of a presigned URL request."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        url: str = "",
        expire_time: Optional[int] = None,
        error_message: Optional[str] = None,
    ):
        super().__init__(request_id)
        self.success = success
        self.url = url
        self.expire_time = expire_time
        self.error_message = error_message


class ContextFileListResult(ApiResponse):
    """Result of file listing operation."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        entries: Optional[List[ContextFileEntry]] = None,
        count: Optional[int] = None,
        error_message: Optional[str] = None,
    ):
        super().__init__(request_id)
        self.success = success
        self.entries = entries or []
        self.count = count
        self.error_message = error_message


class ContextListParams:
    """Parameters for listing contexts with pagination support."""

    def __init__(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ):
        """
        Initialize ContextListParams.

        Args:
            max_results (Optional[int], optional): Maximum number of results per page.
                Defaults to 10 if not specified.
            next_token (Optional[str], optional): Token for the next page of results.
        """
        self.max_results = max_results
        self.next_token = next_token

class ClearContextResult(OperationResult):
    """
    Result of context clear operations, including the real-time status.

    Attributes:
        request_id (str): Unique identifier for the API request.
        success (bool): Whether the operation was successful.
        error_message (str): Error message if the operation failed.
        status (Optional[str]): Current status of the clearing task. This corresponds to the
            context's state field. Possible values:
            - "clearing": Context data is being cleared (in progress)
            - "available": Clearing completed successfully
        context_id (Optional[str]): The unique identifier of the context being cleared.
    """

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
        status: Optional[str] = None,
        context_id: Optional[str] = None,
    ):
        super().__init__(request_id, success, None, error_message)
        self.status = status
        self.context_id = context_id

class ContextService:
    """
    Provides methods to manage persistent contexts in the AGB cloud environment.
    """

    def __init__(self, agb: "AGB"):
        """
        Initialize the ContextService.

        Args:
            agb (AGB): The AGB instance.
        """
        self.agb = agb

    def list(self, params: Optional[ContextListParams] = None) -> ContextListResult:
        """
        Lists all available contexts with pagination support.

        Args:
            params (Optional[ContextListParams], optional): Parameters for listing contexts.
                If None, defaults will be used.

        Returns:
            ContextListResult: A result object containing the list of Context objects,
                pagination information, and request ID.
        """
        try:
            if params is None:
                params = ContextListParams()
            max_results = params.max_results if params.max_results is not None else 10
            request_details = f"MaxResults={max_results}"
            if params.next_token:
                request_details += f", NextToken={params.next_token}"
            log_operation_start("ContextService.list", request_details)
            request = ListContextsRequest(
                authorization=f"Bearer {self.agb.api_key}",
                max_results=max_results,
                next_token=params.next_token,
            )
            response = self.agb.client.list_contexts(request)

            request_id = response.request_id

            if not response.is_successful():
                error_msg = response.get_error_message()
                log_operation_error("ContextService.list", error_msg or "Unknown error")
                return ContextListResult(
                    request_id=request_id or "",
                    success=False,
                    contexts=[],
                    error_message=error_msg
                )

            try:
                contexts = []
                response_data = response.get_contexts_data()
                if response_data and isinstance(response_data, list):
                    for context_data in response_data:
                        context = Context(
                            id=context_data.id or "",
                            name=context_data.name or "",
                            created_at=context_data.create_time,
                            last_used_at=context_data.last_used_time,
                        )
                        contexts.append(context)

                # Get pagination metadata from response
                next_token = response.get_next_token()
                max_results_actual = response.get_max_results() or max_results
                total_count = response.get_total_count()

                result_msg = f"Found {len(contexts)} contexts, TotalCount={total_count}"
                log_operation_success("ContextService.list", result_msg)
                return ContextListResult(
                    request_id=request_id or "",
                    success=True,
                    contexts=contexts,
                    next_token=next_token,
                    max_results=max_results_actual,
                    total_count=total_count,
                )
            except Exception as e:
                log_operation_error("parse ListContexts response", str(e))
                return ContextListResult(
                    request_id=request_id or "", success=False, contexts=[], error_message=str(e)
                )
        except Exception as e:
            log_operation_error("ListContexts", str(e))
            return ContextListResult(
                request_id="",
                success=False,
                contexts=[],
                next_token=None,
                max_results=None,
                total_count=None,
                error_message=str(e)
            )

    def get(
        self,
        name: Optional[str] = None,
        create: bool = False,
        login_region_id: Optional[str] = None,
        context_id: Optional[str] = None,
    ) -> ContextResult:
        """
        Gets a context by ID or name. Optionally creates it if it doesn't exist.

        Args:
            name (Optional[str]): The name of the context to get. Either name or context_id must be provided.
            create (bool, optional): Whether to create the context if it doesn't exist.
                If True, context_id cannot be provided (only name is allowed). Defaults to False.
            login_region_id (Optional[str], optional): Login region ID for the request.
                If None or empty, defaults to Hangzhou region (cn-hangzhou).
            context_id (Optional[str]): The ID of the context to get. Either name or context_id must be provided.
                This parameter is placed last for backward compatibility.

        Returns:
            ContextResult: The ContextResult object containing the Context and request ID.

        Raises:
            ValueError: If validation fails (both name and context_id are None, or
                context_id is provided when create is True).
        """
        # Store original values for error messages
        original_context_id = context_id
        original_name = name

        try:
            # Normalize empty strings to None
            name = name.strip() if name and name.strip() else None
            context_id = context_id.strip() if context_id and context_id.strip() else None

            # Validation: ID and Name must be provided (at least one)
            if not context_id and not name:
                error_msg = "Either context_id or name must be provided (cannot both be empty)"
                log_operation_error("ContextService.get", error_msg)
                return ContextResult(
                    success=False,
                    error_message=error_msg,
                    request_id=""
                )

            # Validation: If AllowCreate is True, ID cannot be provided
            if create and context_id:
                error_msg = "context_id cannot be provided when create=True (only name is allowed when creating)"
                log_operation_error("ContextService.get", error_msg)
                return ContextResult(
                    success=False,
                    error_message=error_msg,
                    request_id=""
                )

            # Prepare operation details for logging
            op_details = f"Name={name or 'None'}, ContextId={context_id or 'None'}, Create={create}"
            if login_region_id:
                op_details += f", LoginRegionId={login_region_id}"
            log_operation_start("ContextService.get", op_details)

            # Note: If login_region_id is None or empty, the server will default to Hangzhou region (cn-hangzhou)
            request = GetContextRequest(
                id=context_id,
                name=name,
                allow_create=create,
                login_region_id=login_region_id,  # None means use default region (cn-hangzhou)
                authorization=f"Bearer {self.agb.api_key}",
            )
            response = self.agb.client.get_context(request)

            request_id = response.request_id

            if not response.is_successful():
                error_msg = response.get_error_message()
                log_operation_error("ContextService.get", error_msg or "Unknown error")
                return ContextResult(
                    request_id=request_id or "",
                    success=False,
                    context_id="",
                    context=None,
                    error_message=error_msg
                )

            try:
                data = response.get_context_data()
                result_context_id = data.id or context_id or ""
                context = Context(
                    id=result_context_id,
                    name=data.name or name or "",
                    created_at=data.create_time,
                    last_used_at=data.last_used_time,
                )
                result_msg = f"ContextId={result_context_id}, Name={context.name}"
                log_operation_success("ContextService.get", result_msg)
                return ContextResult(
                    request_id=request_id or "",
                    success=True,
                    context_id=result_context_id,
                    context=context,
                )
            except Exception as e:
                log_operation_error("parse GetContext response", str(e))
                return ContextResult(
                    request_id=request_id or "",
                    success=False,
                    context_id="",
                    context=None,
                    error_message=f"Failed to parse response: {str(e)}"
                )
        except Exception as e:
            log_operation_error("GetContext", str(e))
            context_identifier = original_context_id or original_name or "unknown"
            return ContextResult(
                request_id="",
                success=False,
                context_id="",
                context=None,
                error_message=f"Failed to get context {context_identifier}: {e}"
            )

    def create(self, name: str) -> ContextResult:
        """
        Creates a new context with the given name.

        Args:
            name (str): The name for the new context.

        Returns:
            ContextResult: The created ContextResult object with request ID.
        """
        # Validate required parameter
        if not name or (isinstance(name, str) and not name.strip()):
            error_msg = "name cannot be empty or None"
            logger.error(error_msg)
            return ContextResult(
                success=False,
                error_message=error_msg,
                request_id=""
            )
        return self.get(name.strip(), create=True)

    def update(self, context: Context) -> OperationResult:
        """
        Updates the specified context.

        Args:
            context (Context): The Context object to update.

        Returns:
            OperationResult: Result object containing success status and request ID.
        """
        if context is None:
            log_operation_error("ContextService.update", "context cannot be None")
            return OperationResult(
                request_id="",
                success=False,
                error_message="context cannot be None",
            )
        # Validate context.id
        if not context.id or (isinstance(context.id, str) and not context.id.strip()):
            error_msg = "context.id cannot be empty or None"
            log_operation_error("ContextService.update", error_msg)
            return OperationResult(
                request_id="",
                success=False,
                error_message=error_msg
            )

        # Validate context.name
        if not context.name or (isinstance(context.name, str) and not context.name.strip()):
            error_msg = "context.name cannot be empty or None"
            log_operation_error("ContextService.update", error_msg)
            return OperationResult(
                request_id="",
                success=False,
                error_message=error_msg
            )

        try:
            context_id = context.id.strip() if isinstance(context.id, str) else context.id
            context_name = context.name.strip() if isinstance(context.name, str) else context.name
            log_operation_start("ContextService.update", f"ContextId={context_id}, Name={context_name}")
            request = ModifyContextRequest(
                id=context_id,
                name=context_name,
                authorization=f"Bearer {self.agb.api_key}",
            )
            response = self.agb.client.modify_context(request)

            request_id = response.request_id

            if not response.is_successful():
                error_msg = response.get_error_message()
                log_operation_error("ContextService.update", error_msg or "Unknown error")
                return OperationResult(
                    request_id=request_id or "",
                    success=False,
                    error_message=error_msg
                )

            # Update was successful
            result_msg = f"ContextId={context_id}, RequestId={request_id}"
            log_operation_success("ContextService.update", result_msg)
            return OperationResult(
                request_id=request_id or "",
                success=True,
                data={"context_id": context_id}
            )
        except Exception as e:
            log_operation_error("ContextService.update", str(e), exc_info=True)
            return OperationResult(
                request_id="",
                success=False,
                error_message=f"Failed to update context {context_id}: {e}"
            )

    def delete(self, context: Context) -> OperationResult:
        """
        Deletes the specified context.

        Args:
            context (Context): The Context object to delete.

        Returns:
            OperationResult: Result object containing success status and request ID.
        """
        if context is None:
            log_operation_error("ContextService.delete", "context cannot be None")
            return OperationResult(
                success=False,
                error_message="context cannot be None",
                request_id=""
            )
        # Validate context.id
        if not context.id or (isinstance(context.id, str) and not context.id.strip()):
            error_msg = "context.id cannot be empty or None"
            log_operation_error("ContextService.delete", error_msg)
            return OperationResult(
                request_id="",
                success=False,
                error_message=error_msg
            )

        try:
            context_id = context.id.strip() if isinstance(context.id, str) else context.id
            log_operation_start("ContextService.delete", f"ContextId={context_id}")
            request = DeleteContextRequest(
                id=context_id, authorization=f"Bearer {self.agb.api_key}"
            )
            response = self.agb.client.delete_context(request)

            request_id = response.request_id

            if not response.is_successful():
                error_msg = response.get_error_message()
                log_operation_error("ContextService.delete", error_msg or "Unknown error")
                return OperationResult(
                    request_id=request_id or "",
                    success=False,
                    error_message=error_msg
                )

            # Delete was successful
            result_msg = f"ContextId={context_id}, RequestId={request_id}"
            log_operation_success("ContextService.delete", result_msg)
            return OperationResult(
                request_id=request_id or "",
                success=True,
                data={"context_id": context_id}
            )

        except Exception as e:
            log_operation_error("ContextService.delete", str(e), exc_info=True)
            return OperationResult(
                request_id="",
                success=False,
                error_message=f"Failed to delete context {context_id}: {e}"
            )

    def get_file_download_url(self, context_id: str, file_path: str) -> FileUrlResult:
        """
        Get a presigned download URL for a file in a context.

        Args:
            context_id (str): The ID of the context.
            file_path (str): The path of the file within the context.

        Returns:
            FileUrlResult: Result object containing the download URL.
        """
        # Validate required parameters
        if not context_id or (isinstance(context_id, str) and not context_id.strip()):
            error_msg = "context_id cannot be empty or None"
            log_operation_error("ContextService.get_file_download_url", error_msg)
            return FileUrlResult(
                request_id="",
                success=False,
                url="",
                error_message=error_msg
            )

        if not file_path or (isinstance(file_path, str) and not file_path.strip()):
            error_msg = "file_path cannot be empty or None"
            log_operation_error("ContextService.get_file_download_url", error_msg)
            return FileUrlResult(
                request_id="",
                success=False,
                url="",
                error_message=error_msg
            )

        validated_context_id = context_id.strip() if isinstance(context_id, str) else context_id
        validated_file_path = file_path.strip() if isinstance(file_path, str) else file_path
        log_operation_start("ContextService.get_file_download_url", f"ContextId={validated_context_id}, FilePath={validated_file_path}")
        req = GetContextFileDownloadUrlRequest(
            authorization=f"Bearer {self.agb.api_key}",
            context_id=validated_context_id,
            file_path=validated_file_path,
        )
        resp = self.agb.client.get_context_file_download_url(req)

        request_id = resp.request_id
        download_url = resp.get_download_url()

        if resp.is_successful():
            result_msg = f"ContextId={validated_context_id}, FilePath={validated_file_path}, RequestId={request_id}"
            log_operation_success("ContextService.get_file_download_url", result_msg)
        else:
            error_msg = resp.get_error_message()
            log_operation_error("ContextService.get_file_download_url", error_msg or "Unknown error")

        return FileUrlResult(
            request_id=request_id or "",
            success=resp.is_successful(),
            url=download_url,
            expire_time=resp.get_expire_time(),
            error_message="" if resp.is_successful() else resp.get_error_message()
        )

    def get_file_upload_url(self, context_id: str, file_path: str) -> FileUrlResult:
        """
        Get a presigned upload URL for a file in a context.

        Args:
            context_id (str): The ID of the context.
            file_path (str): The path of the file within the context.

        Returns:
            FileUrlResult: Result object containing the upload URL.
        """
        # Validate required parameters
        if not context_id or (isinstance(context_id, str) and not context_id.strip()):
            error_msg = "context_id cannot be empty or None"
            log_operation_error("ContextService.get_file_upload_url", error_msg)
            return FileUrlResult(
                request_id="",
                success=False,
                url="",
                error_message=error_msg
            )

        if not file_path or (isinstance(file_path, str) and not file_path.strip()):
            error_msg = "file_path cannot be empty or None"
            log_operation_error("ContextService.get_file_upload_url", error_msg)
            return FileUrlResult(
                request_id="",
                success=False,
                url="",
                error_message=error_msg
            )

        validated_context_id = context_id.strip() if isinstance(context_id, str) else context_id
        validated_file_path = file_path.strip() if isinstance(file_path, str) else file_path
        log_operation_start("ContextService.get_file_upload_url", f"ContextId={validated_context_id}, FilePath={validated_file_path}")
        req = GetContextFileUploadUrlRequest(
            authorization=f"Bearer {self.agb.api_key}",
            context_id=validated_context_id,
            file_path=validated_file_path,
        )
        resp = self.agb.client.get_context_file_upload_url(req)

        request_id = resp.request_id
        upload_url = resp.get_upload_url()

        if resp.is_successful():
            result_msg = f"ContextId={validated_context_id}, FilePath={validated_file_path}, RequestId={request_id}"
            log_operation_success("ContextService.get_file_upload_url", result_msg)
        else:
            error_msg = resp.get_error_message()
            log_operation_error("ContextService.get_file_upload_url", error_msg or "Unknown error")

        return FileUrlResult(
            request_id=request_id or "",
            success=resp.is_successful(),
            url=upload_url,
            expire_time=resp.get_expire_time(),
            error_message="" if resp.is_successful() else resp.get_error_message()
        )

    def delete_file(self, context_id: str, file_path: str) -> OperationResult:
        """
        Delete a file in a context.

        Args:
            context_id (str): The ID of the context.
            file_path (str): The path of the file within the context.

        Returns:
            OperationResult: Result object containing success status.
        """
        # Validate required parameters
        if not context_id or (isinstance(context_id, str) and not context_id.strip()):
            error_msg = "context_id cannot be empty or None"
            log_operation_error("ContextService.delete_file", error_msg)
            return OperationResult(
                request_id="",
                success=False,
                error_message=error_msg
            )

        if not file_path or (isinstance(file_path, str) and not file_path.strip()):
            error_msg = "file_path cannot be empty or None"
            log_operation_error("ContextService.delete_file", error_msg)
            return OperationResult(
                request_id="",
                success=False,
                error_message=error_msg
            )

        validated_context_id = context_id.strip() if isinstance(context_id, str) else context_id
        validated_file_path = file_path.strip() if isinstance(file_path, str) else file_path
        log_operation_start("ContextService.delete_file", f"ContextId={validated_context_id}, FilePath={validated_file_path}")
        req = DeleteContextFileRequest(
            authorization=f"Bearer {self.agb.api_key}",
            context_id=validated_context_id,
            file_path=validated_file_path,
        )
        resp = self.agb.client.delete_context_file(req)

        request_id = resp.request_id

        if resp.is_successful():
            result_msg = f"ContextId={validated_context_id}, FilePath={validated_file_path}, RequestId={request_id}"
            log_operation_success("ContextService.delete_file", result_msg)
        else:
            error_msg = resp.get_error_message()
            log_operation_error("ContextService.delete_file", error_msg or "Unknown error")

        return OperationResult(
            request_id=request_id or "",
            success=resp.is_successful(),
            data=resp.is_successful(),
            error_message="" if resp.is_successful() else resp.get_error_message()
        )

    def list_files(
        self,
        context_id: str,
        parent_folder_path: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 50,
    ) -> ContextFileListResult:
        """
        List files under a specific folder path in a context.

        Args:
            context_id (str): The ID of the context.
            parent_folder_path (Optional[str]): The parent folder path. Can be empty or None.
            page_number (int): Page number for pagination. Defaults to 1.
            page_size (int): Page size for pagination. Defaults to 50.

        Returns:
            ContextFileListResult: Result object containing list of file entries.
        """
        # Validate required parameters
        if not context_id or (isinstance(context_id, str) and not context_id.strip()):
            error_msg = "context_id cannot be empty or None"
            log_operation_error("ContextService.list_files", error_msg)
            return ContextFileListResult(
                request_id="",
                success=False,
                entries=[],
                error_message=error_msg
            )

        # parent_folder_path is optional and can be empty
        validated_context_id = context_id.strip() if isinstance(context_id, str) else context_id
        validated_parent_folder_path = parent_folder_path.strip() if parent_folder_path and isinstance(parent_folder_path, str) else (parent_folder_path or "")
        op_details = f"ContextId={validated_context_id}, ParentFolderPath={validated_parent_folder_path}, PageNumber={page_number}, PageSize={page_size}"
        log_operation_start("ContextService.list_files", op_details)
        req = DescribeContextFilesRequest(
            authorization=f"Bearer {self.agb.api_key}",
            page_number=page_number,
            page_size=page_size,
            parent_folder_path=validated_parent_folder_path,
            context_id=validated_context_id,
        )
        resp = self.agb.client.describe_context_files(req)

        request_id = resp.request_id

        if not resp.is_successful():
            error_msg = resp.get_error_message()
            log_operation_error("ContextService.list_files", error_msg or "Unknown error")
            return ContextFileListResult(
                request_id=request_id or "",
                success=False,
                entries=[],
                error_message=error_msg
            )

        try:
            raw_list = resp.get_files_data()
            entries = []
            for it in raw_list:
                # raw_list is always List[DescribeContextFilesResponseBodyData] or empty list
                entries.append(ContextFileEntry(
                    file_id=it.file_id or "",
                    file_name=it.file_name or "",
                    file_path=it.file_path or "",
                    file_type=it.file_type,
                    gmt_create=it.gmt_create,
                    gmt_modified=it.gmt_modified,
                    size=it.size,
                    status=it.status,
                ))

            # Get count from response
            count = resp.get_count()

            result_msg = f"ContextId={validated_context_id}, Found {len(entries)} files, TotalCount={count}"
            log_operation_success("ContextService.list_files", result_msg)
            return ContextFileListResult(
                request_id=request_id or "",
                success=True,
                entries=entries,
                count=count,
            )
        except Exception as e:
            log_operation_error("ContextService.list_files", f"Error parsing response: {str(e)}", exc_info=True)
            return ContextFileListResult(
                request_id=request_id or "",
                success=False,
                entries=[],
                error_message=f"Failed to parse response: {e}"
            )

    def clear_async(self, context_id: str) -> ClearContextResult:
        """
        Asynchronously initiate a task to clear the context's persistent data.

        This is a non-blocking method that returns immediately after initiating the clearing task
        on the backend. The context's state will transition to "clearing" while the operation
        is in progress.

        Args:
            context_id: Unique ID of the context to clear.

        Returns:
            A ClearContextResult object indicating the task has been successfully started,
            with status field set to "clearing".

        Raises:
            AGBError: If the backend API rejects the clearing request (e.g., invalid ID).
        """
        try:
            log_operation_start("ContextService.clear_async", f"ContextId={context_id}")
            request = ClearContextRequest(
                authorization=f"Bearer {self.agb.api_key}",
                id=context_id,
            )
            response = self.agb.client.clear_context(request)

            request_id = response.request_id or ""

            # Check for API-level errors
            if not response.is_successful():
                error_msg = response.get_error_message() or "Unknown error"
                log_operation_error("ContextService.clear_async", error_msg)
                return ClearContextResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_msg,
                )

            # ClearContext API returns success info without Data field
            # Initial status is "clearing" when the task starts
            result_msg = f"ContextId={context_id}, Status=clearing, RequestId={request_id}"
            log_operation_success("ContextService.clear_async", result_msg)
            return ClearContextResult(
                request_id=request_id,
                success=True,
                context_id=context_id,
                status="clearing",
                error_message="",
            )
        except Exception as e:
            log_operation_error("ContextService.clear_async", str(e), exc_info=True)
            raise AGBError(f"Failed to start context clearing for {context_id}: {e}")

    def get_clear_status(self, context_id: str) -> ClearContextResult:
        """
        Query the status of the clearing task.

        This method calls GetContext API directly and parses the raw response to extract
        the state field, which indicates the current clearing status.

        Args:
            context_id: ID of the context.

        Returns:
            ClearContextResult object containing the current task status.
        """
        try:
            log_operation_start("ContextService.get_clear_status", f"ContextId={context_id}")
            request = GetContextRequest(
                authorization=f"Bearer {self.agb.api_key}",
                id=context_id,
                allow_create=False,
            )
            response = self.agb.client.get_context(request)

            request_id = response.request_id or ""

            # Check for API-level errors
            if not response.is_successful():
                error_msg = response.get_error_message() or "Unknown error"
                log_operation_error("ContextService.get_clear_status", error_msg)
                return ClearContextResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_msg,
                )

            # Extract clearing status from the response using get_context_data()
            # The server's state field indicates the clearing status:
            # - "clearing": Clearing is in progress
            # - "available": Clearing completed successfully
            data = response.get_context_data()
            context_id = data.id or context_id or ""
            state = data.state or "clearing"  # Extract state from parsed response data
            error_message = ""  # ErrorMessage is not in GetContextResponse data

            result_msg = f"ContextId={context_id}, Status={state}, RequestId={request_id}"
            log_operation_success("ContextService.get_clear_status", result_msg)
            return ClearContextResult(
                request_id=request_id,
                success=True,
                context_id=context_id,
                status=state,
                error_message=error_message,
            )
        except Exception as e:
            log_operation_error("ContextService.get_clear_status", str(e), exc_info=True)
            return ClearContextResult(
                request_id="",
                success=False,
                error_message=f"Failed to get clear status: {e}",
            )

    def clear(
        self, context_id: str, timeout: int = 60, poll_interval: float = 2.0
    ) -> ClearContextResult:
        """
        Synchronously clear the context's persistent data and wait for the final result.

        This method wraps the `clear_async` and `_get_clear_status` polling logic,
        providing the simplest and most direct way to handle clearing tasks.

        The clearing process transitions through the following states:
        - "clearing": Data clearing is in progress
        - "available": Clearing completed successfully (final success state)

        Args:
            context_id (str): Unique ID of the context to clear.
            timeout (int): Timeout in seconds to wait for task completion. Defaults to 60.
            poll_interval (float): Interval in seconds between status polls. Defaults to 2.0.

        Returns:
            ClearContextResult: ClearContextResult object containing the final task result.
                The status field will be "available" on success.

        Raises:
            ClearanceTimeoutError: If the task fails to complete within the timeout.
            AGBError: If an API or network error occurs during execution.
        """
        log_operation_start("ContextService.clear", f"ContextId={context_id}, Timeout={timeout}s, PollInterval={poll_interval}s")
        # 1. Asynchronously start the clearing task
        start_result = self.clear_async(context_id)
        if not start_result.success:
            return start_result

        # 2. Poll task status until completion or timeout
        start_time = time.time()
        max_attempts = int(timeout / poll_interval)
        attempt = 0

        while attempt < max_attempts:
            # Wait before querying
            time.sleep(poll_interval)
            attempt += 1

            # Query task status (using GetContext API with context ID)
            status_result = self.get_clear_status(context_id)

            if not status_result.success:
                logger.error(
                    f"Failed to get clear status: {status_result.error_message}"
                )
                return status_result

            status = status_result.status
            logger.debug(
                f"Clear task status: {status} (attempt {attempt}/{max_attempts})"
            )

            # Check if completed
            # When clearing is complete, the state changes from "clearing" to "available"
            if status == "available":
                elapsed = time.time() - start_time
                result_msg = f"ContextId={context_id}, Status={status}, Elapsed={elapsed:.2f}s"
                log_operation_success("ContextService.clear", result_msg)
                return ClearContextResult(
                    request_id=start_result.request_id,
                    success=True,
                    context_id=status_result.context_id,
                    status=status,
                    error_message="",
                )
            elif status not in ("clearing", "pre-available"):
                # If status is not "clearing" or "pre-available", and not "available",
                # treat it as a potential error or unexpected state
                elapsed = time.time() - start_time
                logger.warning(
                    f"Context in unexpected state after {elapsed:.2f} seconds: {status}"
                )
                # Continue polling as the state might transition to "available"

        # Timeout
        elapsed = time.time() - start_time
        error_msg = f"Context clearing timed out after {elapsed:.2f} seconds"
        log_operation_error("ContextService.clear", error_msg)
        raise ClearanceTimeoutError(error_msg)