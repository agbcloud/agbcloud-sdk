"""
File transfer module for uploading and downloading files between local and OSS.
"""

import asyncio
import json
import os
import time
from pathlib import PurePosixPath
from typing import Callable, Dict, Optional, Tuple

import httpx

from agb.api.models import GetAndLoadInternalContextRequest
from agb.logger import get_logger, log_operation_start, log_operation_success, log_operation_error
from agb.model.response import UploadResult, DownloadResult

# Initialize logger for this module
logger = get_logger("file_transfer")


class FileTransfer:
    """
    Provides pre-signed URL upload/download functionality between local and OSS,
    with integration to Session Context synchronization.

    Prerequisites and Constraints:
    - Session must be associated with the corresponding context_id and path through
      CreateSessionParams.context_syncs, and remote_path should fall within that
      synchronization path (or conform to backend path rules).
    - Requires available AGB context service (agb.context) and session context.
    """

    def __init__(
        self,
        agb,  # AGB instance (for using agb.context service)
        session,  # Created session object (for session.context.sync/info)
        *,
        http_timeout: float = 60.0,
        follow_redirects: bool = True,
    ):
        """
        Initialize FileTransfer with AGB client and session.

        Args:
            agb: AGB instance for context service access
            session: Created session object for context operations
            http_timeout: HTTP request timeout in seconds (default: 60.0)
            follow_redirects: Whether to follow HTTP redirects (default: True)
        """
        self._agb = agb
        self._context_svc = agb.context
        self._session = session
        self._http_timeout = http_timeout
        self._follow_redirects = follow_redirects
        self.context_id: Optional[str] = None
        self.context_path: Optional[str] = None

        # Task completion states (for compatibility)
        self._finished_states = {
            "success",
            "successful",
            "ok",
            "finished",
            "done",
            "completed",
            "complete",
        }

    def ensure_context_id(self) -> Tuple[bool, Optional[str]]:
        """
        Lazy-load the file_transfer context ID for this session.
        This calls GetAndLoadInternalContext with sessionId and contextTypes=["file_transfer"].
        """
        if self.context_id:
            return True, ""

        try:
            log_operation_start("FileTransfer.ensure_context_id", f"SessionId={self._session.get_session_id()}")
            request = GetAndLoadInternalContextRequest(
                authorization=f"Bearer {self._agb.api_key}",
                session_id=self._session.get_session_id(),
                context_types=["file_transfer"],
            )

            client = self._agb.client
            if hasattr(client, "get_and_load_internal_context_async") and callable(
                getattr(client, "get_and_load_internal_context_async")
            ):
                response = client.get_and_load_internal_context_async(request)
            else:
                response = client.get_and_load_internal_context(request)

            # Extract context_id from response data
            # Response has structure: response.data is a list of context items
            # Each item has contextId, contextType, and contextPath

            # Check for API-level errors
            if not response.is_successful():
                error_msg = response.get_error_message() or "Unknown error"
                log_operation_error("FileTransfer.ensure_context_id", error_msg)
                return False, error_msg

            # Get context list from response
            data = response.get_context_list()
            if isinstance(data, list) and len(data) > 0:
                for item in data:
                    if isinstance(item, dict):
                        context_id = item.get("contextId", "")
                        context_path = item.get("contextPath", "")
                        if context_id and context_path:
                            self.context_id = context_id
                            self.context_path = context_path
                            result_msg = f"ContextId={context_id}, ContextPath={context_path}"
                            log_operation_success("FileTransfer.ensure_context_id", result_msg)
                            return True, ""
            error_msg = "Response contains no data"
            log_operation_error("FileTransfer.ensure_context_id", error_msg)
            return False, error_msg
        except Exception as e:
            log_operation_error("FileTransfer.ensure_context_id", str(e), exc_info=True)
            return False, str(e)

    def upload(
        self,
        local_path: str,
        remote_path: str,
        *,
        content_type: Optional[str] = None,
        wait: bool = True,
        wait_timeout: float = 30.0,
        poll_interval: float = 1.5,
        progress_cb: Optional[
            Callable[[int], None]
        ] = None,  # Callback with cumulative bytes transferred
    ) -> UploadResult:
        """
        Upload workflow:
        1) Get OSS pre-signed URL via context.get_file_upload_url
        2) Upload local file to OSS using the URL (HTTP PUT)
        3) Trigger session.context.sync(mode="download") to sync cloud disk data from OSS
        4) If wait=True, poll session.context.info until upload task reaches completion or timeout

        Returns UploadResult containing request_ids, HTTP status, ETag and other information.
        """
        log_operation_start("FileTransfer.upload", f"LocalPath={local_path}, RemotePath={remote_path}, Wait={wait}")
        # 0. Parameter validation
        if not os.path.isfile(local_path):
            error_msg = f"Local file not found: {local_path}"
            log_operation_error("FileTransfer.upload", error_msg)
            return UploadResult(
                success=False,
                request_id_upload_url=None,
                request_id_sync=None,
                http_status=None,
                etag=None,
                bytes_sent=0,
                path=remote_path,
                error_message=error_msg,
            )
        if self.context_id is None:
            ensure_result, message = self.ensure_context_id()
            if not ensure_result:
                log_operation_error("FileTransfer.upload", f"Failed to ensure context_id: {message}")
                return UploadResult(
                    success=False,
                    request_id_upload_url=None,
                    request_id_sync=None,
                    http_status=None,
                    etag=None,
                    bytes_sent=0,
                    path=remote_path,
                    error_message=message,
                )
        # Ensure context_id is set
        if not self.context_id:
            error_msg = "Context ID not available"
            log_operation_error("FileTransfer.upload", error_msg)
            return UploadResult(
                success=False,
                request_id_upload_url=None,
                request_id_sync=None,
                http_status=None,
                etag=None,
                bytes_sent=0,
                path=remote_path,
                error_message=error_msg,
            )
        # 1. Get pre-signed upload URL
        url_res = self._context_svc.get_file_upload_url(
            self.context_id, remote_path
        )
        if not getattr(url_res, "success", False) or not getattr(url_res, "url", None):
            error_msg = f"get_file_upload_url failed: {getattr(url_res, 'message', 'unknown error')}"
            log_operation_error("FileTransfer.upload", error_msg)
            return UploadResult(
                success=False,
                request_id_upload_url=getattr(url_res, "request_id", None),
                request_id_sync=None,
                http_status=None,
                etag=None,
                bytes_sent=0,
                path=remote_path,
                error_message=error_msg,
            )

        upload_url = url_res.url
        req_id_upload = getattr(url_res, "request_id", None)

        logger.info(f"Uploading {local_path} to OSS (URL: {upload_url})")

        # 2. PUT upload to pre-signed URL
        try:
            http_status, etag, bytes_sent = self._put_file_sync(upload_url,
                local_path,
                self._http_timeout,
                self._follow_redirects,
                content_type,
                progress_cb,
            )
            logger.info(f"Upload completed with HTTP {http_status}, BytesSent={bytes_sent}")
            if http_status not in (200, 201, 204):
                error_msg = f"Upload failed with HTTP {http_status}"
                log_operation_error("FileTransfer.upload", error_msg)
                return UploadResult(
                    success=False,
                    request_id_upload_url=req_id_upload,
                    request_id_sync=None,
                    http_status=http_status,
                    etag=etag,
                    bytes_sent=bytes_sent,
                    path=remote_path,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("FileTransfer.upload", f"Upload exception: {str(e)}", exc_info=True)
            return UploadResult(
                success=False,
                request_id_upload_url=req_id_upload,
                request_id_sync=None,
                http_status=None,
                etag=None,
                bytes_sent=0,
                path=remote_path,
                error_message=f"Upload exception: {e}",
            )

        # 3. Trigger sync to cloud disk (download mode),download from oss to cloud disk
        req_id_sync = None
        try:
            logger.info("Triggering sync to cloud disk (download mode)")
            req_id_sync = self._await_sync(
                "download", remote_path, self.context_id or ""
            )
        except Exception as e:
            error_msg = f"session.context.sync(download) failed: {e}"
            log_operation_error("FileTransfer.upload", error_msg, exc_info=True)
            return UploadResult(
                success=False,
                request_id_upload_url=req_id_upload,
                request_id_sync=req_id_sync,
                http_status=http_status,
                etag=etag,
                bytes_sent=bytes_sent,
                path=remote_path,
                error_message=error_msg,
            )

        logger.info(f"Sync request ID: {req_id_sync}")
        # 4. Optionally wait for task completion
        if wait:
            ok, err = self._wait_for_task(
                context_id=self.context_id or "",
                remote_path=remote_path,
                task_type="download",
                timeout=wait_timeout,
                interval=poll_interval,
            )
            if not ok:
                error_msg = f"Upload sync not finished: {err or 'timeout or unknown'}"
                log_operation_error("FileTransfer.upload", error_msg)
                return UploadResult(
                    success=False,
                    request_id_upload_url=req_id_upload,
                    request_id_sync=req_id_sync,
                    http_status=http_status,
                    etag=etag,
                    bytes_sent=bytes_sent,
                    path=remote_path,
                    error_message=error_msg,
                )

        result_msg = f"RemotePath={remote_path}, BytesSent={bytes_sent}, RequestIdUpload={req_id_upload}, RequestIdSync={req_id_sync}"
        log_operation_success("FileTransfer.upload", result_msg)
        return UploadResult(
            success=True,
            request_id_upload_url=req_id_upload,
            request_id_sync=req_id_sync,
            http_status=http_status,
            etag=etag,
            bytes_sent=bytes_sent,
            path=remote_path,
            error_message=None,
        )

    def download(
        self,
        remote_path: str,
        local_path: str,
        *,
        overwrite: bool = True,
        wait: bool = True,
        wait_timeout: float = 300.0,
        poll_interval: float = 1.5,
        progress_cb: Optional[
            Callable[[int], None]
        ] = None,  # Callback with cumulative bytes received
    ) -> DownloadResult:
        """
        Download workflow:
        1) Trigger session.context.sync(mode="upload") to sync cloud disk data to OSS
        2) Get pre-signed download URL via context.get_file_download_url
        3) Download the file and save to local local_path
        4) If wait=True, wait for download task to reach completion after step 1
           (ensuring backend has prepared the download object)

        Returns DownloadResult containing sync and download request_ids, HTTP status, byte count, etc.
        """
        log_operation_start("FileTransfer.download", f"RemotePath={remote_path}, LocalPath={local_path}, Wait={wait}, Overwrite={overwrite}")
        # Use default context if none provided
        if self.context_id is None:
            ensure_result, message = self.ensure_context_id()
            if not ensure_result:
                log_operation_error("FileTransfer.download", f"Failed to ensure context_id: {message}")
                return DownloadResult(
                    success=False,
                    request_id_download_url=None,
                    request_id_sync=None,
                    http_status=None,
                    bytes_received=0,
                    path=remote_path,
                    local_path=local_path,
                    error_message=message,
                )
        # Ensure context_id is set
        if not self.context_id:
            error_msg = "Context ID not available"
            log_operation_error("FileTransfer.download", error_msg)
            return DownloadResult(
                success=False,
                request_id_download_url=None,
                request_id_sync=None,
                http_status=None,
                bytes_received=0,
                path=remote_path,
                local_path=local_path,
                error_message=error_msg,
            )
        # 1. Trigger cloud disk to OSS download sync
        req_id_sync = None
        try:
            logger.info(f"Triggering sync to OSS (upload mode) for path: {remote_path}")
            req_id_sync = self._await_sync(
                "upload", remote_path, self.context_id or ""
            )
        except Exception as e:
            error_msg = f"session.context.sync(upload) failed: {e}"
            log_operation_error("FileTransfer.download", error_msg, exc_info=True)
            return DownloadResult(
                success=False,
                request_id_download_url=None,
                request_id_sync=req_id_sync,
                http_status=None,
                bytes_received=0,
                path=remote_path,
                local_path=local_path,
                error_message=error_msg,
            )

        # Optionally wait for task completion (ensure object is ready in OSS)
        if wait:
            ok, err = self._wait_for_task(
                context_id=self.context_id or "",
                remote_path=remote_path,
                task_type="upload",
                timeout=wait_timeout,
                interval=poll_interval,
            )
            if not ok:
                error_msg = f"Download sync not finished: {err or 'timeout or unknown'}"
                log_operation_error("FileTransfer.download", error_msg)
                return DownloadResult(
                    success=False,
                    request_id_download_url=None,
                    request_id_sync=req_id_sync,
                    http_status=None,
                    bytes_received=0,
                    path=remote_path,
                    local_path=local_path,
                    error_message=error_msg,
                )

        # 2. Get pre-signed download URL
        url_res = self._context_svc.get_file_download_url(
            self.context_id, remote_path
        )
        if not getattr(url_res, "success", False) or not getattr(url_res, "url", None):
            error_msg = f"get_file_download_url failed: {getattr(url_res, 'message', 'unknown error')}"
            log_operation_error("FileTransfer.download", error_msg)
            return DownloadResult(
                success=False,
                request_id_download_url=getattr(url_res, "request_id", None),
                request_id_sync=req_id_sync,
                http_status=None,
                bytes_received=0,
                path=remote_path,
                local_path=local_path,
                error_message=error_msg,
            )

        download_url = url_res.url
        req_id_download = getattr(url_res, "request_id", None)

        # 3. Download and save to local
        try:
            os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
            if os.path.exists(local_path) and not overwrite:
                return DownloadResult(
                    success=False,
                    request_id_download_url=req_id_download,
                    request_id_sync=req_id_sync,
                    http_status=None,
                    bytes_received=0,
                    path=remote_path,
                    local_path=local_path,
                    error_message=f"Destination exists and overwrite=False: {local_path}",
                )

            logger.info(f"Downloading from OSS to {local_path} (URL: {download_url})")
            http_status, bytes_received = self._get_file_sync(download_url,
                local_path,
                self._http_timeout,
                self._follow_redirects,
                progress_cb,
            )
            logger.info(f"Download completed with HTTP {http_status}, BytesReceived={bytes_received}")
            if http_status != 200:
                error_msg = f"Download failed with HTTP {http_status}"
                log_operation_error("FileTransfer.download", error_msg)
                return DownloadResult(
                    success=False,
                    request_id_download_url=req_id_download,
                    request_id_sync=req_id_sync,
                    http_status=http_status,
                    bytes_received=bytes_received,
                    path=remote_path,
                    local_path=local_path,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("FileTransfer.download", f"Download exception: {str(e)}", exc_info=True)
            return DownloadResult(
                success=False,
                request_id_download_url=req_id_download,
                request_id_sync=req_id_sync,
                http_status=None,
                bytes_received=0,
                path=remote_path,
                local_path=local_path,
                error_message=f"Download exception: {e}",
            )

        bytes_final = os.path.getsize(local_path) if os.path.exists(local_path) else 0
        result_msg = f"RemotePath={remote_path}, LocalPath={local_path}, BytesReceived={bytes_final}, RequestIdDownload={req_id_download}, RequestIdSync={req_id_sync}"
        log_operation_success("FileTransfer.download", result_msg)
        return DownloadResult(
            success=True,
            request_id_download_url=req_id_download,
            request_id_sync=req_id_sync,
            http_status=200,
            bytes_received=bytes_final,
            path=remote_path,
            local_path=local_path,
            error_message=None,
        )

    # ========== Internal Utilities ==========

    @staticmethod
    def _extract_remote_dir_path(remote_path: str) -> Optional[str]:
        """
        Extract a directory path from a remote path (POSIX style).

        Notes:
        - This function is ONLY used for `session.context.sync` / `session.context.info`
          `path` parameter. In those APIs, `path` means a mounted/sync directory, not a
          single file path.
        - Presigned URL APIs (`get_file_upload_url` / `get_file_download_url`) still use
          the original file path.

        Rules:
        - Empty/blank input: return None
        - If the input ends with '/': treat it as a directory and strip trailing slashes
          (keep '/' for root)
        - Otherwise: return the parent directory; if parent is '.' (e.g. 'a.txt'), return
          None (meaning: do not pass `path`)
        """
        if remote_path is None:
            return None
        raw = remote_path.strip()
        if not raw:
            return None

        # Normalize separators to POSIX to avoid issues with Windows-style backslashes.
        raw = raw.replace("\\", "/")

        if raw == "/":
            return "/"

        # If it's a directory path (ends with '/'), keep it as a directory.
        if raw.endswith("/"):
            normalized = raw.rstrip("/")
            return normalized if normalized else "/"

        p = PurePosixPath(raw)
        parent = str(p.parent)
        if parent == ".":
            return None
        # PurePosixPath turns parent of '/a' into '/', which is expected.
        return parent

    def _await_sync(
        self, mode: str, remote_path: str = "", context_id: str = ""
    ) -> Optional[str]:
        """
        Compatibility wrapper for session.context.sync which is an async coroutine.
        Uses asyncio to execute the coroutine in a synchronous context.
        Returns request_id if available
        """
        mode = mode.lower().strip()

        sync_fn = getattr(self._session.context, "sync")
        dir_path = self._extract_remote_dir_path(remote_path)
        logger.info(
            f"Calling session.context.sync(mode={mode}, path={dir_path}, context_id={context_id})"
        )

        async def _call_sync():
            """Helper function to call sync with different parameter combinations"""
            # Try as coroutine with mode, path, and context_id parameters
            try:
                return await sync_fn(
                    mode=mode,
                    path=dir_path,
                    context_id=context_id if context_id else None,
                )
            except TypeError:
                # Backend may not support all parameters, try with mode and path only
                try:
                    return await sync_fn(
                        mode=mode,
                        path=dir_path
                    )
                except TypeError:
                    # Backend may not support mode or path parameter
                    try:
                        return await sync_fn(mode=mode)
                    except TypeError:
                        # Backend may not support mode parameter
                        return await sync_fn()

        # Run the async coroutine
        try:
            # Check if there's a running event loop
            asyncio.get_running_loop()
            # If we get here, there's a running loop, so we need to use a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _call_sync())
                result = future.result()
        except RuntimeError:
            # No event loop is running, we can use asyncio.run()
            result = asyncio.run(_call_sync())

        # Return request_id if available
        success = getattr(result, "success", False)
        request_id = getattr(result, "request_id", None)
        logger.info(f"Sync result: success={success}, request_id={request_id}")
        return request_id

    def _wait_for_task(
        self,
        *,
        context_id: str,
        remote_path: str,
        task_type: Optional[str],
        timeout: float,
        interval: float,
    ) -> Tuple[bool, Optional[str]]:
        """
        Poll session.context.info within timeout to check if specified task is completed.
        Returns (True, None) on success, (False, error_msg) on failure.
        """
        deadline = time.time() + timeout
        last_err = None
        dir_path = self._extract_remote_dir_path(remote_path)

        while time.time() < deadline:
            try:
                info_fn = getattr(self._session.context, "info")
                # Try calling with filter parameters
                try:
                    res = info_fn(
                        context_id=context_id, path=dir_path, task_type=task_type
                    )
                except TypeError:
                    res = info_fn()

                # Parse response
                status_list = getattr(res, "context_status_data", None) or []
                for item in status_list:
                    cid = getattr(item, "context_id", None)
                    path = getattr(item, "path", None)
                    ttype = getattr(item, "task_type", None)
                    status = getattr(item, "status", None)
                    err = getattr(item, "error_message", None)

                    if (
                        cid == context_id
                        and path == dir_path
                        and (task_type is None or ttype == task_type)
                    ):
                        if err:
                            return False, f"Task error: {err}"
                        if status and status.lower() in self._finished_states:
                            return True, None
                        # Otherwise continue waiting
                last_err = "task not finished"
            except Exception as e:
                last_err = f"info error: {e}"

            time.sleep(interval)

        return False, last_err or "timeout"

    @staticmethod
    def _put_file_sync(
        url: str,
        file_path: str,
        timeout: float,
        follow_redirects: bool,
        content_type: Optional[str],
        progress_cb: Optional[Callable[[int], None]],
    ) -> Tuple[int, Optional[str], int]:
        """
        Synchronously PUT file in background thread using httpx.
        Returns (status_code, etag, bytes_sent)
        """
        headers: Dict[str, str] = {}
        if content_type:
            headers["Content-Type"] = content_type

        file_size = os.path.getsize(file_path)

        with httpx.Client(timeout=timeout, follow_redirects=follow_redirects) as client:
            with open(file_path, "rb") as f:
                resp = client.put(url, content=f, headers=headers)
            status = resp.status_code
            etag = resp.headers.get("ETag")
            return status, etag, file_size

    @staticmethod
    def _get_file_sync(
        url: str,
        dest_path: str,
        timeout: float,
        follow_redirects: bool,
        progress_cb: Optional[Callable[[int], None]],
    ) -> Tuple[int, int]:
        """
        Synchronously GET download to local file in background thread using httpx.
        Returns (status_code, bytes_received)
        """
        bytes_recv = 0
        with httpx.Client(timeout=timeout, follow_redirects=follow_redirects) as client:
            with client.stream("GET", url) as resp:
                status = resp.status_code
                if status != 200:
                    # Still consume content to release connection
                    _ = resp.read()
                    return status, 0
                with open(dest_path, "wb") as f:
                    for chunk in resp.iter_bytes():
                        if chunk:
                            f.write(chunk)
                            bytes_recv += len(chunk)
                            if progress_cb:
                                try:
                                    progress_cb(bytes_recv)
                                except Exception:
                                    pass
        return 200, bytes_recv

