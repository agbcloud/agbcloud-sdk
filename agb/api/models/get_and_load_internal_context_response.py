"""
Get and load internal context response model
"""

from typing import Any, Dict, List, Optional


class GetAndLoadInternalContextResponseBodyData:
    """Data class for a single context item in the response list"""

    def __init__(
        self,
        context_id: str = "",
        context_type: str = "",
        context_path: str = "",
    ):
        """
        Initialize GetAndLoadInternalContextResponseBodyData

        Args:
            context_id (str): The context ID
            context_type (str): The context type
            context_path (str): The context path
        """
        self.context_id = context_id
        self.context_type = context_type
        self.context_path = context_path

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any]
    ) -> "GetAndLoadInternalContextResponseBodyData":
        """
        Create GetAndLoadInternalContextResponseBodyData from dictionary

        Args:
            data: Dictionary containing contextId, contextType, and contextPath

        Returns:
            GetAndLoadInternalContextResponseBodyData: Parsed data object
        """
        return cls(
            context_id=data.get("contextId", ""),
            context_type=data.get("contextType", ""),
            context_path=data.get("contextPath", ""),
        )


class GetAndLoadInternalContextResponse:
    """Structured response object for get and load internal context operation"""

    def __init__(
        self,
        status_code: int = 0,
        url: str = "",
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        """
        Initialize GetAndLoadInternalContextResponse

        Args:
            status_code (int): HTTP status code
            url (str): Request URL
            headers (Dict[str, str]): Response headers
            json_data (Dict[str, Any]): JSON response data
            request_id (str): Request ID
        """
        self.status_code = status_code
        self.url = url
        self.headers = headers or {}
        self.json_data = json_data or {}
        self.request_id = request_id

        if json_data:
            self.api_success = json_data.get("success", False)
            self.message = json_data.get("message", "")
            # data is a list of context items
            # Handle case where data is None (API returns null)
            data_value = json_data.get("data")
            self.data = data_value if isinstance(data_value, list) else []
        else:
            self.api_success = False
            self.message = ""
            self.data = []

    @classmethod
    def from_http_response(
        cls, response_dict: Dict[str, Any]
    ) -> "GetAndLoadInternalContextResponse":
        """
        Create GetAndLoadInternalContextResponse from HTTP client returned dictionary

        Args:
            response_dict: Dictionary returned by HTTP client

        Returns:
            GetAndLoadInternalContextResponse: Structured response object
        """
        return cls(
            status_code=response_dict.get("status_code", 0),
            url=response_dict.get("url", ""),
            headers=response_dict.get("headers", {}),
            json_data=response_dict.get("json"),
            request_id=response_dict.get("request_id")
            or (
                response_dict.get("json", {}).get("requestId")
                if response_dict.get("json")
                else None
            ),
        )

    def is_successful(self) -> bool:
        """Check if the operation was successful"""
        return self.status_code == 200 and self.api_success

    def get_error_message(self) -> str:
        """Get error message if operation failed"""
        if not self.is_successful():
            return self.message or f"HTTP {self.status_code} error"
        return ""

    def get_context_list(self) -> List[Dict[str, str]]:
        """
        Get list of context items from response as dictionaries.
        Each item contains contextId, contextType, and contextPath.

        Returns:
            List[Dict[str, str]]: List of context items as dictionaries
        """
        if not self.is_successful():
            return []

        if isinstance(self.data, list):
            return self.data
        return []

    def get_context_list_data(self) -> List[GetAndLoadInternalContextResponseBodyData]:
        """
        Get list of parsed context items from response.
        Each item is a GetAndLoadInternalContextResponseBodyData object.

        Returns:
            List[GetAndLoadInternalContextResponseBodyData]: List of parsed context items
        """
        if not self.is_successful():
            return []

        if isinstance(self.data, list):
            result = []
            for item in self.data:
                if isinstance(item, dict):
                    result.append(
                        GetAndLoadInternalContextResponseBodyData.from_dict(item)
                    )
            return result
        return []

    def to_map(self) -> Dict[str, Any]:
        """
        Convert response to dictionary format for compatibility.

        Returns:
            Dict[str, Any]: Response as dictionary
        """
        return {
            "body": {
                "Success": self.api_success,
                "Code": "" if self.api_success else (self.message or "Unknown error"),
                "Message": self.message,
                "Data": self.data,
            },
            "request_id": self.request_id,
        }
