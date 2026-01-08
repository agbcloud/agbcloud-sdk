import json
from typing import Any, Dict, List, Optional


class CreateMcpSessionRequestPersistenceDataList:
    def __init__(
        self,
        context_id: Optional[str] = None,
        path: Optional[str] = None,
        policy: Optional[str] = None,
    ):
        self.context_id = context_id
        self.path = path
        self.policy = policy

    def validate(self):
        pass

    def to_map(self):
        result = dict()

        # Always include fields, even if they are empty strings
        # Use lowercase field names as expected by the server
        result["contextId"] = self.context_id if self.context_id is not None else ""
        result["path"] = self.path if self.path is not None else ""
        result["policy"] = self.policy if self.policy is not None else ""

        return result

    def from_map(self, m: Optional[dict] = None):
        m = m or dict()
        if m.get("contextId") is not None:
            self.context_id = m.get("contextId")

        if m.get("path") is not None:
            self.path = m.get("path")

        if m.get("policy") is not None:
            self.policy = m.get("policy")

        return self


class CreateSessionRequest:
    """Request object for creating a session"""

    def __init__(
        self,
        authorization: str = "",
        context_id: Optional[str] = None,
        image_id: str = "",
        labels: Optional[str] = None,
        persistence_data_list: Optional[
            List[CreateMcpSessionRequestPersistenceDataList]
        ] = None,
        session_id: str = "",
        sdk_stats: Optional[Dict[str, Any]] = None,
    ):
        self.authorization = authorization
        self.context_id = context_id
        self.image_id = image_id
        self.labels = labels
        self.persistence_data_list = persistence_data_list
        self.session_id = session_id
        self.sdk_stats = sdk_stats

    def get_body(self) -> Dict[str, Any]:
        """Convert request object to dictionary format"""
        body = {}

        if self.session_id:
            body["sessionId"] = self.session_id

        if self.persistence_data_list:
            body["persistenceDataList"] = []
            for data in self.persistence_data_list:
                body["persistenceDataList"].append(data.to_map() if data else None)

        if self.context_id:
            body["contextId"] = self.context_id

        if self.labels:
            body["labels"] = self.labels

        return body

    def get_params(self) -> Dict[str, Any]:
        """Get query parameters"""
        params = {}
        if self.image_id:
            params["imageId"] = self.image_id

        if self.sdk_stats:
            # Serialize sdk_stats dict to JSON string for query parameter
            # Use separators=(',', ':') to remove spaces, matching reference implementation
            # This avoids space encoding issues with urlencode (spaces -> +)
            json_str = json.dumps(
                self.sdk_stats, ensure_ascii=False, separators=(",", ":")
            )
            params["sdkStats"] = json_str
        return params
