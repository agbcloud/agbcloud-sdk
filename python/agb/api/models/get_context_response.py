"""
Get context response model
"""

from typing import Any, Dict, Optional


class GetContextResponseBodyData:
    def __init__(
        self,
        create_time: Optional[str] = None,
        id: Optional[str] = None,
        last_used_time: Optional[str] = None,
        name: Optional[str] = None,
        state: Optional[str] = None,
    ):
        self.create_time = create_time
        self.id = id
        self.last_used_time = last_used_time
        self.name = name
        self.state = state


class GetContextResponse:
    """Structured response object for get context operation"""

    def __init__(
        self,
        status_code: int = 0,
        url: str = "",
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        """
        Initialize GetContextResponse

        Args:
            status_code (int): HTTP status code
            url (str): Request URL
            headers (Dict[str, str]): Response headers
            json_data (Dict[str, Any]): JSON response data
            request_id (str): Request ID
        """
        self.status_code = status_code
        self.url = url
        self.headers = headers or {}
        self.json_data = json_data or {}
        self.request_id = request_id

        # Parse json_data once in constructor
        if json_data:
            self.api_success = json_data.get("success", False)
            self.message = json_data.get("message", "")
            self.data = json_data.get("data", {})
        else:
            self.api_success = False
            self.message = ""
            self.data = {}

    @classmethod
    def from_http_response(cls, response_dict: Dict[str, Any]) -> "GetContextResponse":
        """
        Create GetContextResponse from HTTP client returned dictionary

        Args:
            response_dict: Dictionary returned by HTTP client

        Returns:
            GetContextResponse: Structured response object
        """
        return cls(
            status_code=response_dict.get("status_code", 0),
            url=response_dict.get("url", ""),
            headers=response_dict.get("headers", {}),
            json_data=response_dict.get("json", {}),
            request_id=response_dict.get("request_id")
            or (
                response_dict.get("json", {}).get("requestId")
                if response_dict.get("json")
                else None
            ),
        )

    def is_successful(self) -> bool:
        """Check if the operation was successful"""
        return self.status_code == 200 and self.api_success

    def get_error_message(self) -> str:
        """Get error message if operation failed"""
        if not self.is_successful():
            return self.message or f"HTTP {self.status_code} error"
        return ""

    def get_context_data(self) -> GetContextResponseBodyData:
        """Get context data from response"""
        if not self.is_successful():
            return GetContextResponseBodyData()

        if isinstance(self.data, dict):
            return GetContextResponseBodyData(
                create_time=self.data.get("createTime"),
                id=self.data.get("id"),
                last_used_time=self.data.get("lastUsedTime"),
                name=self.data.get("name"),
                state=self.data.get("state"),
            )
        return GetContextResponseBodyData()
