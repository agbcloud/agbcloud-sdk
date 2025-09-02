from typing import Optional, Dict, Any, List


class ListMcpToolsResponse:
    """List MCP tools response object"""

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

        if json_data:
            self.api_success = json_data.get('success')
            self.code = json_data.get('code')
            self.message = json_data.get('message')
            self.http_status_code = json_data.get('httpStatusCode')
            self.data = json_data.get('data', {})
        else:
            self.api_success = None
            self.code = None
            self.message = None
            self.http_status_code = None
            self.data = None

    @classmethod
    def from_http_response(cls, response_dict: Dict[str, Any]) -> 'ListMcpToolsResponse':
        """Create ListMcpToolsResponse from HTTP response dictionary"""
        json_data = response_dict.get("json", {})

        # Extract request ID from response
        request_id = None
        if json_data and isinstance(json_data, dict):
            request_id = json_data.get("requestId")

        return cls(
            status_code=response_dict.get("status_code", 0),
            url=response_dict.get("url", ""),
            headers=response_dict.get("headers", {}),
            success=response_dict.get("success", False),
            json_data=json_data,
            text=response_dict.get("text"),
            error=response_dict.get("error"),
            request_id=request_id
        )

    def is_successful(self) -> bool:
        """Check if the HTTP request was successful"""
        return (
            self.success and
            self.status_code == 200 and
            self.api_success is True
        )

    def get_error_message(self) -> Optional[str]:
        """Get error message from response"""
        if self.error:
            return self.error

        if self.json_data and isinstance(self.json_data, dict):
            # Check for API-level error messages
            if not self.json_data.get("success", True):
                return self.json_data.get("message") or "API request failed"

            # Check for data-level error messages
            data = self.json_data.get("data")
            if data and isinstance(data, dict) and data.get("isError"):
                return data.get("errMsg") or "Tool execution failed"

        return None

    def get_tools_list(self) -> Optional[str]:
        """Get the tools list from response"""
        if self.json_data and isinstance(self.json_data, dict):
            data = self.json_data.get("data")
            if data and isinstance(data, str):
                return data
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert response object to dictionary"""
        return {
            "status_code": self.status_code,
            "url": self.url,
            "headers": self.headers,
            "success": self.success,
            "json_data": self.json_data,
            "text": self.text,
            "error": self.error,
            "request_id": self.request_id
        }

    def __str__(self) -> str:
        """String representation of the response"""
        return f"ListMcpToolsResponse(status_code={self.status_code}, success={self.success}, request_id={self.request_id})"

    def __repr__(self) -> str:
        """Detailed string representation of the response"""
        return f"ListMcpToolsResponse(status_code={self.status_code}, url='{self.url}', success={self.success}, request_id='{self.request_id}')"
