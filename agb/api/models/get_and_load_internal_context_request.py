import json
from typing import List, Optional


class GetAndLoadInternalContextRequest:
    """Request model for getting and loading internal context."""

    def __init__(
        self,
        authorization: str = "",
        session_id: str = "",
        context_types: Optional[List[str]] = None,
    ):
        """
        Initialize GetAndLoadInternalContextRequest.

        Args:
            authorization (str): Authorization token.
            session_id (str): ID of the session.
            context_types (List[str]): List of context types to get and load.
        """
        self.authorization = authorization
        self.session_id = session_id
        self.context_types = context_types or []

    def get_params(self) -> dict:
        """Get the query parameters as a dictionary."""
        params = {}
        if self.session_id:
            params["sessionId"] = self.session_id
        if self.context_types:
            # Serialize list as JSON array string for query parameter
            # Some APIs expect JSON array format in query parameters
            params["contextTypes"] = json.dumps(self.context_types)
        return params

    def get_body(self) -> dict:
        """Get the request body as a dictionary."""
        body = {}
        return body
