# -*- coding: utf-8 -*-
"""
Request models for delete session async operations
"""

from typing import Any, Dict, Optional


class DeleteSessionAsyncRequest:
    """Request object for deleting a session asynchronously"""

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
        return params

    def get_body(self) -> Dict[str, Any]:
        """Convert request object to dictionary format"""
        body = {}
        if self.session_id:
            body["sessionId"] = self.session_id
        return body
