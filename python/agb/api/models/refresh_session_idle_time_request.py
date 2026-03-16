# -*- coding: utf-8 -*-
"""
Request models for refresh session idle time operations
"""

from typing import Any, Dict

class RefreshSessionIdleTimeRequest:
    """Request object for refreshing session idle time"""

    def __init__(
        self,
        authorization: str = "",
        session_id: str = "",
    ):
        self.authorization = authorization
        self.session_id = session_id

    def get_params(self) -> Dict[str, Any]:
        """Get query parameters"""
        params: Dict[str, Any] = {}
        if self.session_id:
            params["sessionId"] = self.session_id
        return params

    def get_body(self) -> Dict[str, Any]:
        """Convert request to body dict"""
        body: Dict[str, Any] = {}
        return body
