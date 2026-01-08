from typing import Optional


class SyncContextRequest:
    """Request model for syncing context."""

    def __init__(
        self,
        authorization: str = "",
        session_id: str = "",
        context_id: Optional[str] = None,
        path: Optional[str] = None,
        mode: Optional[str] = None,
    ):
        """
        Initialize SyncContextRequest.

        Args:
            authorization (str): Authorization token.
            session_id (str): ID of the session.
            context_id (Optional[str]): ID of the context to sync.
            path (Optional[str]): Path to sync.
            mode (Optional[str]): Sync mode.
        """
        self.authorization = authorization
        self.session_id = session_id
        self.context_id = context_id
        self.path = path
        self.mode = mode

    def get_params(self) -> dict:
        """Get the query parameters as a dictionary."""
        params = {}
        if self.session_id:
            params["sessionId"] = self.session_id
        if self.context_id:
            params["contextId"] = self.context_id
        if self.path:
            params["path"] = self.path
        if self.mode:
            params["mode"] = self.mode
        return params

    def get_body(self) -> dict:
        """Get the request body as a dictionary."""
        return {}
