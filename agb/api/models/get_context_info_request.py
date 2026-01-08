from typing import Optional


class GetContextInfoRequest:
    """Request model for getting context info."""

    def __init__(
        self,
        authorization: str = "",
        session_id: str = "",
        context_id: Optional[str] = None,
        path: Optional[str] = None,
        task_type: Optional[str] = None,
    ):
        """
        Initialize GetContextInfoRequest.

        Args:
            authorization (str): Authorization token.
            session_id (str): ID of the session.
            context_id (Optional[str]): ID of the context to get info for.
            path (Optional[str]): Path to get info for.
            task_type (Optional[str]): Type of task to get info for.
        """
        self.authorization = authorization
        self.session_id = session_id
        self.context_id = context_id
        self.path = path
        self.task_type = task_type

    def get_params(self) -> dict:
        """Get the query parameters as a dictionary."""
        params = {}
        if self.session_id:
            params["sessionId"] = self.session_id
        if self.context_id:
            params["contextId"] = self.context_id
        if self.path:
            params["path"] = self.path
        if self.task_type:
            params["taskType"] = self.task_type
        return params

    def get_body(self) -> dict:
        """Get the request body as a dictionary (empty for GET requests)."""
        return {}
