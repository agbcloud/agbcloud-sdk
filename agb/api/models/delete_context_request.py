from typing import Optional


class DeleteContextRequest:
    """Request model for deleting a context."""

    def __init__(
        self,
        authorization: str = "",
        id: str = "",
    ):
        """
        Initialize DeleteContextRequest.

        Args:
            authorization (str): Authorization token.
            id (str): ID of the context to delete.
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
