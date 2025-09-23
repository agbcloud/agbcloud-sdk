import json
import random
import string
import time
from typing import Any, Dict, Optional

import requests

from agb.api.models import CallMcpToolRequest
from agb.exceptions import AGBError
from agb.model import OperationResult


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

    def _call_mcp_tool(
        self,
        name: str,
        args: Dict[str, Any],
        read_timeout: Optional[int] = None,
        connect_timeout: Optional[int] = None,
    ) -> OperationResult:
        """
        Internal helper to call MCP tool and handle errors.

        Args:
            name (str): The name of the tool to call.
            args (Dict[str, Any]): The arguments to pass to the tool.

        Returns:
            OperationResult: The response from the tool with request ID.
        """
        try:
            args_json = json.dumps(args, ensure_ascii=False)

            # use traditional API call
            request = CallMcpToolRequest(
                authorization=f"Bearer {self.session.get_api_key()}",
                session_id=self.session.get_session_id(),
                name=name,
                args=args_json,
            )
            response = self.session.get_client().call_mcp_tool(
                request, read_timeout=read_timeout, connect_timeout=connect_timeout
            )

            # Check if response is empty
            if response is None:
                return OperationResult(
                    request_id="",
                    success=False,
                    error_message="OpenAPI client returned None response",
                )

            request_id = response.request_id or ""

            # Check response type, if it's CallMcpToolResponse, use new parsing method
            if hasattr(response, "is_tool_successful"):
                # This is a CallMcpToolResponse object
                try:
                    print("Response body:")
                    print(json.dumps(response.json_data, ensure_ascii=False, indent=2))
                except Exception:
                    print(f"Response: {response}")

                if response.is_tool_successful():
                    # Tool execution successful
                    result = response.get_tool_result()
                    return OperationResult(
                        request_id=request_id, success=True, data=result
                    )
                else:
                    # Tool execution failed
                    error_msg = response.get_error_message() or "Tool execution failed"
                    return OperationResult(
                        request_id=request_id,
                        success=False,
                        error_message=error_msg,
                    )
            else:
                # This is the original OpenAPI response object, use existing parsing method
                # Here you can add existing parsing logic if needed
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
