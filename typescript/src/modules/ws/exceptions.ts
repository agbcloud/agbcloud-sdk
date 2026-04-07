import { createErrorClass } from "../../exceptions";

/** Base class for all WebSocket errors. */
export const WsError = createErrorClass("WsError", "WebSocket error");



/** Raised when a WS message violates the expected protocol. */
export const WsProtocolError = createErrorClass("WsProtocolError", "WebSocket protocol error");

/** Raised when backend rejects connection-level handshake. */
export const WsHandshakeRejectedError = createErrorClass("WsHandshakeRejectedError", "WebSocket handshake rejected");

/** Raised when WS connection is closed while a stream is pending. */
export const WsConnectionClosedError = createErrorClass("WsConnectionClosedError", "WebSocket connection closed");

/** Raised when backend sends an error for an invocation. */
export const WsRemoteError = createErrorClass("WsRemoteError", "WebSocket remote error");

/** Raised when a stream is cancelled by the caller. */
export const WsCancelledError = createErrorClass("WsCancelledError", "WebSocket stream cancelled");
