# -*- coding: utf-8 -*-
"""
Get CDP link request model for HTTP client
"""

from typing import Any, Dict, Optional


class GetCdpLinkRequest:
    """
    Request model for getting CDP (Chrome DevTools Protocol) link.

    This request is used to retrieve the WebSocket URL for connecting
    to the browser instance via CDP.
    """

    def __init__(
        self,
        authorization: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        self.authorization = authorization
        self.session_id = session_id

    def get_params(self) -> Dict[str, Any]:
        """
        Get query parameters for HTTP request.

        Returns:
            Dict[str, Any]: Query parameters with sessionId
        """
        params: Dict[str, Any] = {}
        if self.session_id:
            params["sessionId"] = self.session_id
        return params

    def get_body(self) -> Dict[str, Any]:
        """
        Get request body for HTTP request.

        Returns:
            Dict[str, Any]: Empty body (sessionId is sent as query param)
        """
        return {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "authorization": self.authorization,
            "session_id": self.session_id,
        }

    def validate(self) -> bool:
        """
        Validate request parameters.

        Returns:
            bool: True if valid, False otherwise
        """
        if not self.authorization:
            return False
        if not self.session_id:
            return False
        return True
