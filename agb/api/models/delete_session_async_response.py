# -*- coding: utf-8 -*-
"""
Response models for delete session async operations
"""

from typing import Any, Dict, Optional


class DeleteSessionAsyncResponseBody:
    """Response body for delete session async operation"""

    def __init__(
        self,
        code: Optional[str] = None,
        http_status_code: Optional[int] = None,
        message: Optional[str] = None,
        request_id: Optional[str] = None,
        success: Optional[bool] = None,
    ):
        self.code = code
        self.http_status_code = http_status_code
        self.message = message
        self.request_id = request_id
        self.success = success

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteSessionAsyncResponseBody":
        """Create from dictionary"""
        return cls(
            code=data.get("Code") or data.get("code"),
            http_status_code=data.get("HttpStatusCode") or data.get("httpStatusCode"),
            message=data.get("Message") or data.get("message"),
            request_id=data.get("RequestId")
            or data.get("requestId")
            or data.get("request_id"),
            success=(
                data.get("Success")
                if data.get("Success") is not None
                else data.get("success")
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        result = {}
        if self.code is not None:
            result["Code"] = self.code
        if self.http_status_code is not None:
            result["HttpStatusCode"] = self.http_status_code
        if self.message is not None:
            result["Message"] = self.message
        if self.request_id is not None:
            result["RequestId"] = self.request_id
        if self.success is not None:
            result["Success"] = self.success
        return result


class DeleteSessionAsyncResponse:
    """Response object for deleting a session asynchronously"""

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

        # Parse body from JSON data
        if json_data:
            # The response body is directly in json_data, or nested in "body" field
            body_data = json_data.get("body", json_data)
            self.body = DeleteSessionAsyncResponseBody.from_dict(body_data)
        else:
            self.body = DeleteSessionAsyncResponseBody()

    @classmethod
    def from_http_response(
        cls, response_dict: Dict[str, Any]
    ) -> "DeleteSessionAsyncResponse":
        """Create response object from HTTP response dictionary"""
        json_data = response_dict.get("json")

        # Extract request_id from various possible locations
        request_id = response_dict.get("request_id")
        return cls(
            status_code=response_dict.get("status_code", 0),
            url=response_dict.get("url", ""),
            headers=response_dict.get("headers", {}),
            success=response_dict.get("success", False),
            json_data=json_data,
            text=response_dict.get("text"),
            error=response_dict.get("error"),
            request_id=request_id,
        )

    def is_successful(self) -> bool:
        """Check if the response indicates success"""
        return self.success and self.status_code == 200 and self.body.success is True

    def get_error_message(self) -> Optional[str]:
        """Get error message from the response"""
        if not self.is_successful():
            return self.body.message or self.error or f"HTTP {self.status_code} error"
        return None

    def to_map(self) -> Dict[str, Any]:
        """Convert to dictionary format (for compatibility)"""
        result = {
            "status_code": self.status_code,
            "url": self.url,
            "headers": self.headers,
            "success": self.success,
            "request_id": self.request_id or self.body.request_id,
        }

        if self.json_data:
            result["json"] = self.json_data
        if self.text:
            result["text"] = self.text
        if self.error:
            result["error"] = self.error

        return result
