# -*- coding: utf-8 -*-
"""
InitBrowserRequest model for browser initialization
"""

import json
from typing import Dict, Any, Optional


class InitBrowserRequest:
    """
    Request model for initializing browser
    """

    def __init__(
        self,
        authorization: str,
        session_id: str,
        persistent_path: str,
        browser_option: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize InitBrowserRequest

        Args:
            authorization: Authorization header value
            session_id: Session ID
            persistent_path: Path for persistent browser data
            browser_option: Browser configuration options
        """
        self.authorization = authorization
        self.session_id = session_id
        self.persistent_path = persistent_path
        self.browser_option = browser_option or {}

    def get_body(self) -> Dict[str, Any]:
        """
        Get request body data

        Returns:
            Dict containing request body
        """
        return {}

    def get_params(self) -> Dict[str, Any]:

        """
        Get query parameters for the request

        Returns:
            Dict containing query parameters
        """
        # Convert browser_option to JSON string if it's a dict
        browser_option_param = self.browser_option
        if isinstance(self.browser_option, dict):
            browser_option_param = json.dumps(self.browser_option)

        return {
            "sessionId": self.session_id,
            "persistentPath": self.persistent_path,
            "browserOption": browser_option_param
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert request to dictionary

        Returns:
            Dict representation of the request
        """
        return {
            "authorization": self.authorization,
            "session_id": self.session_id,
            "persistent_path": self.persistent_path,
            "browser_option": self.browser_option
        }
