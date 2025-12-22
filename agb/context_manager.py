from typing import Optional, List, Dict, Any, Callable, TYPE_CHECKING
from agb.api.models import GetContextInfoRequest, SyncContextRequest
from agb.model.response import ApiResponse
from .logger import get_logger, log_operation_start, log_operation_success, log_operation_error
import json
import time
import threading
import asyncio

if TYPE_CHECKING:
    from agb.session import Session

# Initialize logger for this module
logger = get_logger("context_manager")


class ContextStatusData:
    def __init__(
        self,
        context_id: str = "",
        path: str = "",
        error_message: str = "",
        status: str = "",
        start_time: int = 0,
        finish_time: int = 0,
        task_type: str = "",
    ):
        self.context_id = context_id
        self.path = path
        self.error_message = error_message
        self.status = status
        self.start_time = start_time
        self.finish_time = finish_time
        self.task_type = task_type

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextStatusData":
        return cls(
            context_id=data.get("contextId", ""),
            path=data.get("path", ""),
            error_message=data.get("errorMessage", ""),
            status=data.get("status", ""),
            start_time=data.get("startTime", 0),
            finish_time=data.get("finishTime", 0),
            task_type=data.get("taskType", ""),
        )


class ContextInfoResult(ApiResponse):
    def __init__(
        self, request_id: str = "", success: bool = False, context_status_data: Optional[List[ContextStatusData]] = None, error_message: Optional[str] = None
    ):
        super().__init__(request_id)
        self.success = success
        self.context_status_data = context_status_data or []
        self.error_message = error_message


class ContextSyncResult(ApiResponse):
    def __init__(self, request_id: str = "", success: bool = False, error_message: str = ""):
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message


