from typing import Optional, Dict, Any, List


class DesktopInfo:
    """Desktop information in the response"""

    def __init__(
        self,
        app_id: Optional[str] = None,
        auth_code: Optional[str] = None,
        connection_properties: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        ticket: Optional[str] = None
    ):
        self.app_id = app_id
        self.auth_code = auth_code
        self.connection_properties = connection_properties
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.ticket = ticket

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DesktopInfo':
        """Create DesktopInfo from dictionary"""
        return cls(
            app_id=data.get("appId"),
            auth_code=data.get("authCode"),
            connection_properties=data.get("connectionProperties"),
            resource_id=data.get("resourceId"),
            resource_type=data.get("resourceType"),
            ticket=data.get("ticket")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "appId": self.app_id,
            "authCode": self.auth_code,
            "connectionProperties": self.connection_properties,
            "resourceId": self.resource_id,
            "resourceType": self.resource_type,
            "ticket": self.ticket
        }


class McpResourceData:
    """MCP resource data in the response"""

    def __init__(
        self,
        desktop_info: Optional[DesktopInfo] = None,
        resource_url: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        self.desktop_info = desktop_info
        self.resource_url = resource_url
        self.session_id = session_id

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'McpResourceData':
        """Create McpResourceData from dictionary"""
        desktop_info = None
        if data.get("desktopInfo"):
            desktop_info = DesktopInfo.from_dict(data["desktopInfo"])

        return cls(
            desktop_info=desktop_info,
            resource_url=data.get("resourceUrl"),
            session_id=data.get("sessionId")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {}
        if self.desktop_info:
            result["desktopInfo"] = self.desktop_info.to_dict()
        if self.resource_url:
            result["resourceUrl"] = self.resource_url
        if self.session_id:
            result["sessionId"] = self.session_id
        return result


class GetMcpResourceResponse:
    """Get MCP resource response object"""

    def __init__(
        self,
        status_code: int,
        url: str,
        headers: Dict[str, str],
        success: bool,
        json_data: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        error: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        self.status_code = status_code
        self.url = url
        self.headers = headers
        self.success = success
        self.json_data = json_data
        self.text = text
        self.error = error
        self.request_id = request_id

    @classmethod
    def from_http_response(cls, response_dict: Dict[str, Any]) -> 'GetMcpResourceResponse':
        """Create GetMcpResourceResponse from HTTP response dictionary"""
        json_data = response_dict.get("json", {})

        # Extract request ID from response
        request_id = None
        if json_data and isinstance(json_data, dict):
            request_id = json_data.get("requestId")

        return cls(
            status_code=response_dict.get("status_code", 0),
            url=response_dict.get("url", ""),
            headers=response_dict.get("headers", {}),
            success=response_dict.get("success", False),
            json_data=json_data,
            text=response_dict.get("text"),
            error=response_dict.get("error"),
            request_id=request_id
        )

    def is_successful(self) -> bool:
        """Check if the HTTP request was successful"""
        return self.success and self.status_code == 200

    def get_error_message(self) -> Optional[str]:
        """Get error message from response"""
        if self.error:
            return self.error

        if self.json_data and isinstance(self.json_data, dict):
            # Check for API-level error messages
            if not self.json_data.get("success", True):
                return self.json_data.get("message") or "API request failed"

            # Check for data-level error messages
            data = self.json_data.get("data")
            if data and isinstance(data, dict) and data.get("isError"):
                return data.get("errMsg") or "Resource retrieval failed"

        return None

    def get_resource_data(self) -> Optional[McpResourceData]:
        """Get resource data from response"""
        if self.json_data and isinstance(self.json_data, dict):
            data = self.json_data.get("data")
            if data and isinstance(data, dict):
                return McpResourceData.from_dict(data)
        return None

    def get_resource_url(self) -> Optional[str]:
        """Get resource URL from response"""
        resource_data = self.get_resource_data()
        if resource_data:
            return resource_data.resource_url
        return None

    def get_desktop_info(self) -> Optional[DesktopInfo]:
        """Get desktop info from response"""
        resource_data = self.get_resource_data()
        if resource_data and resource_data.desktop_info:
            return resource_data.desktop_info
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert response object to dictionary"""
        return {
            "status_code": self.status_code,
            "url": self.url,
            "headers": self.headers,
            "success": self.success,
            "json_data": self.json_data,
            "text": self.text,
            "error": self.error,
            "request_id": self.request_id
        }

    def __str__(self) -> str:
        """String representation of the response"""
        resource_data = self.get_resource_data()
        return f"GetMcpResourceResponse(status_code={self.status_code}, success={self.success}, has_resource_data={resource_data is not None}, request_id={self.request_id})"

    def __repr__(self) -> str:
        """Detailed string representation of the response"""
        resource_data = self.get_resource_data()
        return f"GetMcpResourceResponse(status_code={self.status_code}, url='{self.url}', success={self.success}, has_resource_data={resource_data is not None}, request_id='{self.request_id}')"
