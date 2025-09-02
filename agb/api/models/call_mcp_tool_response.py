from typing import Optional, Union, List, Dict, Any


class CallMcpToolResponse:
    """Response object for calling MCP tools"""

    def __init__(
        self,
        status_code: int,
        url: str,
        headers: Dict[str, str],
        success: bool,
        json_data: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        error: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        self.status_code = status_code
        self.url = url
        self.headers = headers
        self.success = success
        self.json_data = json_data
        self.text = text
        self.error = error
        self.request_id = request_id

        # Parse fields from JSON data
        if json_data:
            self.api_success = json_data.get('success')
            self.code = json_data.get('code')
            self.message = json_data.get('message')
            self.http_status_code = json_data.get('httpStatusCode')
            self.access_denied_detail = json_data.get('accessDeniedDetail')
            self.data = json_data.get('data', {})

            # Check if tool execution was successful
            self.tool_success = not self.data.get('isError', False) if self.data else True

            # Get tool execution result
            if self.data and not self.data.get('isError', False):
                # Tool execution successful, try to get result
                content = self.data.get('content', [])
                if content and isinstance(content, list):
                    # Extract text content
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            text_parts.append(item.get('text', ''))
                    self.result = '\n'.join(text_parts) if text_parts else None
                else:
                    self.result = None
            else:
                # Tool execution failed, get error information
                content = self.data.get('content', []) if self.data else []
                if content and isinstance(content, list):
                    error_parts = []
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            error_parts.append(item.get('text', ''))
                    self.result = '\n'.join(error_parts) if error_parts else None
                else:
                    self.result = None

            self.output = self.result  # Maintain backward compatibility
        else:
            self.api_success = None
            self.code = None
            self.message = None
            self.http_status_code = None
            self.access_denied_detail = None
            self.data = None
            self.tool_success = False
            self.result = None
            self.output = None

    @classmethod
    def from_http_response(cls, response_dict: Dict[str, Any]) -> 'CallMcpToolResponse':
        """Create CallMcpToolResponse object from dictionary returned by HTTP client"""
        return cls(
            status_code=response_dict.get('status_code', 0),
            url=response_dict.get('url', ''),
            headers=response_dict.get('headers', {}),
            success=response_dict.get('success', False),
            json_data=response_dict.get('json'),
            text=response_dict.get('text'),
            error=response_dict.get('error'),
            request_id=response_dict.get('request_id') or
                      (response_dict.get('json', {}).get('requestId') if response_dict.get('json') else None)
        )

    def is_successful(self) -> bool:
        """Check if API call was successful"""
        return (
            self.success and
            self.status_code == 200 and
            self.api_success is True
        )

    def is_tool_successful(self) -> bool:
        """Check if tool execution was successful"""
        return self.tool_success

    def get_error_message(self) -> Optional[str]:
        """Get error message"""
        if self.error:
            return self.error
        if self.message:
            return self.message
        if not self.tool_success and self.result:
            return self.result
        return None

    def get_tool_result(self) -> Optional[Any]:
        """Get tool execution result"""
        return self.result

    def get_tool_output(self) -> Optional[str]:
        """Get tool output"""
        return self.output

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        result = {
            'status_code': self.status_code,
            'url': self.url,
            'headers': self.headers,
            'success': self.success,
            'request_id': self.request_id
        }

        if self.json_data:
            result['json'] = self.json_data
        if self.text:
            result['text'] = self.text
        if self.error:
            result['error'] = self.error

        return result

    def __str__(self) -> str:
        """String representation"""
        if self.is_tool_successful():
            return f"CallMcpToolResponse(tool_success=True, result={self.get_tool_result()})"
        else:
            return f"CallMcpToolResponse(tool_success=False, error={self.get_error_message()})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"CallMcpToolResponse(status_code={self.status_code}, success={self.success}, tool_success={self.is_tool_successful()}, result={self.get_tool_result()})"
