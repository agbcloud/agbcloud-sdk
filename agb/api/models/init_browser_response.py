# -*- coding: utf-8 -*-
"""
InitBrowserResponse model for browser initialization response
"""

from typing import Dict, Any, Optional


class InitBrowserResponse:
    """
    Response model for browser initialization
    """

    def __init__(
        self,
        status_code: int,
        url: str,
        headers: Dict[str, str],
        json_data: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None
    ):
        """
        Initialize InitBrowserResponse

        Args:
            status_code: HTTP status code
            url: Request URL
            headers: Response headers
            json_data: JSON response data
            text: Response text
            success: Whether the request was successful
            error: Error message if any
        """
        self.status_code = status_code
        self.url = url
        self.headers = headers
        self.json_data = json_data or {}
        self.text = text
        self.success = success
        self.error = error

        if json_data:
            self.api_success = json_data.get('success')
            self.code = json_data.get('code')
            self.message = json_data.get('message')
            self.http_status_code = json_data.get('httpStatusCode')
            self.data = json_data.get('data', {})
            self.port = self.data.get('port')

        else:
            self.api_success = None
            self.code = None
            self.message = None
            self.http_status_code = None
            self.data = None
            self.port = None

    @classmethod
    def from_http_response(cls, response_dict: Dict[str, Any]) -> 'InitBrowserResponse':
        """
        Create InitBrowserResponse from HTTP response dictionary

        Args:
            response_dict: HTTP response dictionary

        Returns:
            InitBrowserResponse instance
        """
        return cls(
            status_code=response_dict.get("status_code", 0),
            url=response_dict.get("url", ""),
            headers=response_dict.get("headers", {}),
            json_data=response_dict.get("json"),
            text=response_dict.get("text"),
            success=response_dict.get("success", False),
            error=response_dict.get("error")
        )

    def is_successful(self) -> bool:
        """
        Check if the response indicates success

        Returns:
            True if successful, False otherwise
        """
        return (
            self.success and
            self.status_code == 200 and
            self.api_success is True
        )

    def get_error_message(self) -> Optional[str]:
        """
        Get error message if any

        Returns:
            Error message or None
        """
        return self.error

    def get_port(self) -> Optional[int]:
        """
        Get browser port from response data

        Returns:
            Port number or None
        """
        try:
            if self.json_data and "data" in self.json_data:
                data = self.json_data["data"]
                if isinstance(data, dict) and "port" in data:
                    return data["port"]
        except (KeyError, TypeError):
            pass
        return None

    def to_map(self) -> Dict[str, Any]:
        """
        Convert response to map format for backward compatibility

        Returns:
            Dict representation of the response
        """
        return {
            "status_code": self.status_code,
            "url": self.url,
            "headers": self.headers,
            "body": self.json_data or {},
            "success": self.success,
            "error": self.error
        }
