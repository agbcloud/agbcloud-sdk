from typing import Any, Dict, Optional


class GetLabelRequest:
    """Request object for getting labels"""

    def __init__(
        self,
        authorization: str = "",
        session_id: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ):
        """
        Initialize GetLabelRequest.

        Args:
            authorization (str): Authorization token.
            session_id (Optional[str]): ID of the session.
            max_results (Optional[int]): Maximum number of results to return.
            next_token (Optional[str]): Token for pagination.
        """
        self.authorization = authorization
        self.session_id = session_id
        self.max_results = max_results
        self.next_token = next_token

    def get_params(self) -> Dict[str, Any]:
        """Get query parameters"""
        params = {}
        if self.session_id:
            params["sessionId"] = self.session_id
        if self.max_results is not None:
            params["maxResults"] = self.max_results
        if self.next_token:
            params["nextToken"] = self.next_token
        return params

    def get_body(self) -> Dict[str, Any]:
        """Get the request body as a dictionary (empty for this request)"""
        return {}
