"""
Get context file upload URL response model
"""

from typing import Any, Dict, Optional


class GetContextFileUploadUrlResponseBodyData:
    def __init__(
        self,
        expire_time: Optional[int] = None,
        url: Optional[str] = None,
    ):
        self.expire_time = expire_time
        self.url = url


class GetContextFileUploadUrlResponse:
    """Structured response object for get context file upload URL operation"""

    def __init__(
        self,
        status_code: int = 0,
        url: str = "",
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        """
        Initialize GetContextFileUploadUrlResponse

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

        if json_data:
            self.api_success = json_data.get("success", False)
            self.message = json_data.get("message", "")
            self.data = json_data.get("data", {})
        else:
            self.api_success = False
            self.message = ""
            self.data = {}

    @classmethod
    def from_http_response(
        cls, response_dict: Dict[str, Any]
    ) -> "GetContextFileUploadUrlResponse":
        """
        Create GetContextFileUploadUrlResponse from HTTP client returned dictionary

        Args:
            response_dict: Dictionary returned by HTTP client

        Returns:
            GetContextFileUploadUrlResponse: Structured response object
        """
        return cls(
            status_code=response_dict.get("status_code", 0),
            url=response_dict.get("url", ""),
            headers=response_dict.get("headers", {}),
            json_data=response_dict.get("json"),
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

    def get_upload_url(self) -> str:
        """Get upload URL from response"""
        if not self.is_successful():
            return ""

        if isinstance(self.data, dict):
            return self.data.get("url", "")
        return ""

    def get_expire_time(self) -> Optional[int]:
        """Get expire time from response"""
        if not self.is_successful():
            return None

        if isinstance(self.data, dict):
            return self.data.get("expireTime", None)
        return None

    def get_upload_url_data(self) -> GetContextFileUploadUrlResponseBodyData:
        """Get upload URL data from response"""
        if not self.is_successful():
            return GetContextFileUploadUrlResponseBodyData()

        if isinstance(self.data, dict):
            return GetContextFileUploadUrlResponseBodyData(
                expire_time=self.data.get("expireTime"), url=self.data.get("url")
            )
        return GetContextFileUploadUrlResponseBodyData()
