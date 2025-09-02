from typing import Optional, Union, List, Dict, Any


class CallMcpToolRequest:
    """Request object for calling MCP tools"""

    def __init__(
        self,
        args: Optional[Union[str, List[str], Dict[str, Any]]] = None,
        authorization: Optional[str] = None,
        image_id: Optional[str] = None,
        name: Optional[str] = None,
        server: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        self.args = args
        self.authorization = authorization
        self.image_id = image_id
        self.name = name
        self.server = server
        self.session_id = session_id

    def get_body(self) -> Dict[str, Any]:
        """Convert request object to dictionary format"""
        body = {}

        if self.args:
            # If args is a list or dict, convert to JSON string
            if isinstance(self.args, (list, dict)):
                import json
                body["args"] = json.dumps(self.args)
            else:
                body["args"] = str(self.args)

        if self.session_id:
            body["sessionId"] = self.session_id

        if self.name:
            body["name"] = self.name

        if self.server:
            body["server"] = self.server

        return body

    def get_params(self) -> Dict[str, Any]:
        """Get query parameters"""
        params = {}
        if self.image_id:
            params["imageId"] = self.image_id
        return params
