from typing import Optional


class DescribeContextFilesRequest:
    """Request model for describing context files."""

    def __init__(
        self,
        authorization: str = "",
        context_id: str = "",
        parent_folder_path: str = "",
        page_number: int = 1,
        page_size: int = 50,
    ):
        """
        Initialize DescribeContextFilesRequest.

        Args:
            authorization (str): Authorization token.
            context_id (str): ID of the context.
            parent_folder_path (str): Path of the parent folder.
            page_number (int): Page number for pagination.
            page_size (int): Number of items per page.
        """
        self.authorization = authorization
        self.context_id = context_id
        self.parent_folder_path = parent_folder_path
        self.page_number = page_number
        self.page_size = page_size

    def get_params(self) -> dict:
        """Get the query parameters as a dictionary."""
        params = {}
        if self.context_id:
            params["contextId"] = self.context_id
        if self.parent_folder_path:
            params["parentFolderPath"] = self.parent_folder_path
        # Always include page_number and page_size, even if they are 0
        params["pageNumber"] = str(self.page_number)
        params["pageSize"] = str(self.page_size)
        return params

    def get_body(self) -> dict:
        """Get the request body as a dictionary (empty for GET requests)."""
        return {}
