from typing import Any, Dict, Optional


class GetSessionRequest:
    """Request object for getting session information"""

    def __init__(
        self,
        authorization: str = "",
        session_id: Optional[str] = None,
    ):
        """
        Initialize GetSessionRequest.

        Args:
            authorization (str): Authorization token.
            session_id (Optional[str]): ID of the session.
        """
        self.authorization = authorization
        self.session_id = session_id

    def get_params(self) -> Dict[str, Any]:
        """Get query parameters (empty for this request)"""
        return {}

    def get_body(self) -> Dict[str, Any]:
        """Get the request body as a dictionary"""
        body = {}
        if self.session_id:
            body["sessionId"] = self.session_id
        return body
