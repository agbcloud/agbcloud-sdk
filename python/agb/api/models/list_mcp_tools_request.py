from typing import Any, Dict, List, Optional


class ListMcpToolsRequest:
    """List MCP tools request object"""

    def __init__(self, image_id: str = "", authorization: Optional[str] = None):
        self.image_id = image_id
        self.authorization = authorization

    def get_body(self) -> Dict[str, Any]:
        """Convert request object to dictionary format"""
        body: Dict[str, Any] = {}

        return body

    def get_params(self) -> Dict[str, Any]:
        """Get query parameters"""
        params: Dict[str, Any] = {}
        if self.image_id:
            params["imageId"] = self.image_id
        return params
