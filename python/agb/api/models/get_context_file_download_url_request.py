from typing import Optional


class GetContextFileDownloadUrlRequest:
    """Request model for getting context file download URL."""

    def __init__(
        self,
        authorization: str = "",
        context_id: str = "",
        file_path: str = "",
    ):
        """
        Initialize GetContextFileDownloadUrlRequest.

        Args:
            authorization (str): Authorization token.
            context_id (str): ID of the context.
            file_path (str): Path of the file to download.
        """
        self.authorization = authorization
        self.context_id = context_id
        self.file_path = file_path

    def get_params(self) -> dict:
        """Get the query parameters as a dictionary."""
        params = {}
        if self.context_id:
            params["contextId"] = self.context_id
        if self.file_path:
            params["filePath"] = self.file_path
        return params

    def get_body(self) -> dict:
        """Get the request body as a dictionary (empty for GET requests)."""
        return {}
