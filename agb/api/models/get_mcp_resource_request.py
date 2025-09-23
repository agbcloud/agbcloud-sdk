from typing import Any, Dict, List, Optional


class GetMcpResourceRequest:
    """Get MCP resource request object"""

    def __init__(self, session_id: str = "", authorization: Optional[str] = None):
        self.session_id = session_id
        self.authorization = authorization

    def get_body(self) -> Dict[str, Any]:
        """Convert request object to dictionary format"""
        body: Dict[str, Any] = {}

        if self.session_id:
            body["sessionId"] = self.session_id

        return body

    def get_params(self) -> Dict[str, Any]:
        """Get query parameters"""
        params: Dict[str, Any] = {}
        return params
