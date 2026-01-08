from typing import Any, Dict, Optional


class SetLabelRequest:
    """Request object for setting labels"""

    def __init__(
        self,
        authorization: str = "",
        session_id: Optional[str] = None,
        labels: Optional[str] = None,
    ):
        """
        Initialize SetLabelRequest.

        Args:
            authorization (str): Authorization token.
            session_id (Optional[str]): ID of the session.
            labels (Optional[str]): Labels to set.
        """
        self.authorization = authorization
        self.session_id = session_id
        self.labels = labels

    def get_params(self) -> Dict[str, Any]:
        """Get query parameters"""
        params = {}
        if self.session_id:
            params["sessionId"] = self.session_id
        if self.labels:
            params["Labels"] = self.labels
        return params

    def get_body(self) -> Dict[str, Any]:
        """Get the request body as a dictionary (empty for this request)"""
        return {}
