"""
File transfer module for uploading and downloading files between local and OSS.
"""

import json
import os
import time
from typing import Callable, Dict, Optional, Tuple

import httpx

from agb.api.models import GetAndLoadInternalContextRequest
from agb.logger import log_api_call, log_api_response, log_operation_error
from agb.model.response import UploadResult, DownloadResult


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
        This calls GetAndLoadInternalContext with SessionId and ContextTypes=["file_transfer"].
        """
        if self.context_id:
            return True, ""

        try:
            request = GetAndLoadInternalContextRequest(
                authorization=f"Bearer {self._agb.api_key}",
                session_id=self._session.get_session_id(),
                context_types=["file_transfer"],
            )
            log_api_call("GetAndLoadInternalContext", f"SessionId={self._session.get_session_id()}, ContextTypes=file_transfer")

            client = self._agb.client
            if hasattr(client, "get_and_load_internal_context_async") and callable(
                getattr(client, "get_and_load_internal_context_async")
            ):
                response = client.get_and_load_internal_context_async(request)
            else:
                response = client.get_and_load_internal_context(request)

            # Extract context_id from response data
            # Response has structure: response.data is a list of context items
            # Each item has ContextId, ContextType, and ContextPath
            try:
                response_body = json.dumps(response.json_data, ensure_ascii=False, indent=2)
            except Exception:
                response_body = str(response.json_data)

            # Check for API-level errors
            if not response.is_successful():
                log_api_response(response_body, success=False)
                return False, response.get_error_message() or "Unknown error"

            log_api_response(response_body, success=True)

            # Get context list from response
            data = response.get_context_list()
            if isinstance(data, list) and len(data) > 0:
                for item in data:
                    if isinstance(item, dict):
                        context_id = item.get("ContextId", "")
                        context_path = item.get("ContextPath", "")
                        if context_id and context_path:
                            self.context_id = context_id
                            self.context_path = context_path
                            return True, ""
            return False, "Response contains no data"
        except Exception as e:
            log_operation_error("ensure_context_id", str(e))
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
        # 0. Parameter validation
        if not os.path.isfile(local_path):
            return UploadResult(
                success=False,
                request_id_upload_url=None,
                request_id_sync=None,
                http_status=None,
                etag=None,
                bytes_sent=0,
                path=remote_path,
                error=f"Local file not found: {local_path}",
            )
        if self.context_id is None:
            ensure_result, message = self.ensure_context_id()
            if not ensure_result:
                return UploadResult(
                    success=False,
                    request_id_upload_url=None,
                    request_id_sync=None,
                    http_status=None,
                    etag=None,
                    bytes_sent=0,
                    path=remote_path,
                    error=message,
                )
        # Ensure context_id is set
        if not self.context_id:
            return UploadResult(
                success=False,
                request_id_upload_url=None,
                request_id_sync=None,
                http_status=None,
                etag=None,
                bytes_sent=0,
                path=remote_path,
                error="Context ID not available",
            )
        # 1. Get pre-signed upload URL
        url_res = self._context_svc.get_file_upload_url(
            self.context_id, remote_path
        )
        if not getattr(url_res, "success", False) or not getattr(url_res, "url", None):
            return UploadResult(
                success=False,
                request_id_upload_url=getattr(url_res, "request_id", None),
                request_id_sync=None,
                http_status=None,
                etag=None,
                bytes_sent=0,
                path=remote_path,
                error=f"get_file_upload_url failed: {getattr(url_res, 'message', 'unknown error')}",
            )

        upload_url = url_res.url
        req_id_upload = getattr(url_res, "request_id", None)

        print(f"Uploading {local_path} to {upload_url}")

        # 2. PUT upload to pre-signed URL
        try:
            http_status, etag, bytes_sent = self._put_file_sync(upload_url,
                local_path,
                self._http_timeout,
                self._follow_redirects,
                content_type,
                progress_cb,
            )
            print(f"Upload completed with HTTP {http_status}")
            if http_status not in (200, 201, 204):
                return UploadResult(
                    success=False,
                    request_id_upload_url=req_id_upload,
                    request_id_sync=None,
                    http_status=http_status,
                    etag=etag,
                    bytes_sent=bytes_sent,
                    path=remote_path,
                    error=f"Upload failed with HTTP {http_status}",
                )
        except Exception as e:
            return UploadResult(
                success=False,
                request_id_upload_url=req_id_upload,
                request_id_sync=None,
                http_status=None,
                etag=None,
                bytes_sent=0,
                path=remote_path,
                error=f"Upload exception: {e}",
            )

        # 3. Trigger sync to cloud disk (download mode),download from oss to cloud disk
        req_id_sync = None
        try:
            print("Triggering sync to cloud disk")
            req_id_sync = self._await_sync(
                "download", remote_path, self.context_id or ""
            )
        except Exception as e:
            return UploadResult(
                success=False,
                request_id_upload_url=req_id_upload,
                request_id_sync=req_id_sync,
                http_status=http_status,
                etag=etag,
                bytes_sent=bytes_sent,
                path=remote_path,
                error=f"session.context.sync(upload) failed: {e}",
            )

        print(f"Sync request ID: {req_id_sync}")
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
                return UploadResult(
                    success=False,
                    request_id_upload_url=req_id_upload,
                    request_id_sync=req_id_sync,
                    http_status=http_status,
                    etag=etag,
                    bytes_sent=bytes_sent,
                    path=remote_path,
                    error=f"Upload sync not finished: {err or 'timeout or unknown'}",
                )

        return UploadResult(
            success=True,
            request_id_upload_url=req_id_upload,
            request_id_sync=req_id_sync,
            http_status=http_status,
            etag=etag,
            bytes_sent=bytes_sent,
            path=remote_path,
            error=None,
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
        # Use default context if none provided
        if self.context_id is None:
            ensure_result, message = self.ensure_context_id()
            if not ensure_result:
                return DownloadResult(
                    success=False,
                    request_id_download_url=None,
                    request_id_sync=None,
                    http_status=None,
                    bytes_received=0,
                    path=remote_path,
                    local_path=local_path,
                    error=message,
                )
        # Ensure context_id is set
        if not self.context_id:
            return DownloadResult(
                success=False,
                request_id_download_url=None,
                request_id_sync=None,
                http_status=None,
                bytes_received=0,
                path=remote_path,
                local_path=local_path,
                error="Context ID not available",
            )
        # 1. Trigger cloud disk to OSS download sync
        req_id_sync = None
        try:
            req_id_sync = self._await_sync(
                "upload", remote_path, self.context_id or ""
            )
        except Exception as e:
            return DownloadResult(
                success=False,
                request_id_download_url=None,
                request_id_sync=req_id_sync,
                http_status=None,
                bytes_received=0,
                path=remote_path,
                local_path=local_path,
                error=f"session.context.sync(download) failed: {e}",
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
                return DownloadResult(
                    success=False,
                    request_id_download_url=None,
                    request_id_sync=req_id_sync,
                    http_status=None,
                    bytes_received=0,
                    path=remote_path,
                    local_path=local_path,
                    error=f"Download sync not finished: {err or 'timeout or unknown'}",
                )

        # 2. Get pre-signed download URL
        url_res = self._context_svc.get_file_download_url(
            self.context_id, remote_path
        )
        if not getattr(url_res, "success", False) or not getattr(url_res, "url", None):
            return DownloadResult(
                success=False,
                request_id_download_url=getattr(url_res, "request_id", None),
                request_id_sync=req_id_sync,
                http_status=None,
                bytes_received=0,
                path=remote_path,
                local_path=local_path,
                error=f"get_file_download_url failed: {getattr(url_res, 'message', 'unknown error')}",
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
                    error=f"Destination exists and overwrite=False: {local_path}",
                )

            http_status, bytes_received = self._get_file_sync(download_url,
                local_path,
                self._http_timeout,
                self._follow_redirects,
                progress_cb,
            )
            if http_status != 200:
                return DownloadResult(
                    success=False,
                    request_id_download_url=req_id_download,
                    request_id_sync=req_id_sync,
                    http_status=http_status,
                    bytes_received=bytes_received,
                    path=remote_path,
                    local_path=local_path,
                    error=f"Download failed with HTTP {http_status}",
                )
        except Exception as e:
            return DownloadResult(
                success=False,
                request_id_download_url=req_id_download,
                request_id_sync=req_id_sync,
                http_status=None,
                bytes_received=0,
                path=remote_path,
                local_path=local_path,
                error=f"Download exception: {e}",
            )

        return DownloadResult(
            success=True,
            request_id_download_url=req_id_download,
            request_id_sync=req_id_sync,
            http_status=200,
            bytes_received=(
                os.path.getsize(local_path) if os.path.exists(local_path) else 0
            ),
            path=remote_path,
            local_path=local_path,
            error=None,
        )

    # ========== Internal Utilities ==========

    def _await_sync(
        self, mode: str, remote_path: str = "", context_id: str = ""
    ) -> Optional[str]:
        """
        Compatibility wrapper for session.context.sync_context which may be sync or async:
        - Try async call first
        - Fall back to sync call using asyncio.to_thread
        Returns request_id if available
        """
        mode = mode.lower().strip()

        sync_fn = getattr(self._session.context, "sync")
        print(
            f"session.context.sync(mode={mode}, path={remote_path}, context_id={context_id})"
        )
        # Try as coroutine with mode, path, and context_id parameters
        try:
            result = sync_fn(
                mode=mode,
                path=remote_path if remote_path else None,
                context_id=context_id if context_id else None,
            )
            out = sync_fn(mode=mode,
                    path=remote_path if remote_path else None,
                    context_id=context_id if context_id else None,
                )
        except TypeError:
            # Backend may not support all parameters, try with mode and path only
            try:
                result = sync_fn(mode=mode, path=remote_path if remote_path else None)
                out = sync_fn(mode=mode, path=remote_path if remote_path else None
                    )
            except TypeError:
                # Backend may not support mode or path parameter
                try:
                    result = sync_fn(mode=mode)
                    out = sync_fn(mode=mode)
                except TypeError:
                    # Backend may not support mode parameter
                    result = sync_fn()
                    out = sync_fn
        # Return request_id if available
        success = getattr(out, "success", False)
        print(f"   Result: {success}")
        return getattr(out, "request_id", None)

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

        while time.time() < deadline:
            try:
                info_fn = getattr(self._session.context, "info")
                # Try calling with filter parameters
                try:
                    res = info_fn(
                        context_id=context_id, path=remote_path, task_type=task_type
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
                        and path == remote_path
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

