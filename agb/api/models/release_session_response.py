from typing import Optional, Dict, Any


class ReleaseSessionResponse:
    """Release session response object"""

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

        # Parse fields from JSON data
        if json_data:
            self.api_success = json_data.get('success')
            self.code = json_data.get('code')
            self.message = json_data.get('message')
            self.http_status_code = json_data.get('httpStatusCode')
            self.access_denied_detail = json_data.get('accessDeniedDetail')
            self.data = json_data.get('data')
        else:
            self.api_success = None
            self.code = None
            self.message = None
            self.http_status_code = None
            self.access_denied_detail = None
            self.data = None

    @classmethod
    def from_http_response(cls, response_dict: Dict[str, Any]) -> 'ReleaseSessionResponse':
        """Create ReleaseSessionResponse object from HTTP client returned dictionary"""
        return cls(
            status_code=response_dict.get('status_code', 0),
            url=response_dict.get('url', ''),
            headers=response_dict.get('headers', {}),
            success=response_dict.get('success', False),
            json_data=response_dict.get('json'),
            text=response_dict.get('text'),
            error=response_dict.get('error'),
            request_id=response_dict.get('request_id') or
                      (response_dict.get('json', {}).get('requestId') if response_dict.get('json') else None)
        )

    def is_successful(self) -> bool:
        """Check if API call was successful"""
        return (
            self.success and
            self.status_code == 200 and
            self.api_success is True
        )

    def get_error_message(self) -> Optional[str]:
        """Get error message"""
        if self.error:
            return self.error
        if self.message:
            return self.message
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        result = {
            'status_code': self.status_code,
            'url': self.url,
            'headers': self.headers,
            'success': self.success,
            'request_id': self.request_id
        }

        if self.json_data:
            result['json'] = self.json_data
        if self.text:
            result['text'] = self.text
        if self.error:
            result['error'] = self.error

        return result

    def __str__(self) -> str:
        """String representation"""
        if self.is_successful():
            return f"ReleaseSessionResponse(success=True)"
        else:
            return f"ReleaseSessionResponse(success=False, error={self.get_error_message()})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"ReleaseSessionResponse(status_code={self.status_code}, success={self.success})"
