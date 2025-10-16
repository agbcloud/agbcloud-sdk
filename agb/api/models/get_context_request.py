from typing import Optional


class GetContextRequest:
    """Request model for getting a context."""

    def __init__(
        self,
        authorization: str = "",
        name: str = "",
        allow_create: bool = False,
        login_region_id: Optional[str] = None,
    ):
        """
        Initialize GetContextRequest.

        Args:
            authorization (str): Authorization token.
            name (str): Name of the context to get.
            allow_create (bool): Whether to create the context if it doesn't exist.
            login_region_id (Optional[str]): Login region ID for the request.
                If None or empty, defaults to Hangzhou region (cn-hangzhou).
        """
        self.authorization = authorization
        self.name = name
        self.allow_create = allow_create
        self.login_region_id = login_region_id

    def get_params(self) -> dict:
        """Get the query parameters as a dictionary."""
        params = {}
        if self.name:
            params["name"] = self.name
        if self.login_region_id:
            # Only include loginRegionId if specified; if None/empty, server defaults to cn-hangzhou
            params["loginRegionId"] = self.login_region_id
        params["allowCreate"] = str(self.allow_create).lower()
        return params

    def get_body(self) -> dict:
        """Get the request body as a dictionary (empty for GET requests)."""
        return {}

