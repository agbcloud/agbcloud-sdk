from typing import Optional, Dict, Any


class ReleaseSessionRequest:
    """Release session request object"""

    def __init__(
        self,
        session_id: str,
        authorization: Optional[str] = None
    ):
        self.session_id = session_id
        self.authorization = authorization

    def get_body(self) -> dict:
        """Convert request object to dictionary format"""
        body = {}

        if self.session_id:
            body["sessionId"] = self.session_id

        return body

    def get_params(self) -> dict:
        """Get query parameters"""
        params = {}
        return params
