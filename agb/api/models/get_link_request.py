# -*- coding: utf-8 -*-
"""
Get link request model for HTTP client
"""

from typing import Dict, Any, Optional


class GetLinkRequest:
    """
    Request model for getting session link
    """

    def __init__(
        self,
        authorization: str = None,
        port: int = None,
        protocol_type: str = None,
        session_id: str = None,
    ):
        self.authorization = authorization
        self.port = port
        self.protocol_type = protocol_type
        self.session_id = session_id

    def get_params(self) -> Dict[str, Any]:
        """
        Get query parameters for HTTP request

        Returns:
            Dict[str, Any]: Query parameters
        """
        params = {}
        if self.session_id:
            params['sessionId'] = self.session_id
        if self.protocol_type:
            params['protocolType'] = self.protocol_type
        if self.port:
            params['port'] = self.port
        return params

    def get_body(self) -> Dict[str, Any]:
        """
        Get request body for HTTP request

        Returns:
            Dict[str, Any]: Request body
        """
        # GET request typically doesn't have body, but keeping for consistency
        return {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            'authorization': self.authorization,
            'session_id': self.session_id,
            'protocol_type': self.protocol_type,
            'port': self.port
        }

    def validate(self) -> bool:
        """
        Validate request parameters

        Returns:
            bool: True if valid, False otherwise
        """
        if not self.authorization:
            return False
        if not self.session_id:
            return False
        return True

