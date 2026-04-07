# -*- coding: utf-8 -*-
"""
WebSocket models and enums for AGB SDK.
"""

from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass


class WsConnectionState(str, Enum):
    """WebSocket connection state."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    RECONNECTING = "RECONNECTING"
    ERROR = "ERROR"


class WebSocketMessageType(Enum):
    """WebSocket message types."""
    # Control messages
    PING = "ping"
    PONG = "pong"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    
    # Data messages
    DATA = "data"
    EVENT = "event"
    COMMAND = "command"
    RESPONSE = "response"
    
    # Error messages
    ERROR = "error"


class WebSocketMessage:
    """
    WebSocket message wrapper.
    
    Provides a structured way to handle WebSocket messages with type safety.
    """
    
    def __init__(
        self,
        message_type: str,
        data: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[int] = None,
    ):
        """
        Initialize WebSocket message.
        
        Args:
            message_type: Message type
            data: Message data
            message_id: Unique message identifier
            timestamp: Message timestamp (Unix timestamp in milliseconds)
        """
        self.message_type = message_type
        self.data = data or {}
        self.message_id = message_id
        self.timestamp = timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert message to dictionary.
        
        Returns:
            Dict[str, Any]: Message as dictionary
        """
        result: Dict[str, Any] = {
            "type": self.message_type,
            "data": self.data,
        }
        
        if self.message_id is not None:
            result["message_id"] = self.message_id
        
        if self.timestamp is not None:
            result["timestamp"] = self.timestamp
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebSocketMessage":
        """
        Create message from dictionary.
        
        Args:
            data: Message data as dictionary
            
        Returns:
            WebSocketMessage: Message instance
        """
        return cls(
            message_type=data.get("type", ""),
            data=data.get("data", {}),
            message_id=data.get("message_id"),
            timestamp=data.get("timestamp"),
        )
    
    def is_type(self, message_type: WebSocketMessageType) -> bool:
        """
        Check if message is of specific type.
        
        Args:
            message_type: Message type to check
            
        Returns:
            bool: True if message matches type
        """
        return self.message_type == message_type.value
    
    def __repr__(self) -> str:
        return f"WebSocketMessage(type={self.message_type}, id={self.message_id})"


@dataclass
class PendingStream:
    """Internal dataclass for tracking pending streams."""
    invocation_id: str
    target: str
    on_event: Optional[Any]
    on_end: Optional[Any]
    on_error: Optional[Any]
    end_future: Any
