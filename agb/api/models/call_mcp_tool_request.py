from typing import Any, Dict, List, Optional, Union


class CallMcpToolRequest:
    """Request object for calling MCP tools"""

    def __init__(
        self,
        args: Optional[Union[str, List[str], Dict[str, Any]]] = None,
        authorization: Optional[str] = None,
        image_id: Optional[str] = None,
        name: Optional[str] = None,
        server: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        self.args = args
        self.authorization = authorization
        self.image_id = image_id
        self.name = name
        self.server = server
        self.session_id = session_id

    def _filter_args_for_body(self, args_data: Any) -> str:
        """Filter out parameters that should not be included in request body"""
        import json
        
        if isinstance(args_data, dict):
            # Remove auto_gen_session as it should be a query parameter, not body parameter
            filtered_args = {k: v for k, v in args_data.items() if k != "auto_gen_session"}
            return json.dumps(filtered_args)
        elif isinstance(args_data, list):
            # For list, just convert directly
            return json.dumps(args_data)
        elif isinstance(args_data, str):
            # For string, parse and filter if it's valid JSON
            try:
                parsed_data = json.loads(args_data)
                if isinstance(parsed_data, dict):
                    filtered_args = {k: v for k, v in parsed_data.items() if k != "auto_gen_session"}
                    return json.dumps(filtered_args)
                else:
                    # If it's not a dict after parsing, use as-is
                    return args_data
            except (json.JSONDecodeError, TypeError):
                # If not valid JSON, use as-is
                return args_data
        else:
            # For other types, convert to string
            return str(args_data)

    def get_body(self) -> Dict[str, Any]:
        """Convert request object to dictionary format"""
        body = {}

        if self.args:
            # Use unified filtering method for all args types
            body["args"] = self._filter_args_for_body(self.args)

        if self.session_id:
            body["sessionId"] = self.session_id

        if self.name:
            body["name"] = self.name

        if self.server:
            body["server"] = self.server

        return body

    def get_params(self) -> Dict[str, Any]:
        """Get query parameters"""
        params = {}
        if self.image_id:
            params["imageId"] = self.image_id
        
        # Handle auto_gen_session from args, default to False if not present
        auto_gen_session = False  # Default value
        
        if self.args and isinstance(self.args, dict):
            # Direct dict access
            auto_gen_session = self.args.get("auto_gen_session", False)
        
        # Always set autoGenSession parameter
        params["autoGenSession"] = str(auto_gen_session).lower()
        
        return params
