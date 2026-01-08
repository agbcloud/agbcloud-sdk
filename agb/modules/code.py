import json
from typing import Any, Dict, Optional
from agb.api.base_service import BaseService
from agb.model.response import ApiResponse
from agb.logger import get_logger, log_operation_start, log_operation_success, log_operation_error, log_warning
from agb.model.response import EnhancedCodeExecutionResult, ExecutionResult, ExecutionLogs

logger = get_logger(__name__)

class Code(BaseService):
    """
    Handles code execution operations in the AGB cloud environment.
    """

    def run_code(
        self, code: str, language: str, timeout_s: int = 60
    ) -> EnhancedCodeExecutionResult:
        """
        Execute code in the specified language with a timeout.

        Args:
            code (str): The code to execute.
            language (str): The programming language of the code. Supported languages are:
                'python', 'javascript', 'java', 'r'.
            timeout_s (int): The timeout for the code execution in seconds. Default is 60s.

        Returns:
            EnhancedCodeExecutionResult: Enhanced result object containing success status, 
                execution results with rich format support (HTML, images, charts, etc.), 
                logs, and error information if any.

        Raises:
            CommandError: If the code execution fails or if an unsupported language is
                specified.
        """
        try:
            # Convert language to lowercase for consistent processing
            language = language.lower()

            # Language aliases mapping
            aliases = {
                "python3": "python",
                "js": "javascript",
                "node": "javascript",
                "nodejs": "javascript",
            }
            canonical_language = aliases.get(language, language)

            # Validate language
            supported_languages = {"python", "javascript", "java", "r"}
            if canonical_language not in supported_languages:
                error_msg = f"Unsupported language: {language}. Supported languages are: {', '.join(supported_languages)}"
                log_operation_error("Code.run_code", error_msg)
                return EnhancedCodeExecutionResult(
                    request_id="",
                    success=False,
                    error_message=f"Unsupported language: {language}. Supported languages are: {', '.join(supported_languages)}",
                    logs=ExecutionLogs(stdout=[], stderr=[]),
                    results=[],
                    execution_count=None,
                    execution_time=0.0
                )
            log_operation_start("Code.run_code", f"Language={language}, TimeoutS={timeout_s}, Code={code}")
            args = {"code": code, "language": canonical_language, "timeout_s": timeout_s}
            result = self._call_mcp_tool("run_code", args)
            
            if result.success:
                # result_msg = f"RequestId={result.request_id}, ResultLength={result.data if result.data else 0}"
                # log_operation_success("Code.run_code", result_msg)
                # Parse the run_code specific result format
                log_operation_success("Code.run_code", f"ResponseData={result.data}")
                parsed_result = self._parse_run_code_result(result.data, result.request_id)
                return parsed_result
            else:
                error_msg = result.error_message or "Failed to run code"
                log_operation_error("Code.run_code", error_msg)
                return EnhancedCodeExecutionResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to run code",
                    logs=ExecutionLogs(stdout=[], stderr=[]),
                    results=[],
                    execution_count=None,
                    execution_time=0.0
                )
        except Exception as e:
            log_operation_error("Code.run_code", str(e), exc_info=True)
            return EnhancedCodeExecutionResult(
                request_id="",
                success=False,
                error_message=f"Failed to run code: {e}",
                logs=ExecutionLogs(stdout=[], stderr=[]),
                results=[],
                execution_count=None,
                execution_time=0.0
            )

    def _parse_run_code_result(self, data: Any, request_id: str) -> EnhancedCodeExecutionResult:
        """
        Parse run_code tool responses, supporting multiple response formats
        
        Args:
            data: Raw response data from the tool
            request_id: Request ID to set in the result
            
        Returns:
            EnhancedCodeExecutionResult: Parsed code execution result
        """
        try:
            if not data:
                return EnhancedCodeExecutionResult(
                    request_id=request_id,
                    success=False,
                    logs=ExecutionLogs(stdout=[], stderr=[]),
                    results=[],
                    error_message="No data returned",
                    execution_count=None,
                    execution_time=0.0
                )
            
            # Parse data into dictionary format uniformly
            response_data = self._parse_to_dict(data)
            if not isinstance(response_data, dict):
                # If not a dict, treat as simple text result
                return EnhancedCodeExecutionResult(
                    request_id=request_id,
                    success=True,
                    results=[ExecutionResult(text=str(data), is_main_result=True)],
                    logs=ExecutionLogs(stdout=[str(data)], stderr=[]),
                    error_message="",
                    execution_count=None,
                    execution_time=0.0
                )
            
            # Check formats by priority and parse
            format_handlers = [
                ("result", lambda d: "result" in d and isinstance(d["result"], list), self._parse_new_format),
                ("rich", lambda d: "logs" in d or "results" in d, self._parse_rich_format),
                ("legacy", lambda d: "content" in d, self._parse_legacy_format)
            ]
            
            for name, checker, handler in format_handlers:
                if checker(response_data):
                    result = handler(response_data, request_id)
                    return result
            
            # Default fallback
            return EnhancedCodeExecutionResult(
                request_id=request_id,
                success=True,
                results=[ExecutionResult(text=str(response_data), is_main_result=True)],
                logs=ExecutionLogs(stdout=[str(response_data)], stderr=[]),
                error_message="",
                execution_count=None,
                execution_time=0.0
            )
                
        except Exception as e:
            return EnhancedCodeExecutionResult(
                request_id=request_id,
                success=False,
                logs=ExecutionLogs(stdout=[], stderr=[]),
                results=[],
                error_message=f"Parse error: {str(e)}. Original result: {data}",
                execution_count=None,
                execution_time=0.0
            )
    
    def _parse_to_dict(self, data: Any) -> Any:
        """Parse data into dictionary format"""
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return data
    
    def _parse_new_format(self, response_data: Dict[str, Any], request_id: str) -> EnhancedCodeExecutionResult:
        """Parse new format response: format containing result, stdout, stderr"""
        # Parse logs
        logs = ExecutionLogs(
            stdout=response_data.get("stdout", []),
            stderr=response_data.get("stderr", [])
        )
        
        # Parse result array
        results = []
        for res_item in response_data.get("result", []):
            parsed_item = self._parse_result_item(res_item)
            if parsed_item:
                results.append(parsed_item)
        
        # Check execution error
        error_message = ""
        execution_error = response_data.get("executionError")
        if execution_error:
            error_message = str(execution_error)
        
        # Return EnhancedCodeExecutionResult object
        return EnhancedCodeExecutionResult(
            request_id=request_id,
            execution_count=response_data.get("execution_count"),
            execution_time=response_data.get("execution_time", 0.0),
            logs=logs,
            results=results,
            error_message=error_message,
            success=not bool(execution_error)
        )
    
    def _parse_result_item(self, res_item: Any) -> Optional[ExecutionResult]:
        """Parse single result item"""
        # If already a dictionary, process directly
        if isinstance(res_item, dict):
            return ExecutionResult(
                text=res_item.get("text/plain") or res_item.get("text"),
                html=res_item.get("text/html") or res_item.get("html"),
                markdown=res_item.get("text/markdown") or res_item.get("markdown"),
                png=res_item.get("image/png") or res_item.get("png"),
                jpeg=res_item.get("image/jpeg") or res_item.get("jpeg"),
                svg=res_item.get("image/svg+xml") or res_item.get("svg"),
                json=res_item.get("application/json") or res_item.get("json"),
                latex=res_item.get("text/latex") or res_item.get("latex"),
                chart=(res_item.get("application/vnd.vegalite.v4+json") or 
                      res_item.get("application/vnd.vegalite.v5+json") or 
                      res_item.get("chart")),
                is_main_result=(res_item.get("isMainResult", False) or 
                               res_item.get("is_main_result", False))
            )
        
        # If it's a string, try to parse JSON
        elif isinstance(res_item, str):
            try:
                parsed_item = json.loads(res_item)
                # Handle double encoding
                if isinstance(parsed_item, str):
                    try:
                        parsed_item = json.loads(parsed_item)
                    except json.JSONDecodeError:
                        pass
                
                # Recursively call to process parsed object
                if isinstance(parsed_item, dict):
                    return self._parse_result_item(parsed_item)
                else:
                    return ExecutionResult(text=str(parsed_item), is_main_result=False)
                    
            except json.JSONDecodeError:
                # If not JSON, treat as plain text
                return ExecutionResult(text=str(res_item), is_main_result=False)
        
        # Other types, convert to string
        else:
            return ExecutionResult(text=str(res_item), is_main_result=False)
    
    def _parse_rich_format(self, response_data: Dict[str, Any], request_id: str) -> EnhancedCodeExecutionResult:
        """Parse rich response format: format containing logs, results"""
        # Parse logs
        logs_data = response_data.get("logs", {})
        logs = ExecutionLogs(
            stdout=logs_data.get("stdout", []),
            stderr=logs_data.get("stderr", [])
        )
        
        # Parse results
        results = []
        for res_data in response_data.get("results", []):
            result_obj = ExecutionResult(
                text=res_data.get("text"),
                html=res_data.get("html"),
                markdown=res_data.get("markdown"),
                png=res_data.get("png"),
                jpeg=res_data.get("jpeg"),
                svg=res_data.get("svg"),
                json=res_data.get("json"),
                latex=res_data.get("latex"),
                chart=res_data.get("chart"),
                is_main_result=res_data.get("is_main_result", False)
            )
            results.append(result_obj)
        
        # Parse error
        error_message = ""
        error_data = response_data.get("error")
        if error_data:
            error_message = error_data.get("value", "") or error_data.get("name", "UnknownError")
        
        return EnhancedCodeExecutionResult(
            request_id=request_id,
            execution_count=response_data.get("execution_count"),
            execution_time=response_data.get("execution_time", 0.0),
            logs=logs,
            results=results,
            error_message=error_message,
            success=not response_data.get("isError", False)
        )
    
    def _parse_legacy_format(self, response_data: Dict[str, Any], request_id: str) -> EnhancedCodeExecutionResult:
        """Parse legacy format: content array format"""
        content = response_data.get("content", [])
        if content and isinstance(content, list):
            content_item = content[0]
            text_string = content_item.get("text")
            if text_string is not None:
                # Wrap as unified format
                return EnhancedCodeExecutionResult(
                    request_id=request_id,
                    success=True,
                    logs=ExecutionLogs(stdout=[text_string], stderr=[]),
                    results=[ExecutionResult(text=text_string, is_main_result=True)],
                    error_message="",
                    execution_count=None,
                    execution_time=0.0
                )
        
        # If no content found, return empty result
        return EnhancedCodeExecutionResult(
            request_id=request_id,
            success=False,
            logs=ExecutionLogs(stdout=[], stderr=[]),
            results=[],
            error_message="No content found in response",
            execution_count=None,
            execution_time=0.0
        )
