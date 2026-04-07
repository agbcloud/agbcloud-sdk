# -*- coding: utf-8 -*-
"""
WebSocket-specific exceptions for AGB SDK.
"""


class WsError(Exception):
    """Base exception for WebSocket errors."""
    pass


class WsProtocolError(WsError):
    """Raised when a WS message violates the expected protocol."""
    pass


class WsHandshakeRejectedError(WsError):
    """Raised when backend rejects connection-level handshake."""
    pass


class WsConnectionClosedError(WsError):
    """Raised when WS connection is closed while a stream is pending."""
    pass


class WsRemoteError(WsError):
    """Raised when backend sends an error for an invocation."""
    pass


class WsCancelledError(WsError):
    """Raised when a stream is cancelled by the caller."""
    pass
