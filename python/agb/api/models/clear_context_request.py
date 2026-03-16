from typing import Optional


class ClearContextRequest:
    """Request model for clearing a context."""

    def __init__(
        self,
        authorization: str = "",
        id: str = "",
    ):
        """
        Initialize ClearContextRequest.

        Args:
            authorization (str): Authorization token.
            id (str): ID of the context to clear.
        """
        self.authorization = authorization
        self.id = id

    def get_params(self) -> dict:
        """Get the query parameters as a dictionary."""
        params = {}
        if self.id:
            params["id"] = self.id
        return params

    def get_body(self) -> dict:
        """Get the request body as a dictionary."""
        return {}
