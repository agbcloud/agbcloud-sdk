import json
from typing import Any, Callable, Dict, List, Optional
from agb.api.base_service import BaseService
from agb.model.response import ApiResponse
from agb.logger import (
    get_logger,
    log_operation_start,
    log_operation_success,
    log_operation_error,
)
from agb.model.response import (
    EnhancedCodeExecutionResult,
    ExecutionResult,
    ExecutionLogs,
    ExecutionError,
)

logger = get_logger(__name__)

# Language aliases mapping
LANGUAGE_ALIASES = {
    "py": "python",
    "python3": "python",
    "js": "javascript",
    "node": "javascript",
    "nodejs": "javascript",
}

# Supported languages set for O(1) lookup
SUPPORTED_LANGUAGES = {"python", "javascript", "java", "r"}


def _empty_result(
    request_id: str,
    success: bool,
    error_message: str,
) -> EnhancedCodeExecutionResult:
    """Create an empty result object."""
    return EnhancedCodeExecutionResult(
        request_id=request_id,
        success=success,
        error_message=error_message,
        logs=ExecutionLogs(stdout=[], stderr=[]),
        results=[],
        execution_count=None,
        execution_time=0.0,
    )


class Code(BaseService):
    """
    Handles code execution operations in the AGB cloud environment.
    """

    def _run_code(
        self,
        code: str,
        language: str,
        timeout_s: int = 60,
        stream_beta: bool = False,
        on_stdout: Optional[Callable[[str], None]] = None,
        on_stderr: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[Any], None]] = None,
    ) -> EnhancedCodeExecutionResult:
        """
        Internal implementation for code execution.

        Use the public `run()` method instead.
        """
        try:
            # Normalize and validate language (case-insensitive)
            raw_language = "" if language is None else str(language)
            normalized_language = raw_language.strip().lower()
            canonical_language = LANGUAGE_ALIASES.get(normalized_language, normalized_language)

            if canonical_language not in SUPPORTED_LANGUAGES:
                error_msg = (
                    f"Unsupported language: {raw_language}. Supported languages are "
                    f"{', '.join(sorted(SUPPORTED_LANGUAGES))}"
                )
                log_operation_error("Code.run_code", error_msg)
                return _empty_result("", False, error_msg)

            if stream_beta:
                return self._run_code_stream_ws(
                    code=code,
                    language=canonical_language,
                    timeout_s=timeout_s,
                    on_stdout=on_stdout,
                    on_stderr=on_stderr,
                    on_error=on_error,
                )

            log_operation_start(
                "Code.run_code", f"Language={canonical_language}, TimeoutS={timeout_s}"
            )

            args = {
                "code": code,
                "language": canonical_language,
                "timeout_s": timeout_s,
            }
            result = self._call_mcp_tool("run_code", args)

            if not result.success:
                error_msg = result.error_message or "Failed to run code"
                log_operation_error("Code.run_code", error_msg)
                return _empty_result(result.request_id, False, error_msg)

            # If data is already an EnhancedCodeExecutionResult, use it directly
            if isinstance(result.data, EnhancedCodeExecutionResult):
                result.data.request_id = result.request_id
                return result.data

            log_operation_success("Code.run_code", f"RequestId={result.request_id}")
            return self._parse_run_code_result(result.data, result.request_id)

        except Exception as e:
            log_operation_error("Code.run_code", str(e), exc_info=True)
            return _empty_result("", False, f"Failed to run code: {e}")

    def _run_code_stream_ws(
        self,
        *,
        code: str,
        language: str,
        timeout_s: int,
        on_stdout: Optional[Callable[[str], None]],
        on_stderr: Optional[Callable[[str], None]],
        on_error: Optional[Callable[[Any], None]],
    ) -> EnhancedCodeExecutionResult:
        """
        Execute code via WebSocket streaming.

        Internal helper for stream_beta mode.
        """
        stdout_chunks: List[str] = []
        stderr_chunks: List[str] = []
        results: List[ExecutionResult] = []
        error_obj: Optional[ExecutionError] = None
        error_reported = False

        target = self._resolve_stream_target()
        ws_client = self.session._get_ws_client()

        # ── callback helpers ──────────────────────────────────────────

        def _append_stream(chunks: List[str], callback: Optional[Callable], chunk: str) -> None:
            chunks.append(chunk)
            if callback is not None:
                callback(chunk)

        def _handle_error_payload(err_payload: Any) -> None:
            nonlocal error_obj, error_reported
            error_reported = True
            if isinstance(err_payload, dict):
                name = str(err_payload.get("code") or "ExecutionError")
                value = str(err_payload.get("message") or err_payload.get("error") or "")
                trace_id = str(err_payload.get("traceId") or "")
                error_obj = ExecutionError(
                    name=name, value=value,
                    traceback=f"traceId={trace_id}" if trace_id else "",
                )
            else:
                error_obj = ExecutionError(name="ExecutionError", value=str(err_payload), traceback="")
            if on_error is not None:
                on_error(err_payload)

        def _parse_result_event(result_payload: Any) -> None:
            if not isinstance(result_payload, dict):
                results.append(ExecutionResult(text=str(result_payload)))
                return
            is_main = bool(result_payload.get("isMainResult") or result_payload.get("is_main_result")) or False
            raw_mime = result_payload.get("mime")
            mime: Dict[str, Any] = raw_mime if isinstance(raw_mime, dict) else {}
            results.append(
                ExecutionResult(
                    text=mime.get("text/plain"),
                    html=mime.get("text/html"),
                    markdown=mime.get("text/markdown"),
                    png=mime.get("image/png"),
                    jpeg=mime.get("image/jpeg"),
                    svg=mime.get("image/svg+xml"),
                    json=mime.get("application/json"),
                    latex=mime.get("text/latex"),
                    chart=mime.get("application/vnd.vegalite.v4+json")
                    or mime.get("application/vnd.vegalite.v5+json"),
                    is_main_result=is_main,
                )
            )

        def _on_event(invocation_id: str, data: Dict[str, Any]) -> None:
            event_type = data.get("eventType")
            if event_type == "stdout":
                chunk = data.get("chunk")
                if isinstance(chunk, str):
                    _append_stream(stdout_chunks, on_stdout, chunk)
            elif event_type == "stderr":
                chunk = data.get("chunk")
                if isinstance(chunk, str):
                    _append_stream(stderr_chunks, on_stderr, chunk)
            elif event_type == "result":
                _parse_result_event(data.get("result"))
            elif event_type == "error":
                _handle_error_payload(data.get("error") or data)

        # ── execute via WebSocket ─────────────────────────────────────

        try:
            handle = ws_client.call_stream(
                target=target,
                data={
                    "method": "run_code",
                    "mode": "stream",
                    "params": {"language": language, "timeoutS": timeout_s, "code": code},
                },
                on_event=_on_event,
                on_end=None,
                on_error=lambda _inv, err: _handle_error_payload(err),
            )

            end_data = handle.wait_end()

            exec_count = end_data.get("executionCount")
            execution_count = exec_count if isinstance(exec_count, int) else None
            execution_time = float(end_data.get("executionTime") or 0.0)

            execution_error = end_data.get("executionError")
            if execution_error and error_obj is None:
                error_obj = ExecutionError(name="ExecutionError", value=str(execution_error), traceback="")

            ok = error_obj is None and not execution_error and end_data.get("status") != "failed"
            err_msg = "" if ok else (
                str(execution_error) if execution_error
                else (error_obj.value if error_obj else "")
            )

            return EnhancedCodeExecutionResult(
                request_id=handle.invocation_id,
                success=ok,
                execution_count=execution_count,
                execution_time=execution_time,
                logs=ExecutionLogs(stdout=stdout_chunks, stderr=stderr_chunks),
                results=results,
                error=error_obj,
                error_message=err_msg,
            )
        except Exception as e:
            if on_error is not None and not error_reported:
                on_error(e)
            return EnhancedCodeExecutionResult(
                request_id="",
                success=False,
                logs=ExecutionLogs(stdout=stdout_chunks, stderr=stderr_chunks),
                results=results,
                error=error_obj,
                error_message=str(e),
            )

    def _resolve_stream_target(self) -> str:
        """Resolve the WebSocket stream target from the session's tool list."""
        for tool in getattr(self.session, "tool_list", []) or []:
            try:
                if getattr(tool, "name", "") == "run_code" and getattr(tool, "server", ""):
                    return str(tool.server)
            except Exception:
                continue
        return "wuying_codespace"

    def run(
        self,
        code: str,
        language: str,
        timeout_s: int = 60,
        stream_beta: bool = False,
        on_stdout: Optional[Callable[[str], None]] = None,
        on_stderr: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[Any], None]] = None,
    ) -> EnhancedCodeExecutionResult:
        """
        Execute code in the specified language with a timeout.

        This is the primary public method for code execution. For real-time
        streaming output, set stream_beta=True and provide callback functions.

        Args:
            code: The code to execute.
            language: The programming language of the code. Case-insensitive.
                Supported values: 'python', 'javascript', 'r', 'java'.
                Aliases: 'py' -> 'python', 'js'/'node' -> 'javascript'.
            timeout_s: The timeout for the code execution in seconds. Default is 60s.
            stream_beta: If True, use WebSocket streaming for real-time stdout/stderr
                output. Requires the session to have a valid ws_url. Default is False.
            on_stdout: Callback invoked with each stdout chunk during streaming.
                Only used when stream_beta=True.
            on_stderr: Callback invoked with each stderr chunk during streaming.
                Only used when stream_beta=True.
            on_error: Callback invoked when an error occurs during streaming.
                Only used when stream_beta=True.

        Returns:
            EnhancedCodeExecutionResult: Result object containing success status,
                execution results with rich format support (HTML, images, charts, etc.),
                logs, and error information if any.
        """
        return self._run_code(code, language, timeout_s, stream_beta, on_stdout, on_stderr, on_error)

    def _parse_run_code_result(
        self, data: Any, request_id: str
    ) -> EnhancedCodeExecutionResult:
        """
        Parse run_code tool responses, supporting multiple response formats.

        Args:
            data: Raw response data from the tool
            request_id: Request ID to set in the result

        Returns:
            EnhancedCodeExecutionResult: Parsed code execution result
        """
        if not data:
            return _empty_result(request_id, False, "No data returned")

        # Parse data into dictionary format uniformly
        response_data = self._parse_to_dict(data)
        if not isinstance(response_data, dict):
            # If not a dict, treat as simple text result
            text = str(data)
            return EnhancedCodeExecutionResult(
                request_id=request_id,
                success=True,
                results=[ExecutionResult(text=text, is_main_result=True)],
                logs=ExecutionLogs(stdout=[text], stderr=[]),
                error_message="",
                execution_count=None,
                execution_time=0.0,
            )

        # Check if response is in legacy format where JSON is in content[0].text
        content = response_data.get("content", [])
        if content and isinstance(content, list) and len(content) > 0:
            content_item = content[0]
            text_string = content_item.get("text")
            if text_string:
                try:
                    parsed_json = json.loads(text_string)
                    if isinstance(parsed_json, dict) and ("result" in parsed_json or "executionError" in parsed_json):
                        response_data = parsed_json
                except json.JSONDecodeError:
                    pass

        d = response_data

        # Check for error response
        if d.get("isError", False):
            error_content = d.get("content", [])
            error_message = "; ".join(
                item.get("text", "Unknown error")
                for item in error_content
                if isinstance(item, dict)
            )
            return _empty_result(request_id, False, f"Error in response: {error_message}")

        # Check formats by priority and parse
        if "result" in d and isinstance(d["result"], list):
            return self._parse_new_format(d, request_id)
        if "logs" in d or "results" in d:
            return self._parse_rich_format(d, request_id)
        if "content" in d:
            return self._parse_legacy_format(d, request_id)

        # Default fallback
        text = str(response_data)
        return EnhancedCodeExecutionResult(
            request_id=request_id,
            success=True,
            results=[ExecutionResult(text=text, is_main_result=True)],
            logs=ExecutionLogs(stdout=[text], stderr=[]),
            error_message="",
            execution_count=None,
            execution_time=0.0,
        )

    def _parse_to_dict(self, data: Any) -> Any:
        """Parse data into dictionary format."""
        if isinstance(data, dict):
            return data
        if isinstance(data, str):
            try:
                return json.loads(data.strip())
            except json.JSONDecodeError:
                return data
        return data

    def _parse_new_format(
        self, d: Dict[str, Any], request_id: str
    ) -> EnhancedCodeExecutionResult:
        """Parse new format response: format containing result, stdout, stderr."""
        logs = ExecutionLogs(
            stdout=d.get("stdout", []),
            stderr=d.get("stderr", []),
        )

        results = []
        for item in d.get("result", []):
            parsed = self._parse_result_item(item)
            if parsed:
                results.append(parsed)

        # Parse error if present
        error_obj = None
        exec_error = d.get("executionError")
        if exec_error:
            error_obj = ExecutionError(
                name="ExecutionError",
                value=str(exec_error),
                traceback=""
            )

        return EnhancedCodeExecutionResult(
            request_id=request_id,
            execution_count=d.get("execution_count"),
            execution_time=d.get("execution_time", 0.0),
            logs=logs,
            results=results,
            error=error_obj,
            error_message=str(exec_error) if exec_error else "",
            success=not bool(exec_error) and not d.get("isError", False),
        )

    def _parse_result_item(self, item: Any) -> Optional[ExecutionResult]:
        """Parse single result item."""
        if isinstance(item, dict):
            return ExecutionResult(
                text=item.get("text/plain") or item.get("text"),
                html=item.get("text/html") or item.get("html"),
                markdown=item.get("text/markdown") or item.get("markdown"),
                png=item.get("image/png") or item.get("png"),
                jpeg=item.get("image/jpeg") or item.get("jpeg"),
                svg=item.get("image/svg+xml") or item.get("svg"),
                json=item.get("application/json") or item.get("json"),
                latex=item.get("text/latex") or item.get("latex"),
                chart=(
                    item.get("application/vnd.vegalite.v4+json")
                    or item.get("application/vnd.vegalite.v5+json")
                    or item.get("chart")
                ),
                is_main_result=item.get("isMainResult", False) or item.get("is_main_result", False),
            )

        if isinstance(item, str):
            try:
                parsed = json.loads(item)
                # Handle double encoding
                if isinstance(parsed, str):
                    try:
                        parsed = json.loads(parsed)
                    except json.JSONDecodeError:
                        pass
                if isinstance(parsed, dict):
                    return self._parse_result_item(parsed)
                return ExecutionResult(text=str(parsed), is_main_result=False)
            except json.JSONDecodeError:
                return ExecutionResult(text=item, is_main_result=False)

        return ExecutionResult(text=str(item), is_main_result=False)

    def _parse_rich_format(
        self, d: Dict[str, Any], request_id: str
    ) -> EnhancedCodeExecutionResult:
        """Parse rich response format: format containing logs, results."""
        logs_data = d.get("logs", {})
        logs = ExecutionLogs(
            stdout=logs_data.get("stdout", []),
            stderr=logs_data.get("stderr", []),
        )

        results = []
        for item in d.get("results", []):
            results.append(ExecutionResult(
                text=item.get("text"),
                html=item.get("html"),
                markdown=item.get("markdown"),
                png=item.get("png"),
                jpeg=item.get("jpeg"),
                svg=item.get("svg"),
                json=item.get("json"),
                latex=item.get("latex"),
                chart=item.get("chart"),
                is_main_result=item.get("is_main_result", False),
            ))

        # Parse error if present
        error_obj = None
        error_data = d.get("error")
        error_message = ""
        if error_data:
            error_obj = ExecutionError(
                name=error_data.get("name", "UnknownError"),
                value=error_data.get("value", ""),
                traceback=error_data.get("traceback", "")
            )
            error_message = error_data.get("value", "") or error_data.get("name", "UnknownError")

        return EnhancedCodeExecutionResult(
            request_id=request_id,
            execution_count=d.get("execution_count"),
            execution_time=d.get("execution_time", 0.0),
            logs=logs,
            results=results,
            error=error_obj,
            error_message=error_message,
            success=not d.get("isError", False),
        )

    def _parse_legacy_format(
        self, d: Dict[str, Any], request_id: str
    ) -> EnhancedCodeExecutionResult:
        """Parse legacy format: content array format."""
        content = d.get("content", [])
        if content and isinstance(content, list):
            text = content[0].get("text")
            if text is not None:
                return EnhancedCodeExecutionResult(
                    request_id=request_id,
                    success=True,
                    logs=ExecutionLogs(stdout=[text], stderr=[]),
                    results=[ExecutionResult(text=text, is_main_result=True)],
                    error_message="",
                    execution_count=None,
                    execution_time=0.0,
                )

        return _empty_result(request_id, False, "No content found in response")
