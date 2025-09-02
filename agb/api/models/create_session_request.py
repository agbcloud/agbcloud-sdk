from typing import Optional, Union, List, Dict, Any


class CreateSessionRequest:
    """Request object for creating a session"""

    def __init__(
        self,
        authorization: str = "",
        image_id: str = "",
        session_id: str = "",
    ):
        self.authorization = authorization
        self.image_id = image_id
        self.session_id = session_id

    def get_body(self) -> Dict[str, Any]:
        """Convert request object to dictionary format"""
        body = {}

        if self.session_id:
            body["sessionId"] = self.session_id

        return body


    def get_params(self) -> Dict[str, Any]:
        """Get query parameters"""
        params = {}
        if self.image_id:
            params["imageId"] = self.image_id
        return params
