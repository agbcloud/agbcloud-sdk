from typing import Any, Dict, List, Optional

class SessionData:
    """Session data object"""

    def __init__(
        self,
        session_id: Optional[str] = None,
        app_instance_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_url: Optional[str] = None,
        vpc_resource: Optional[bool] = None,
        network_interface_ip: Optional[str] = None,
        http_port: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.session_id = session_id
        self.app_instance_id = app_instance_id
        self.resource_id = resource_id
        self.resource_url = resource_url
        self.vpc_resource = vpc_resource
        self.network_interface_ip = network_interface_ip
        self.http_port = http_port
        self.token = token

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionData":
        """Create SessionData object from dictionary"""
        return cls(
            session_id=data.get("sessionId"),
            app_instance_id=data.get("appInstanceId"),
            resource_id=data.get("resourceId"),
            resource_url=data.get("resourceUrl"),
            vpc_resource=data.get("vpcResource"),
            network_interface_ip=data.get("networkInterfaceIp"),
            http_port=data.get("httpPort"),
            token=data.get("token"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "sessionId": self.session_id,
            "appInstanceId": self.app_instance_id,
            "resourceId": self.resource_id,
            "resourceUrl": self.resource_url,
            "vpcResource": self.vpc_resource,
            "networkInterfaceIp": self.network_interface_ip,
            "httpPort": self.http_port,
            "token": self.token,
        }

class GetSessionResponse:
    """Get session response object"""

    def __init__(
        self,
        status_code: int,
        url: str,
        headers: Dict[str, str],
        success: bool,
        json_data: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        error: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        self.status_code = status_code
        self.url = url
        self.headers = headers
        self.success = success
        self.json_data = json_data
        self.text = text
        self.error = error
        self.request_id = request_id

        # Parse fields from JSON data
        if json_data:
            self.api_success = json_data.get("success")
            self.code = json_data.get("code")
            self.message = json_data.get("message")
            self.http_status_code = json_data.get("httpStatusCode")
            self.access_denied_detail = json_data.get("accessDeniedDetail")
            self.data = (
                SessionData.from_dict(json_data.get("data", {}))
                if json_data.get("data")
                else None
            )
        else:
            self.api_success = False
            self.code = None
            self.message = None
            self.http_status_code = None
            self.access_denied_detail = None
            self.data = None

    @classmethod
    def from_http_response(
        cls, response_dict: Dict[str, Any]
    ) -> "GetSessionResponse":
        """Create GetSessionResponse object from HTTP client returned dictionary"""
        return cls(
            status_code=response_dict.get("status_code", 0),
            url=response_dict.get("url", ""),
            headers=response_dict.get("headers", {}),
            success=response_dict.get("success", False),
            json_data=response_dict.get("json"),
            text=response_dict.get("text"),
            request_id=response_dict.get("request_id")
            or (
                response_dict.get("json", {}).get("requestId")
                if response_dict.get("json")
                else None
            ),
        )

    def is_successful(self) -> bool:
        """Check if API call was successful"""
        return self.success and self.api_success is True

    def get_session_id(self) -> Optional[str]:
        """Get session ID"""
        return self.data.session_id if self.data else None

    def get_resource_url(self) -> Optional[str]:
        """Get resource URL"""
        return self.data.resource_url if self.data else None

    def get_data(self) -> Optional[SessionData]:
        """Get data"""
        return self.data

    def get_error_message(self) -> str:
        """Get error message"""
        if self.error:
            return self.error
        if self.message:
            return self.message
        return "Unknown error"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        result = {
            "status_code": self.status_code,
            "url": self.url,
            #'headers': self.headers,
            "success": self.success,
            "request_id": self.request_id,
        }

        if self.json_data:
            result["json"] = self.json_data
        if self.text:
            result["text"] = self.text
        if self.error:
            result["error"] = self.error

        return result

    def __str__(self) -> str:
        """String representation"""
        if self.is_successful():
            return f"GetSessionResponse(success=True, session_id={self.get_session_id()})"
        else:
            return f"GetSessionResponse(success=False, error={self.get_error_message()})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"GetSessionResponse(status_code={self.status_code}, success={self.success}, session_id={self.get_session_id()})"