from typing import Optional, Dict, Any, List


class ListMcpToolsRequest:
    """List MCP tools request object"""

    def __init__(
        self,
        image_id: str = "",
        authorization: Optional[str] = None
    ):
        self.image_id = image_id
        self.authorization = authorization

    def get_body(self) -> dict:
        """Convert request object to dictionary format"""
        body = {}

        return body

    def get_params(self) -> dict:
        """Get query parameters"""
        params = {}
        if self.image_id:
            params["imageId"] = self.image_id
        return params

