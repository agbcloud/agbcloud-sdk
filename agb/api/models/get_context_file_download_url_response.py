"""
Get context file download URL response model
"""

from typing import Any, Dict, Optional


class GetContextFileDownloadUrlResponseBodyData:
    def __init__(
        self,
        expire_time: Optional[int] = None,
        url: Optional[str] = None,
    ):
        self.expire_time = expire_time
        self.url = url


class GetContextFileDownloadUrlResponse:
    """Structured response object for get context file download URL operation"""

    def __init__(
        self,
        status_code: int = 0,
        url: str = "",
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        """
        Initialize GetContextFileDownloadUrlResponse

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
            self.http_status_code = json_data.get("httpStatusCode", "")
        else:
            self.api_success = False
            self.message = ""
            self.data = {}
            self.http_status_code = None

    @classmethod
    def from_http_response(
        cls, response_dict: Dict[str, Any]
    ) -> "GetContextFileDownloadUrlResponse":
        """
        Create GetContextFileDownloadUrlResponse from HTTP client returned dictionary

        Args:
            response_dict: Dictionary returned by HTTP client

        Returns:
            GetContextFileDownloadUrlResponse: Structured response object
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

    def get_download_url(self) -> str:
        """Get download URL from response"""
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

    def get_download_url_data(self) -> GetContextFileDownloadUrlResponseBodyData:
        """Get download URL data from response"""
        if not self.is_successful():
            return GetContextFileDownloadUrlResponseBodyData()

        if isinstance(self.data, dict):
            return GetContextFileDownloadUrlResponseBodyData(
                expire_time=self.data.get("expireTime"), url=self.data.get("url")
            )
        return GetContextFileDownloadUrlResponseBodyData()
