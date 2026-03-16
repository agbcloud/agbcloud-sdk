# -*- coding: utf-8 -*-
"""
Get CDP link response model for HTTP client
"""

from typing import Any, Dict, Optional


class GetCdpLinkResponse:
    """
    Response model for getting CDP (Chrome DevTools Protocol) link.

    Parses the API response to extract the WebSocket URL for
    connecting to the browser instance via CDP.
    """

    def __init__(
        self,
        status_code: Optional[int] = None,
        url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        self.status_code = status_code
        self.url = url
        self.headers = headers or {}
        self.json_data = json_data
        self.text = text
        self.success = success
        self.error = error
        self.request_id = request_id

        if json_data:
            self.api_success: Optional[bool] = json_data.get("success")
            self.code: Optional[str] = json_data.get("code")
            self.message: Optional[str] = json_data.get("message")
            self.http_status_code: Optional[int] = json_data.get("httpStatusCode")
            data = json_data.get("data")
            self.cdp_url: Optional[str] = (
                data.get("url") if isinstance(data, dict) else None
            )
        else:
            self.api_success = None
            self.code = None
            self.message = None
            self.http_status_code = None
            self.cdp_url = None

    @classmethod
    def from_http_response(cls, response_dict: Dict[str, Any]) -> "GetCdpLinkResponse":
        """
        Create GetCdpLinkResponse from HTTP response dictionary.

        Args:
            response_dict: HTTP response dictionary

        Returns:
            GetCdpLinkResponse: Response object
        """
        json_data = response_dict.get("json", {})
        return cls(
            status_code=response_dict.get("status_code", 0),
            url=response_dict.get("url", ""),
            headers=response_dict.get("headers", {}),
            success=response_dict.get("success", False),
            json_data=json_data,
            text=response_dict.get("text"),
            error=response_dict.get("error"),
            request_id=response_dict.get("request_id")
            or (
                response_dict.get("json", {}).get("requestId", "")
                if response_dict.get("json")
                else None
            ),
        )

    def is_successful(self) -> bool:
        """
        Check if the response indicates success.

        Returns:
            bool: True if successful, False otherwise
        """
        return self.success and self.status_code == 200 and self.api_success is True

    def get_error_message(self) -> Optional[str]:
        """
        Get error message if response failed.

        Returns:
            Optional[str]: Error message or None if successful
        """
        if self.message:
            return self.message
        if self.error:
            return self.error
        return "Unknown error"

    def get_url(self) -> Optional[str]:
        """
        Get the CDP WebSocket URL from response.

        Returns:
            Optional[str]: CDP URL or None if not found
        """
        return self.cdp_url
