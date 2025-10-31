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
)
from agb.model.response import ApiResponse, OperationResult
from .logger import get_logger, log_api_call, log_api_response, log_operation_error
import json

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
            log_api_call("ListContexts", request_details)
            request = ListContextsRequest(
                authorization=f"Bearer {self.agb.api_key}",
                max_results=max_results,
                next_token=params.next_token,
            )
            response = self.agb.client.list_contexts(request)
            try:
                response_body = json.dumps(
                    response.json_data, ensure_ascii=False, indent=2
                )
                log_api_response(response_body)
            except Exception:
                logger.debug(f"📥 Response: {response}")

            request_id = response.request_id

            if not response.is_successful():
                return ContextListResult(
                    request_id=request_id or "",
                    success=False,
                    contexts=[],
                    error_message=response.get_error_message()
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
                logger.error(error_msg)
                return ContextResult(
                    success=False,
                    error_message=error_msg,
                    request_id=""
                )

            # Validation: If AllowCreate is True, ID cannot be provided
            if create and context_id:
                error_msg = "context_id cannot be provided when create=True (only name is allowed when creating)"
                logger.error(error_msg)
                return ContextResult(
                    success=False,
                    error_message=error_msg,
                    request_id=""
                )

            # Note: If login_region_id is None or empty, the server will default to Hangzhou region (cn-hangzhou)
            log_api_call(
                "GetContext",
                f"Id={context_id or 'None'}, Name={name or 'None'}, AllowCreate={create}, LoginRegionId={login_region_id}"
            )
            request = GetContextRequest(
                id=context_id,
                name=name,
                allow_create=create,
                login_region_id=login_region_id,  # None means use default region (cn-hangzhou)
                authorization=f"Bearer {self.agb.api_key}",
            )
            response = self.agb.client.get_context(request)
            try:
                response_body = json.dumps(
                    response.json_data, ensure_ascii=False, indent=2
                )
                log_api_response(response_body)
            except Exception:
                logger.debug(f"📥 Response: {response}")

            request_id = response.request_id

            if not response.is_successful():
                return ContextResult(
                    request_id=request_id or "",
                    success=False,
                    context_id="",
                    context=None,
                    error_message=response.get_error_message()
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
        # Validate required parameter
        if context is None:
            error_msg = "context cannot be None"
            logger.error(error_msg)
            return OperationResult(
                request_id="",
                success=False,
                error_message=error_msg
            )

        # Validate context.id
        if not context.id or (isinstance(context.id, str) and not context.id.strip()):
            error_msg = "context.id cannot be empty or None"
            logger.error(error_msg)
            return OperationResult(
                request_id="",
                success=False,
                error_message=error_msg
            )

        # Validate context.name
        if not context.name or (isinstance(context.name, str) and not context.name.strip()):
            error_msg = "context.name cannot be empty or None"
            logger.error(error_msg)
            return OperationResult(
                request_id="",
                success=False,
                error_message=error_msg
            )

        try:
            context_id = context.id.strip() if isinstance(context.id, str) else context.id
            context_name = context.name.strip() if isinstance(context.name, str) else context.name
            log_api_call("ModifyContext", f"Id={context_id}, Name={context_name}")
            request = ModifyContextRequest(
                id=context_id,
                name=context_name,
                authorization=f"Bearer {self.agb.api_key}",
            )
            response = self.agb.client.modify_context(request)
            try:
                response_body = json.dumps(
                    response.json_data, ensure_ascii=False, indent=2
                )
                log_api_response(response_body)
            except Exception:
                logger.debug(f"📥 Response: {response}")

            request_id = response.request_id

            if not response.is_successful():
                return OperationResult(
                    request_id=request_id or "",
                    success=False,
                    error_message=response.get_error_message()
                )

            # Update was successful
            return OperationResult(
                request_id=request_id or "",
                success=True,
                data={"context_id": context_id}
            )
        except Exception as e:
            logger.error(f"Error calling ModifyContext: {e}")
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
        # Validate required parameter
        if context is None:
            error_msg = "context cannot be None"
            logger.error(error_msg)
            return OperationResult(
                request_id="",
                success=False,
                error_message=error_msg
            )

        # Validate context.id
        if not context.id or (isinstance(context.id, str) and not context.id.strip()):
            error_msg = "context.id cannot be empty or None"
            logger.error(error_msg)
            return OperationResult(
                request_id="",
                success=False,
                error_message=error_msg
            )

        try:
            context_id = context.id.strip() if isinstance(context.id, str) else context.id
            log_api_call("DeleteContext", f"Id={context_id}")
            request = DeleteContextRequest(
                id=context_id, authorization=f"Bearer {self.agb.api_key}"
            )
            response = self.agb.client.delete_context(request)
            try:
                response_body = json.dumps(
                    response.json_data, ensure_ascii=False, indent=2
                )
                log_api_response(response_body)
            except Exception:
                logger.debug(f"📥 Response: {response}")

            request_id = response.request_id

            if not response.is_successful():
                return OperationResult(
                    request_id=request_id or "",
                    success=False,
                    error_message=response.get_error_message()
                )

            # Delete was successful
            return OperationResult(
                request_id=request_id or "",
                success=True,
                data={"context_id": context_id}
            )

        except Exception as e:
            logger.error(f"Error calling DeleteContext: {e}")
            return OperationResult(
                request_id="",
                success=False,
                error_message=f"Failed to delete context {context_id}: {e}"
            )

    def get_file_download_url(self, context_id: str, file_path: str) -> FileUrlResult:
        """Get a presigned download URL for a file in a context."""
        # Validate required parameters
        if not context_id or (isinstance(context_id, str) and not context_id.strip()):
            error_msg = "context_id cannot be empty or None"
            logger.error(error_msg)
            return FileUrlResult(
                request_id="",
                success=False,
                url="",
                error_message=error_msg
            )

        if not file_path or (isinstance(file_path, str) and not file_path.strip()):
            error_msg = "file_path cannot be empty or None"
            logger.error(error_msg)
            return FileUrlResult(
                request_id="",
                success=False,
                url="",
                error_message=error_msg
            )

        validated_context_id = context_id.strip() if isinstance(context_id, str) else context_id
        validated_file_path = file_path.strip() if isinstance(file_path, str) else file_path
        log_api_call("GetContextFileDownloadUrl", f"ContextId={validated_context_id}, FilePath={validated_file_path}")
        req = GetContextFileDownloadUrlRequest(
            authorization=f"Bearer {self.agb.api_key}",
            context_id=validated_context_id,
            file_path=validated_file_path,
        )
        resp = self.agb.client.get_context_file_download_url(req)
        try:
            response_body = json.dumps(
                resp.json_data, ensure_ascii=False, indent=2
            )
            log_api_response(response_body)
        except Exception:
            logger.debug(f"Response: {resp}")

        request_id = resp.request_id
        download_url = resp.get_download_url()

        return FileUrlResult(
            request_id=request_id or "",
            success=resp.is_successful(),
            url=download_url,
            expire_time=resp.get_expire_time(),
            error_message="" if resp.is_successful() else resp.get_error_message()
        )

    def get_file_upload_url(self, context_id: str, file_path: str) -> FileUrlResult:
        """Get a presigned upload URL for a file in a context."""
        # Validate required parameters
        if not context_id or (isinstance(context_id, str) and not context_id.strip()):
            error_msg = "context_id cannot be empty or None"
            logger.error(error_msg)
            return FileUrlResult(
                request_id="",
                success=False,
                url="",
                error_message=error_msg
            )

        if not file_path or (isinstance(file_path, str) and not file_path.strip()):
            error_msg = "file_path cannot be empty or None"
            logger.error(error_msg)
            return FileUrlResult(
                request_id="",
                success=False,
                url="",
                error_message=error_msg
            )

        validated_context_id = context_id.strip() if isinstance(context_id, str) else context_id
        validated_file_path = file_path.strip() if isinstance(file_path, str) else file_path
        log_api_call("GetContextFileUploadUrl", f"ContextId={validated_context_id}, FilePath={validated_file_path}")
        req = GetContextFileUploadUrlRequest(
            authorization=f"Bearer {self.agb.api_key}",
            context_id=validated_context_id,
            file_path=validated_file_path,
        )
        resp = self.agb.client.get_context_file_upload_url(req)
        try:
            response_body = json.dumps(
                resp.json_data, ensure_ascii=False, indent=2
            )
            log_api_response(response_body)
        except Exception:
            logger.debug(f"Response: {resp}")

        request_id = resp.request_id
        upload_url = resp.get_upload_url()

        return FileUrlResult(
            request_id=request_id or "",
            success=resp.is_successful(),
            url=upload_url,
            expire_time=resp.get_expire_time(),
            error_message="" if resp.is_successful() else resp.get_error_message()
        )

    def delete_file(self, context_id: str, file_path: str) -> OperationResult:
        """Delete a file in a context."""
        # Validate required parameters
        if not context_id or (isinstance(context_id, str) and not context_id.strip()):
            error_msg = "context_id cannot be empty or None"
            logger.error(error_msg)
            return OperationResult(
                request_id="",
                success=False,
                error_message=error_msg
            )

        if not file_path or (isinstance(file_path, str) and not file_path.strip()):
            error_msg = "file_path cannot be empty or None"
            logger.error(error_msg)
            return OperationResult(
                request_id="",
                success=False,
                error_message=error_msg
            )

        validated_context_id = context_id.strip() if isinstance(context_id, str) else context_id
        validated_file_path = file_path.strip() if isinstance(file_path, str) else file_path
        log_api_call("DeleteContextFile", f"ContextId={validated_context_id}, FilePath={validated_file_path}")
        req = DeleteContextFileRequest(
            authorization=f"Bearer {self.agb.api_key}",
            context_id=validated_context_id,
            file_path=validated_file_path,
        )
        resp = self.agb.client.delete_context_file(req)
        try:
            response_body = json.dumps(
                resp.json_data, ensure_ascii=False, indent=2
            )
            log_api_response(response_body)
        except Exception:
            logger.debug(f"Response: {resp}")

        request_id = resp.request_id

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
        """List files under a specific folder path in a context.

        Args:
            context_id (str): The ID of the context.
            parent_folder_path (Optional[str]): The parent folder path. Can be empty or None.
            page_number (int): Page number for pagination. Defaults to 1.
            page_size (int): Page size for pagination. Defaults to 50.
        """
        # Validate required parameters
        if not context_id or (isinstance(context_id, str) and not context_id.strip()):
            error_msg = "context_id cannot be empty or None"
            logger.error(error_msg)
            return ContextFileListResult(
                request_id="",
                success=False,
                entries=[],
                error_message=error_msg
            )

        # parent_folder_path is optional and can be empty
        validated_context_id = context_id.strip() if isinstance(context_id, str) else context_id
        validated_parent_folder_path = parent_folder_path.strip() if parent_folder_path and isinstance(parent_folder_path, str) else (parent_folder_path or "")
        log_api_call("DescribeContextFiles",
            f"ContextId={validated_context_id}, ParentFolderPath={validated_parent_folder_path}, "
            f"PageNumber={page_number}, PageSize={page_size}")
        req = DescribeContextFilesRequest(
            authorization=f"Bearer {self.agb.api_key}",
            page_number=page_number,
            page_size=page_size,
            parent_folder_path=validated_parent_folder_path,
            context_id=validated_context_id,
        )
        resp = self.agb.client.describe_context_files(req)
        try:
            response_body = json.dumps(
                resp.json_data, ensure_ascii=False, indent=2
            )
            log_api_response(response_body)
        except Exception:
            logger.debug(f"Response: {resp}")

        request_id = resp.request_id

        if not resp.is_successful():
            return ContextFileListResult(
                request_id=request_id or "",
                success=False,
                entries=[],
                error_message=resp.get_error_message()
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

            return ContextFileListResult(
                request_id=request_id or "",
                success=True,
                entries=entries,
                count=count,
            )
        except Exception as e:
            logger.error(f"Error parsing DescribeContextFiles response: {e}")
            return ContextFileListResult(
                request_id=request_id or "",
                success=False,
                entries=[],
                error_message=f"Failed to parse response: {e}"
            )
