import json
import requests
import time
import random
import string
from typing import Any, Dict

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

    def _call_mcp_tool(self, name: str, args: Dict[str, Any], read_timeout: int = None, connect_timeout: int = None) -> OperationResult:
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
            response = self.session.get_client().call_mcp_tool(request, read_timeout=read_timeout, connect_timeout=connect_timeout)

            # Check if response is empty
            if response is None:
                return OperationResult(
                    request_id="",
                    success=False,
                    error_message="OpenAPI client returned None response",
                )

            request_id = response.request_id or ""

            # Check response type, if it's CallMcpToolResponse, use new parsing method
            if hasattr(response, 'is_tool_successful'):
                # This is a CallMcpToolResponse object
                try:
                    print("Response body:")
                    print(json.dumps(response.json_data, ensure_ascii=False, indent=2))
                except Exception:
                    print(f"Response: {response}")

                if response.is_tool_successful():
                    # Tool execution successful
                    print("response.json_data =", response.json_data)
                    result = self._parse_response_body(response.json_data or {})
                    return OperationResult(request_id=request_id, success=True, data=result)
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

    def _sanitize_error(self, error_str: str) -> str:
        """
        Sanitizes error messages to remove sensitive information like API keys.

        Args:
            error_str (str): The error string to sanitize.

        Returns:
            str: The sanitized error string.
        """
        import re

        if not error_str:
            return error_str

        # Remove API key from URLs
        # Pattern: apiKey=akm-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        api_key_pattern = re.compile(r'apiKey=akm-[a-f0-9-]+')
        error_str = api_key_pattern.sub('apiKey=***REDACTED***', error_str)

        # Remove API key from Bearer tokens
        # Pattern: Bearer akm-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        bearer_pattern = re.compile(r'Bearer akm-[a-f0-9-]+')
        error_str = bearer_pattern.sub('Bearer ***REDACTED***', error_str)

        # Remove API key from query parameters
        # Pattern: &apiKey=akm-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        query_pattern = re.compile(r'&apiKey=akm-[a-f0-9-]+')
        error_str = query_pattern.sub('&apiKey=***REDACTED***', error_str)

        # Remove API key from URL paths
        # Pattern: /callTool?apiKey=akm-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        url_pattern = re.compile(r'/callTool\?apiKey=akm-[a-f0-9-]+')
        error_str = url_pattern.sub('/callTool?apiKey=***REDACTED***', error_str)

        return error_str

    def _parse_response_body(
        self, body: Dict[str, Any], parse_json: bool = False
    ) -> Any:
        """
        Parses the response body from the MCP tool.

        Args:
            body (Dict[str, Any]): The response body.
            parse_json (bool, optional): Whether to parse the text as JSON.
            Defaults to False.

        Returns:
            Any: The parsed content. If parse_json is True, returns the parsed
                 JSON object; otherwise returns the raw text.


        Raises:
            AGBError: If the response contains errors or is invalid.
        """
        try:
            response_data = body.get("data", {})
            if response_data.get("isError", False):
                error_content = response_data.get("content", [])
                try:
                    print("error_content =")
                    print(json.dumps(error_content, ensure_ascii=False, indent=2))
                except Exception:
                    print(f"error_content: {error_content}")
                error_message = "; ".join(
                    item.get("text", "Unknown error")
                    for item in error_content
                    if isinstance(item, dict)
                )
                raise AGBError(f"Error in response: {error_message}")


            if not response_data:
                raise AGBError("No data field in response")

            # Handle 'content' field for other methods
            content = response_data.get("content", [])
            if not content or not isinstance(content, list):
                raise AGBError("No content found in response")

            content_item = content[0]
            text_string = content_item.get("text")

            # Allow text field to be empty string
            if text_string is None:
                raise AGBError("Text field not found in response")

            return text_string

        except AGBError as e:
            # Transform AGBError to the expected type
            handled_error = self._handle_error(e)
            raise handled_error
        except Exception as e:
            # Transform AGBError to the expected type
            handled_error = self._handle_error(
                AGBError(f"Error parsing response body: {e}")
            )
            raise handled_error
