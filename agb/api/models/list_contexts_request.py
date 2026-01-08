from typing import Optional


class ListContextsRequest:
    """Request model for listing contexts."""

    def __init__(
        self,
        authorization: str = "",
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ):
        """
        Initialize ListContextsRequest.

        Args:
            authorization (str): Authorization token.
            max_results (Optional[int]): Maximum number of results per page.
            next_token (Optional[str]): Token for the next page of results.
        """
        self.authorization = authorization
        self.max_results = max_results
        self.next_token = next_token

    def get_params(self) -> dict:
        """Get the query parameters as a dictionary."""
        params = {}
        if self.max_results is not None:
            params["maxResults"] = str(self.max_results)
        if self.next_token:
            params["nextToken"] = self.next_token
        return params

    def get_body(self) -> dict:
        """Get the request body as a dictionary (empty for GET requests)."""
        return {}
