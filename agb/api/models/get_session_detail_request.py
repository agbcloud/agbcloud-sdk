from typing import Any, Dict, Optional


class GetSessionDetailRequest:
    """Request object for getting session status/details."""

    def __init__(
        self,
        authorization: str = "",
        session_id: Optional[str] = None,
    ):
        """
        Initialize GetSessionDetailRequest.

        Args:
            authorization (str): Authorization token (e.g., "Bearer <token>").
            session_id (Optional[str]): ID of the session.
        """
        self.authorization = authorization
        self.session_id = session_id

    def get_params(self) -> Dict[str, Any]:
        """Get query parameters (empty for this request)."""
        return {}

    def get_body(self) -> Dict[str, Any]:
        """Get the request body as a dictionary."""
        body: Dict[str, Any] = {}
        if self.session_id:
            # Keep both keys to handle potential backend case-sensitivity.
            body["sessionId"] = self.session_id
            body["SessionId"] = self.session_id
        return body
