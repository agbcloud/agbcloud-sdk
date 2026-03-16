from typing import Optional


class ListSessionRequest:
    """Request model for listing sessions."""

    def __init__(
        self,
        authorization: str = "",
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
        labels: Optional[str] = None,
        is_all: Optional[bool] = None,
    ):
        """
        Initialize ListSessionRequest.

        Args:
            authorization (str): Authorization token.
            max_results (Optional[int]): Maximum number of results per page.
            next_token (Optional[str]): Token for the next page of results.
            labels (Optional[str]): Labels filter for sessions.
            is_all (Optional[bool]): Whether to include all sessions.
        """
        self.authorization = authorization
        self.max_results = max_results
        self.next_token = next_token
        self.labels = labels
        self.is_all = is_all

    def get_params(self) -> dict:
        """Get the query parameters as a dictionary."""
        params = {}
        if self.max_results is not None:
            params["maxResults"] = str(self.max_results)
        if self.next_token:
            params["nextToken"] = self.next_token
        if self.labels:
            params["labels"] = self.labels
        if self.is_all is not None:
            params["isAll"] = str(self.is_all).lower()
        return params

    def get_body(self) -> dict:
        """Get the request body as a dictionary (empty for GET requests)."""
        return {}
