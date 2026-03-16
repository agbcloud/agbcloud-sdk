"""
Describe context files response model
"""

from typing import Any, Dict, List, Optional


class DescribeContextFilesResponseBodyData:
    def __init__(
        self,
        file_id: Optional[str] = None,
        file_name: str = "",
        file_path: Optional[str] = None,
        file_type: Optional[str] = None,
        gmt_create: Optional[str] = None,
        gmt_modified: str = "",
        size: Optional[int] = None,
        status: Optional[str] = None,
    ):
        self.file_id = file_id
        self.file_name = file_name
        self.file_path = file_path
        self.file_type = file_type
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.size = size
        self.status = status


class DescribeContextFilesResponse:
    """Structured response object for describe context files operation"""

    def __init__(
        self,
        status_code: int = 0,
        url: str = "",
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ):
        """
        Initialize DescribeContextFilesResponse

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
        self.next_token = next_token
        self.max_results = max_results

        if json_data:
            self.api_success = json_data.get("success", False)
            self.message = json_data.get("message", "")
            self.data = json_data.get("data", {})
        else:
            self.api_success = False
            self.message = ""
            self.data = {}

    @classmethod
    def from_http_response(
        cls, response_dict: Dict[str, Any]
    ) -> "DescribeContextFilesResponse":
        """
        Create DescribeContextFilesResponse from HTTP client returned dictionary

        Args:
            response_dict: Dictionary returned by HTTP client

        Returns:
            DescribeContextFilesResponse: Structured response object
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
            next_token=response_dict.get("nextToken"),
            max_results=response_dict.get("maxResults"),
        )

    def is_successful(self) -> bool:
        """Check if the operation was successful"""
        return self.status_code == 200 and self.api_success

    def get_error_message(self) -> str:
        """Get error message if operation failed"""
        if not self.is_successful():
            return self.message or f"HTTP {self.status_code} error"
        return ""

    def get_files_data(self) -> List[DescribeContextFilesResponseBodyData]:
        """Get files data from response"""
        if not self.is_successful():
            return []

        if isinstance(self.data, list):
            result = []
            for item in self.data:
                if isinstance(item, dict):
                    result.append(
                        DescribeContextFilesResponseBodyData(
                            file_id=item.get("fileId"),
                            file_name=item.get("fileName", ""),
                            file_path=item.get("filePath"),
                            file_type=item.get("fileType"),
                            gmt_create=item.get("gmtCreate"),
                            gmt_modified=item.get("gmtModified", ""),
                            size=item.get("size"),
                            status=item.get("status"),
                        )
                    )
            return result
        return []

    def get_next_token(self) -> Optional[str]:
        """Get next token from response"""
        return self.next_token

    def get_max_results(self) -> Optional[int]:
        """Get max results from response"""
        return self.max_results

    def get_count(self) -> Optional[int]:
        """Get count from response"""
        if not self.is_successful():
            return None
        if isinstance(self.data, dict):
            return self.data.get("count")
        # If data is a list, try to get count from json_data
        if isinstance(self.data, list) and self.json_data:
            return self.json_data.get("count")
        return None
