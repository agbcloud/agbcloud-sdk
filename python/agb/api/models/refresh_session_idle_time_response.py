# -*- coding: utf-8 -*-
"""
Response models for refresh session idle time operations
"""

from typing import Any, Dict, Optional

class RefreshSessionIdleTimeResponse:
    """Response object for refreshing session idle time"""

    def __init__(
        self,
        status_code: int,
        url: str,
        headers: Dict[str, str],
        success: bool,
        json_data: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        error: Optional[str] = None,
        request_id: Optional[str] = None,
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
            self.api_success = json_data.get("success")
            self.code = json_data.get("code")
            self.message = json_data.get("message")
            self.http_status_code = json_data.get("httpStatusCode")
            self.data = json_data.get("data")
        else:
            self.api_success = None
            self.code = None
            self.message = None
            self.http_status_code = None
            self.data = None

    @classmethod
    def from_http_response(cls, response_dict: Dict[str, Any]) -> "RefreshSessionIdleTimeResponse":
        """Create from HTTP response dictionary"""
        return cls(
            status_code=response_dict.get("status_code", 0),
            url=response_dict.get("url", ""),
            headers=response_dict.get("headers", {}),
            success=response_dict.get("success", False),
            json_data=response_dict.get("json"),
            text=response_dict.get("text"),
            error=response_dict.get("error"),
            request_id=response_dict.get("request_id")
            or (
                response_dict.get("json", {}).get("requestId")
                if response_dict.get("json")
                else None
            ),
        )

    def is_successful(self) -> bool:
        """Check if the response indicates success"""
        return bool(self.success and self.status_code == 200 and self.api_success is True)

    def get_error_message(self) -> str:
        """Get error message from the response"""
        if not self.is_successful():
            return self.message or f"HTTP {self.status_code} error"
        return ""

    def get_data(self) -> Optional[Any]:
        """Get data from the response"""
        return self.data