class ContextManager:
    """
    Manages context operations within a session in the AGB cloud environment.

    The ContextManager provides methods to get information about context synchronization
    status and to synchronize contexts with the session.

    """

    def __init__(self, session: "Session"):
        self.session = session

    def info(
        self,
        context_id: Optional[str] = None,
        path: Optional[str] = None,
        task_type: Optional[str] = None,
    ) -> ContextInfoResult:
        """
        Get detailed information about context synchronization status.

        Args:
            context_id (Optional[str]): The ID of the context to query.
            path (Optional[str]): Specific path within the context to query.
            task_type (Optional[str]): Filter by task type (e.g., "upload", "download").

        Returns:
            ContextInfoResult: Result object containing status information.
        """
        op_details = f"SessionId={self.session.get_session_id()}"
        if context_id:
            op_details += f", ContextId={context_id}"
        if path:
            op_details += f", Path={path}"
        if task_type:
            op_details += f", TaskType={task_type}"
        log_operation_start("ContextManager.info", op_details)

        request = GetContextInfoRequest(
            authorization=f"Bearer {self.session.get_api_key()}",
            session_id=self.session.get_session_id(),
        )
        if context_id:
            request.context_id = context_id
        if path:
            request.path = path
        if task_type:
            request.task_type = task_type
        response = self.session.get_client().get_context_info(request)

        request_id = response.request_id

        if not response.is_successful():
            error_msg = response.get_error_message()
            log_operation_error("ContextManager.info", error_msg or "Unknown error")
            return ContextInfoResult(
                request_id=request_id or "",
                success=False,
                context_status_data=[],
                error_message=error_msg
            )

        try:
            context_status_str = response.get_context_status()
            context_status_data= []

            # Parse the context status data
            if context_status_str:
                try:
                    # First, parse the outer array
                    status_items = json.loads(context_status_str)
                    for item in status_items:
                        if item.get("type") == "data":
                            # Parse the inner data string
                            data_items = json.loads(item.get("data", "[]"))
                            for data_item in data_items:
                                try:
                                    context_status_data.append(
                                        ContextStatusData.from_dict(data_item)
                                    )
                                except Exception as e:
                                    logger.error(f"❌ Error parsing data item: {e}")
                                    return ContextInfoResult(
                                        request_id=request_id or "",
                                        success=False,
                                        context_status_data=[],
                                        error_message=f"Failed to parse data item: {e}"
                                    )
                except Exception as e:
                    logger.error(f"❌ Unexpected error parsing context status: {e}")
                    return ContextInfoResult(
                        request_id=request_id or "",
                        success=False,
                        context_status_data=[],
                        error_message=f"Unexpected error parsing context status: {e}"
                    )

            result_msg = f"Found {len(context_status_data)} status entries, RequestId={request_id}"
            log_operation_success("ContextManager.info", result_msg)
            return ContextInfoResult(
                request_id=request_id or "",
                success=True,
                context_status_data=context_status_data
            )
        except Exception as e:
            log_operation_error("ContextManager.info", f"Error parsing response: {str(e)}", exc_info=True)
            return ContextInfoResult(
                request_id=request_id or "",
                success=False,
                context_status_data=[],
                error_message=f"Failed to parse response: {e}"
            )

    async def sync(
        self,
        context_id: Optional[str] = None,
        path: Optional[str] = None,
        mode: Optional[str] = None,
        callback: Optional[Callable[[bool], None]] = None,
        max_retries: int = 150,
        retry_interval: int = 1500,
    ) -> ContextSyncResult:
        """
        Synchronizes context with support for both async and sync calling patterns.

        Usage:
            # Async call - wait for completion
            result = await session.context.sync()

            # Sync call - immediate return with callback
            session.context.sync(callback=lambda success: logger.info(f"Done: {success}"))

        Args:
            context_id (Optional[str]): Optional ID of the context to synchronize. If provided, `path` must also be provided.
            path (Optional[str]): Optional path where the context should be mounted. If provided, `context_id` must also be provided.
            mode (Optional[str]): Optional synchronization mode (e.g., "upload", "download")
            callback (Optional[Callable[[bool], None]]): Optional callback function that receives success status. If provided, the method runs in background and calls callback when complete
            max_retries (int): Maximum number of retries for polling. Defaults to 150.
            retry_interval (int): Milliseconds to wait between retries. Defaults to 1500.

        Returns:
            ContextSyncResult: Result object containing success status and request ID
        """

        # Validate that context_id and path are provided together or both omitted
        has_context_id = context_id is not None and context_id.strip() != ""
        has_path = path is not None and path.strip() != ""

        if has_context_id != has_path:
            error_message = (
                "context_id and path must be provided together or both omitted. "
                "If you want to sync a specific context, both context_id and path are required. "
                "If you want to sync all contexts, omit both parameters."
            )
            return ContextSyncResult(
                request_id="",
                success=False,
                error_message=error_message
            )

        op_details = f"SessionId={self.session.get_session_id()}"
        if context_id:
            op_details += f", ContextId={context_id}"
        if path:
            op_details += f", Path={path}"
        if mode:
            op_details += f", Mode={mode}"
        log_operation_start("ContextManager.sync", op_details)

        request = SyncContextRequest(
            authorization=f"Bearer {self.session.get_api_key()}",
            session_id=self.session.get_session_id(),
        )
        if context_id:
            request.context_id = context_id
        if path:
            request.path = path
        if mode:
            request.mode = mode
        response = self.session.get_client().sync_context(request)

        request_id = response.request_id
        success = response.is_successful()

        if not success:
            error_msg = response.get_error_message()
            log_operation_error("ContextManager.sync", error_msg or "Unknown error")
        else:
            result_msg = f"RequestId={request_id}"
            if callback:
                result_msg += ", Callback provided (async polling)"
            log_operation_success("ContextManager.sync", result_msg)

        # If a callback is provided, polling will be performed in a background thread,
        # and the method will return immediately after starting the thread.
        # ⚠️ Note: If the callback accesses shared resources, the caller must ensure thread safety,
        # because _poll_for_completion runs in a new thread. Potential thread-safety issues depend on the callback logic.
        if callback is not None and success:
            poll_thread = threading.Thread(
                target=self._poll_for_completion,
                args=(callback, context_id, path, max_retries, retry_interval),
                daemon=True
            )
            poll_thread.start()
            return ContextSyncResult(request_id=request_id or "", success=success)
        # If no callback is provided, the method will block and wait for all sync tasks to finish.
        # This is a synchronous (blocking) pattern
        if success:
            final_success = await self._poll_for_completion_async(
                context_id, path, max_retries, retry_interval
            )
            return ContextSyncResult(request_id=request_id or "", success=final_success)

        return ContextSyncResult(request_id=request_id or "", success=success, error_message=response.get_error_message())

    def _poll_for_completion(
        self,
        callback: Callable[[bool], None],
        context_id: Optional[str] = None,
        path: Optional[str] = None,
        max_retries: int = 150,
        retry_interval: int = 1500,
    ) -> None:
        """
        Polls the info interface to check if sync is completed and calls callback.

        Args:
            callback (Callable[[bool], None]): Callback function that receives success status.
            context_id (Optional[str]): ID of the context to check.
            path (Optional[str]): Path to check.
            max_retries (int): Maximum number of retries.
            retry_interval (int): Milliseconds to wait between retries.
        """
        for retry in range(max_retries):
            try:
                # Get context status data
                info_result = self.info(context_id=context_id, path=path)

                # Check if all sync tasks are completed
                all_completed = True
                has_failure = False
                has_sync_tasks = False

                for item in info_result.context_status_data:
                    # We only care about sync tasks (upload/download)
                    if item.task_type not in ["upload", "download"]:
                        continue

                    has_sync_tasks = True
                    logger.info(f"🔄 Sync task {item.context_id} status: {item.status}, path: {item.path}")

                    if item.status not in ["Success", "Failed"]:
                        all_completed = False
                        break

                    if item.status == "Failed":
                        has_failure = True
                        logger.error(f"❌ Sync failed for context {item.context_id}: {item.error_message}")

                if all_completed or not has_sync_tasks:
                    # All tasks completed or no sync tasks found
                    if has_failure:
                        logger.warning("Context sync completed with failures")
                        callback(False)
                    elif has_sync_tasks:
                        logger.info("✅ Context sync completed successfully")
                        callback(True)
                    else:
                        logger.info("ℹ️  No sync tasks found")
                        callback(True)
                    break

                logger.info(f"⏳ Waiting for context sync to complete, attempt {retry+1}/{max_retries}")
                time.sleep(retry_interval / 1000.0)

            except Exception as e:
                logger.error(f"❌ Error checking context status on attempt {retry+1}: {e}")
                time.sleep(retry_interval / 1000.0)

        # If we've exhausted all retries, call callback with failure
        if retry == max_retries - 1:
            logger.error(f"❌ Context sync polling timed out after {max_retries} attempts")
            callback(False)

    async def _poll_for_completion_async(
        self,
        context_id: Optional[str] = None,
        path: Optional[str] = None,
        max_retries: int = 150,
        retry_interval: int = 1500,
    ) -> bool:
        """
        Async version of polling for sync completion.

        Args:
            context_id (Optional[str]): ID of the context to check.
            path (Optional[str]): Path to check.
            max_retries (int): Maximum number of retries.
            retry_interval (int): Milliseconds to wait between retries.

        Returns:
            bool: True if sync completed successfully, False otherwise.
        """
        for retry in range(max_retries):
            try:
                # Get context status data
                info_result = self.info(context_id=context_id, path=path)

                # Check if all sync tasks are completed
                all_completed = True
                has_failure = False
                has_sync_tasks = False

                for item in info_result.context_status_data:
                    # We only care about sync tasks (upload/download)
                    if item.task_type not in ["upload", "download"]:
                        continue

                    has_sync_tasks = True
                    logger.info(f"🔄 Sync task {item.context_id} status: {item.status}, path: {item.path}")

                    if item.status not in ["Success", "Failed"]:
                        all_completed = False
                        break

                    if item.status == "Failed":
                        has_failure = True
                        logger.error(f"❌ Sync failed for context {item.context_id}: {item.error_message}")

                if all_completed or not has_sync_tasks:
                    # All tasks completed or no sync tasks found
                    if has_failure:
                        logger.warning("Context sync completed with failures")
                        return False
                    elif has_sync_tasks:
                        logger.info("✅ Context sync completed successfully")
                        return True
                    else:
                        logger.info("ℹ️  No sync tasks found")
                        return True

                logger.info(f"⏳ Waiting for context sync to complete, attempt {retry+1}/{max_retries}")
                await asyncio.sleep(retry_interval / 1000.0)

            except Exception as e:
                logger.error(f"❌ Error checking context status on attempt {retry+1}: {e}")
                await asyncio.sleep(retry_interval / 1000.0)

        # If we've exhausted all retries, return failure
        logger.error(f"❌ Context sync polling timed out after {max_retries} attempts")
        return False
