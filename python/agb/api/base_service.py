import json
import random
import time
from typing import Any, Dict, Optional

from agb.api.models import CallMcpToolRequest
from agb.exceptions import AGBError
from agb.model import OperationResult
from agb.logger import get_logger, log_operation_start, log_operation_success, log_operation_error

logger = get_logger(__name__)


class BaseService:
    """
    Base service class that provides common functionality for all service classes.
    This class implements the common methods for calling MCP tools and parsing
    responses.
    """

    def __init__(self, session):
        """
        Initialize a BaseService object.

        Args:
            session: The Session instance that this service belongs to.
        """
        self.session = session

    def _handle_error(self, e):
        """
        Handle and convert exceptions. This method should be overridden by subclasses
        to provide specific error handling.

        Args:
            e (Exception): The exception to handle.

        Returns:
            Exception: The handled exception.
        """
        return e

    def _get_mcp_server_for_tool(self, tool_name: str) -> Optional[str]:
        """
        Resolve MCP server name by tool name from session tool list.

        Args:
            tool_name (str): The name of the tool.

        Returns:
            Optional[str]: Server name if found, otherwise None.
        """
        try:
            tool_list = getattr(self.session, "tool_list", None) or []
            for t in tool_list:
                if t and getattr(t, "name", None) == tool_name:
                    server = getattr(t, "server", "") or ""
                    logger.debug(f"Server: {server}")
                    return server if server else None
        except Exception as e:
            logger.debug(f"Failed to resolve server for tool {tool_name}: {e}")
        return None

    def _call_mcp_tool_link_url(
        self,
        tool_name: str,
        args: Dict[str, Any],
        server_name: str,
    ) -> OperationResult:
        """
        Call MCP tool via LinkUrl route (direct HTTP call).

        Args:
            tool_name (str): The name of the tool to call.
            args (Dict[str, Any]): The arguments to pass to the tool.
            server_name (str): The MCP server name.

        Returns:
            OperationResult: Tool call result.
        """
        try:
            import httpx
        except ImportError:
            return OperationResult(
                request_id="",
                success=False,
                error_message="httpx library not available, please install it: pip install httpx",
            )

        link_url = getattr(self.session, "link_url", "") or ""
        token = getattr(self.session, "token", "") or ""

        if not link_url or not token:
            return OperationResult(
                request_id="",
                success=False,
                error_message="LinkUrl/token not available",
            )

        request_id = f"link-{int(time.time() * 1000)}-{random.randint(0, 999999999):09d}"

        log_operation_start(
            "BaseService._call_mcp_tool_link_url",
            f"Tool={tool_name}, SessionId={self.session.get_session_id()}, RequestId={request_id}",
        )

        url = link_url.rstrip("/") + "/callTool"
        payload = {
            "args": args,
            "server": server_name,
            "requestId": request_id,
            "tool": tool_name,
            "token": token,
        }

        try:
            with httpx.Client(timeout=900) as client:
                resp = client.post(
                    url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Access-Token": token,
                    },
                )

            if resp.status_code < 200 or resp.status_code >= 300:
                error_msg = f"HTTP request failed with code: {resp.status_code}"
                log_operation_error(
                    "BaseService._call_mcp_tool_link_url", error_msg)
                return OperationResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_msg,
                )

            outer = resp.json()
            data_field = outer.get("data")
            if data_field is None:
                error_msg = "No data field in LinkUrl response"
                log_operation_error(
                    "BaseService._call_mcp_tool_link_url", error_msg)
                return OperationResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_msg,
                )

            if isinstance(data_field, str):
                parsed_data = json.loads(data_field)
            elif isinstance(data_field, dict):
                parsed_data = data_field
            else:
                error_msg = "Invalid data field type in LinkUrl response"
                log_operation_error(
                    "BaseService._call_mcp_tool_link_url", error_msg)
                return OperationResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_msg,
                )

            result_field = parsed_data.get("result", {})
            if not isinstance(result_field, dict):
                error_msg = "No result field in LinkUrl response data"
                log_operation_error(
                    "BaseService._call_mcp_tool_link_url", error_msg)
                return OperationResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_msg,
                )

            is_error = bool(result_field.get("isError", False))
            content = result_field.get("content", [])
            text_content = ""
            if isinstance(content, list) and len(content) > 0:
                first = content[0]
                if isinstance(first, str):
                    text_content = first
                elif isinstance(first, dict):
                    text_content = first.get("text") or first.get(
                        "blob") or first.get("data") or ""

            if is_error:
                log_operation_error(
                    "BaseService._call_mcp_tool_link_url", str(text_content))
                return OperationResult(
                    request_id=request_id,
                    success=False,
                    error_message=str(text_content),
                )

            log_operation_success(
                "BaseService._call_mcp_tool_link_url",
                f"Tool={tool_name}, SessionId={self.session.get_session_id()}, RequestId={request_id}",
            )
            return OperationResult(
                request_id=request_id,
                success=True,
                data=str(text_content),
            )
        except Exception as e:
            error_msg = f"HTTP request failed: {e}"
            log_operation_error(
                "BaseService._call_mcp_tool_link_url", error_msg, exc_info=True)
            return OperationResult(
                request_id=request_id,
                success=False,
                error_message=error_msg,
            )

    def _call_mcp_tool_api(
        self,
        name: str,
        args: Dict[str, Any],
        read_timeout: Optional[int] = None,
        connect_timeout: Optional[int] = None,
    ) -> OperationResult:
        """
        Call MCP tool via traditional API route.

        Args:
            name (str): The name of the tool to call.
            args (Dict[str, Any]): The arguments to pass to the tool.
            read_timeout (Optional[int]): Read timeout in milliseconds.
            connect_timeout (Optional[int]): Connect timeout in milliseconds.

        Returns:
            OperationResult: The response from the tool with request ID.
        """
        try:
            args_json = json.dumps(args, ensure_ascii=False)

            request = CallMcpToolRequest(
                authorization=f"Bearer {self.session.get_api_key()}",
                session_id=self.session.get_session_id(),
                name=name,
                args=args_json,
            )
            response = self.session.get_client().call_mcp_tool(
                request, read_timeout=read_timeout, connect_timeout=connect_timeout
            )

            if response is None:
                return OperationResult(
                    request_id="",
                    success=False,
                    error_message="OpenAPI client returned None response",
                )

            request_id = response.request_id or ""

            if hasattr(response, "is_successful"):
                try:
                    logger.debug("Response body:")
                    logger.debug(
                        json.dumps(response.json_data,
                                   ensure_ascii=False, indent=2)
                    )
                except Exception:
                    logger.debug(f"Response: {response}")

                # Treat the call as successful only when BOTH API layer and tool layer are successful.
                # This prevents false positives where the tool payload looks OK but the API wrapper
                # reports an error (e.g. InvalidSession.NotFound).
                if response.is_successful():
                    result = response.get_tool_result()
                    return OperationResult(
                        request_id=request_id, success=True, data=result
                    )

                error_msg = response.get_error_message() or "Tool execution failed"
                return OperationResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_msg,
                )
            else:
                error_msg = "Unsupported response type"
                return OperationResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_msg,
                )

        except AGBError as e:
            handled_error = self._handle_error(e)
            request_id = "" if "request_id" not in locals() else request_id
            return OperationResult(
                request_id=request_id,
                success=False,
                error_message=str(handled_error),
            )
        except Exception as e:
            handled_error = self._handle_error(e)
            request_id = "" if "request_id" not in locals() else request_id
            return OperationResult(
                request_id=request_id,
                success=False,
                error_message=f"Failed to call MCP tool {name}: {handled_error}",
            )

    def _call_mcp_tool(
        self,
        name: str,
        args: Dict[str, Any],
        read_timeout: Optional[int] = None,
        connect_timeout: Optional[int] = None,
    ) -> OperationResult:
        """
        Internal helper to call MCP tool with intelligent routing.

        This method routes the call to either:
        1. LinkUrl route (direct HTTP) - when link_url, token, and server_name are available
        2. Traditional API route - fallback method

        Args:
            name (str): The name of the tool to call.
            args (Dict[str, Any]): The arguments to pass to the tool.
            read_timeout (Optional[int]): Read timeout in milliseconds.
            connect_timeout (Optional[int]): Connect timeout in milliseconds.

        Returns:
            OperationResult: The response from the tool with request ID.
        """
        # Try to resolve server name from tool list
        server_name = self._get_mcp_server_for_tool(name) or ""

        # Check if we can use LinkUrl route
        link_url = getattr(self.session, "link_url", "") or ""
        token = getattr(self.session, "token", "") or ""

        if link_url and token and server_name:
            logger.debug(f"Using LinkUrl route for tool: {name}")
            return self._call_mcp_tool_link_url(name, args, server_name)
        else:
            # Fallback to traditional API route
            logger.debug(f"Using API route for tool: {name}")
            return self._call_mcp_tool_api(
                name, args, read_timeout=read_timeout, connect_timeout=connect_timeout
            )
