"""
List session response model
"""

from typing import Any, Dict, List, Optional


class ListSessionResponseBodyData:
    def __init__(
        self,
        session_id: Optional[str] = None,
        session_status: Optional[str] = None,
    ):
        self.session_id = session_id
        self.session_status = session_status


class ListSessionResponse:
    """Structured response object for list session operation"""

    def __init__(
        self,
        status_code: int = 0,
        url: str = "",
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        """
        Initialize ListSessionResponse

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
            self.http_status_code = json_data.get("httpStatusCode", "")
        else:
            self.api_success = False
            self.message = ""
            self.data = {}
            self.http_status_code = None

    @classmethod
    def from_http_response(cls, response_dict: Dict[str, Any]) -> "ListSessionResponse":
        """
        Create ListSessionResponse from HTTP client returned dictionary

        Args:
            response_dict: Dictionary returned by HTTP client

        Returns:
            ListSessionResponse: Structured response object
        """
        return cls(
            status_code=response_dict.get("status_code", 0),
            url=response_dict.get("url", ""),
            headers=response_dict.get("headers", {}),
            json_data=response_dict.get("json"),
            request_id=response_dict.get("request_id")
            or (
                response_dict.get("json", {}).get("requestId", "")
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

    def get_session_data(self) -> List[ListSessionResponseBodyData]:
        """Get session data from response"""
        if not self.is_successful():
            return []

        if isinstance(self.data, list):
            result = []
            for item in self.data:
                if isinstance(item, dict):
                    result.append(
                        ListSessionResponseBodyData(
                            session_id=item.get("sessionId"),
                            session_status=item.get("sessionStatus"),
                        )
                    )
            return result
        return []

    def get_next_token(self) -> Optional[str]:
        """Get next token for pagination"""
        if not self.is_successful():
            return None
        return self.json_data.get("nextToken")

    def get_max_results(self) -> Optional[int]:
        """Get max results from response"""
        if not self.is_successful():
            return None
        return self.json_data.get("maxResults")

    def get_count(self) -> Optional[int]:
        """Get count from response"""
        if not self.is_successful():
            return None
        return self.json_data.get("count")
