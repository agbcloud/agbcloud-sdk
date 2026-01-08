from typing import Optional


class ModifyContextRequest:
    """Request model for modifying a context."""

    def __init__(
        self,
        authorization: str = "",
        id: str = "",
        name: str = "",
    ):
        """
        Initialize ModifyContextRequest.

        Args:
            authorization (str): Authorization token.
            id (str): ID of the context to modify.
            name (str): New name for the context.
        """
        self.authorization = authorization
        self.id = id
        self.name = name

    def get_params(self) -> dict:
        """Get the query parameters as a dictionary."""
        params = {}
        if self.id:
            params["id"] = self.id
        if self.name:
            params["name"] = self.name
        return params

    def get_body(self) -> dict:
        """Get the request body as a dictionary."""
        return {}
