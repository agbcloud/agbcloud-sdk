# -*- coding: utf-8 -*-
"""
WebSocket client module for AGB SDK.

This module provides both synchronous and asynchronous WebSocket clients
for real-time bidirectional communication with AGB sessions.
"""

from .async_client import AsyncWsClient, AsyncWsStreamHandle
from .sync_client import WsClient, WsStreamHandle
from .models import WsConnectionState, WebSocketMessage, WebSocketMessageType
from .exceptions import (
    WsProtocolError,
    WsHandshakeRejectedError,
    WsConnectionClosedError,
    WsRemoteError,
    WsCancelledError,
)

__all__ = [
    # Synchronous API (recommended for most use cases)
    "WsClient",
    "WsStreamHandle",
    # Asynchronous API (for advanced use cases)
    "AsyncWsClient",
    "AsyncWsStreamHandle",
    # Models and enums
    "WsConnectionState",
    "WebSocketMessage",
    "WebSocketMessageType",
    # Exceptions
    "WsProtocolError",
    "WsHandshakeRejectedError",
    "WsConnectionClosedError",
    "WsRemoteError",
    "WsCancelledError",
]
