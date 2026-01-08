from typing import Optional


class DeleteContextFileRequest:
    """Request model for deleting context file."""

    def __init__(
        self,
        authorization: str = "",
        context_id: str = "",
        file_path: str = "",
    ):
        """
        Initialize DeleteContextFileRequest.

        Args:
            context_id (str): ID of the context.
            file_path (str): Path of the file to delete.
        """
        self.authorization = authorization
        self.context_id = context_id
        self.file_path = file_path

    def get_body(self) -> dict:
        """Get the request body as a dictionary."""
        return {}

    def get_params(self) -> dict:
        """Get the query parameters as a dictionary."""
        params = {}
        if self.context_id:
            params["contextId"] = self.context_id
        if self.file_path:
            params["filePath"] = self.file_path
        return params
