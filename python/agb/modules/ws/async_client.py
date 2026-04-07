# -*- coding: utf-8 -*-
"""
Asynchronous WebSocket client for AGB SDK.

This module provides the low-level async WebSocket client implementation.
For most use cases, use the synchronous WsClient wrapper instead.
"""

import asyncio
import inspect
import json
import random
import ssl
import uuid
from typing import Any, Callable, Dict, List, Optional, Union

from agb.logger import get_logger

from .exceptions import (
    WsProtocolError,
    WsHandshakeRejectedError,
    WsConnectionClosedError,
    WsRemoteError,
    WsCancelledError,
)
from .models import WsConnectionState, PendingStream

logger = get_logger(__name__)

# Type aliases
ConnectionStateListener = Callable[[WsConnectionState, str], None]
OnEvent = Callable[[str, Dict[str, Any]], None]
OnEnd = Callable[[str, Dict[str, Any]], None]
OnError = Callable[[str, Exception], None]
PushCallback = Callable[[Dict[str, Any]], Any]


def _new_invocation_id() -> str:
    """Generate a new unique invocation ID."""
    return uuid.uuid4().hex


def _json_dumps(obj: Any) -> str:
    """Serialize object to JSON string."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def _extract_invocation_id(msg: Dict[str, Any]) -> str:
    """Extract invocation ID from message."""
    invocation_id = msg.get("invocationId") or msg.get("requestId")
    if not isinstance(invocation_id, str) or not invocation_id:
        raise WsProtocolError(
            "invocationId is required and must be a non-empty string"
        )
    return invocation_id


def _truncate_for_log(text: str, max_length: int = 1200) -> str:
    """Truncate text for logging."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def _mask_sensitive_data(text: str) -> str:
    """Mask sensitive data in text for logging."""
    # Simple implementation - can be enhanced
    return text


class AsyncWsStreamHandle:
    """
    Handle for an active WebSocket stream.
    
    Provides methods to write data, cancel the stream, and wait for completion.
    """
    
    def __init__(self, client: "AsyncWsClient", pending: PendingStream):
        """
        Initialize stream handle.
        
        Args:
            client: Parent WebSocket client
            pending: Pending stream metadata
        """
        self._client = client
        self._pending = pending
    
    @property
    def invocation_id(self) -> str:
        """Get the invocation ID for this stream."""
        return self._pending.invocation_id
    
    async def write(self, data: Dict[str, Any]) -> None:
        """
        Write data to the stream.
        
        Args:
            data: Data to send
        """
        await self._client._write_business(
            invocation_id=self._pending.invocation_id,
            target=self._pending.target,
            data=data,
        )
    
    async def cancel(self) -> None:
        """Cancel the stream."""
        self._client._cancel_pending(self._pending.invocation_id)
    
    async def wait_end(self) -> Dict[str, Any]:
        """
        Wait for the stream to end.
        
        Returns:
            Dict[str, Any]: Final response data
        """
        return await asyncio.shield(self._pending.end_future)


class AsyncWsClient:
    """
    Asynchronous WebSocket client for AGB SDK.
    
    This is the low-level async implementation. For most use cases,
    use the synchronous WsClient wrapper instead.
    
    Features:
    - Automatic reconnection
    - Message routing by invocation ID
    - Stream-based communication
    - Push message callbacks
    """
    
    def __init__(
        self,
        ws_url: str,
        ws_token: str,
        *,
        heartbeat_interval_s: float = 20.0,
        reconnect_initial_delay_s: float = 0.5,
        reconnect_max_delay_s: float = 5.0,
    ):
        """
        Initialize async WebSocket client.
        
        Args:
            ws_url: WebSocket server URL
            ws_token: Authentication token
            heartbeat_interval_s: Interval for heartbeat pings
            reconnect_initial_delay_s: Initial reconnection delay
            reconnect_max_delay_s: Maximum reconnection delay
        """
        self._ws_url = ws_url
        self._ws_token = ws_token
        
        self._heartbeat_interval_s = heartbeat_interval_s
        self._reconnect_initial_delay_s = reconnect_initial_delay_s
        self._reconnect_max_delay_s = reconnect_max_delay_s
        
        self._ws: Any = None
        self._recv_task: Optional[asyncio.Task[None]] = None
        self._heartbeat_task: Optional[asyncio.Task[None]] = None
        self._reconnect_task: Optional[asyncio.Task[None]] = None
        
        self._connect_lock = asyncio.Lock()
        self._pending_by_id: Dict[str, PendingStream] = {}
        self._state_listeners: List[ConnectionStateListener] = []
        self._callbacks_by_target: Dict[str, List[PushCallback]] = {}
        self._state: WsConnectionState = WsConnectionState.CLOSED
        self._closed_explicitly = False
    
    def on_connection_state_change(self, listener: ConnectionStateListener) -> None:
        """
        Register a connection state change listener.
        
        Args:
            listener: Callback function(state, reason)
        """
        self._state_listeners.append(listener)
    
    async def connect(self) -> None:
        """Establish WebSocket connection."""
        await self._ensure_open()
    
    def register_callback(
        self, target: str, callback: PushCallback
    ) -> Callable[[], None]:
        """
        Register a push callback routed by target.
        
        Args:
            target: Target identifier for routing
            callback: Callback function(payload)
            
        Returns:
            Callable: Unsubscribe function
        """
        if not isinstance(target, str) or not target:
            raise ValueError("target must be a non-empty string")
        if not callable(callback):
            raise ValueError("callback must be callable")
        
        self._callbacks_by_target.setdefault(target, []).append(callback)
        
        def _unsubscribe() -> None:
            self.unregister_callback(target, callback)
        
        return _unsubscribe
    
    def unregister_callback(
        self, target: str, callback: Optional[PushCallback] = None
    ) -> None:
        """
        Unregister a previously registered callback.
        
        Args:
            target: Target identifier
            callback: Specific callback to remove, or None to remove all
        """
        if not isinstance(target, str) or not target:
            raise ValueError("target must be a non-empty string")
        
        if callback is None:
            self._callbacks_by_target.pop(target, None)
            return
        
        callbacks = self._callbacks_by_target.get(target)
        if not callbacks:
            return
        
        self._callbacks_by_target[target] = [
            cb for cb in callbacks if cb is not callback
        ]
        
        if not self._callbacks_by_target[target]:
            self._callbacks_by_target.pop(target, None)
    
    async def close(self) -> None:
        """Close the WebSocket connection."""
        self._closed_explicitly = True
        
        if self._reconnect_task is not None:
            self._reconnect_task.cancel()
            self._reconnect_task = None
        
        await self._close_transport("explicit close")
    
    async def call_stream(
        self,
        *,
        target: str,
        data: Dict[str, Any],
        on_event: Optional[OnEvent],
        on_end: Optional[OnEnd],
        on_error: Optional[OnError],
    ) -> AsyncWsStreamHandle:
        """
        Initiate a streaming call.
        
        Args:
            target: Target endpoint
            data: Initial data to send
            on_event: Callback for stream events
            on_end: Callback for stream completion
            on_error: Callback for errors
            
        Returns:
            AsyncWsStreamHandle: Handle for the stream
        """
        if not isinstance(target, str) or not target:
            raise ValueError("target must be a non-empty string")
        if not isinstance(data, dict):
            raise ValueError("data must be a dict")
        
        await self._ensure_open()
        
        invocation_id = _new_invocation_id()
        loop = asyncio.get_running_loop()
        end_future: asyncio.Future[Dict[str, Any]] = loop.create_future()
        
        pending = PendingStream(
            invocation_id=invocation_id,
            target=target,
            on_event=on_event,
            on_end=on_end,
            on_error=on_error,
            end_future=end_future,
        )
        self._pending_by_id[invocation_id] = pending
        
        try:
            await self._write_business(
                invocation_id=invocation_id,
                target=target,
                data=data,
            )
        except Exception as e:
            self._pending_by_id.pop(invocation_id, None)
            if not end_future.done():
                end_future.set_exception(e)
            if on_error is not None:
                on_error(invocation_id, e)
            raise
        
        return AsyncWsStreamHandle(self, pending)
    
    async def send_message(
        self,
        *,
        target: str,
        data: Dict[str, Any],
    ) -> None:
        """
        Send a one-way message.
        
        Args:
            target: Target endpoint
            data: Data to send
        """
        await self._ensure_open()
        
        try:
            invocation_id = _new_invocation_id()
            await self._write_business(
                invocation_id=invocation_id,
                target=target,
                data=data,
            )
        except Exception as e:
            logger.warning(f"Failed to send message: {e}")
    
    def _set_state(self, state: WsConnectionState, reason: str) -> None:
        """Update connection state and notify listeners."""
        self._state = state
        for listener in list(self._state_listeners):
            try:
                listener(state, reason)
            except Exception:
                logger.exception("ConnectionState listener failed")
    
    def _log_frame(self, direction: str, payload: Dict[str, Any]) -> None:
        """Log WebSocket frame for debugging."""
        try:
            raw = _json_dumps(payload)
        except Exception:
            raw = str(payload)
        
        masked = _mask_sensitive_data(raw)
        truncated = _truncate_for_log(masked, 1200)
        logger.debug(f"WS {direction} {truncated}")
    
    async def _ensure_open(self) -> None:
        """Ensure WebSocket connection is open."""
        async with self._connect_lock:
            if self._ws is not None and self._recv_task is not None:
                return
            await self._open()
    
    async def _open(self) -> None:
        """Open WebSocket connection."""
        if self._closed_explicitly:
            raise WsConnectionClosedError("WS client is closed")
        
        try:
            import websockets   # type: ignore[import-not-found]
            from websockets.exceptions import InvalidStatus  # type: ignore[import-not-found]
        except Exception as e:
            raise WsConnectionClosedError(
                "Missing dependency: install 'websockets' to use WS features"
            ) from e
        
        self._set_state(WsConnectionState.RECONNECTING, "connecting")
        logger.info(f"WS CONNECT url={self._ws_url}")
        
        headers = {"X-Access-Token": self._ws_token}
        
        # Build SSL context with certifi CA bundle
        ssl_context: Any = None
        if self._ws_url.startswith("wss://"):
            ssl_context = ssl.create_default_context()
            try:
                import certifi
                ssl_context.load_verify_locations(certifi.where())
            except ImportError:
                logger.debug(
                    "certifi not available; falling back to system CA certificates"
                )
        
        try:
            ws = await websockets.connect(
                self._ws_url,
                ping_interval=None,
                additional_headers=headers,
                ssl=ssl_context,
            )
        except InvalidStatus as e:
            raise WsHandshakeRejectedError(
                f"WS connection rejected: HTTP {e.response.status_code}; "
                f"url={self._ws_url}"
            ) from e
        
        self._ws = ws
        self._set_state(WsConnectionState.OPEN, "connected")
        logger.info(f"WS CONNECTED url={self._ws_url}")
        
        self._recv_task = asyncio.create_task(self._recv_loop())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
    
    async def _close_transport(self, reason: str) -> None:
        """Close WebSocket transport."""
        try:
            current = asyncio.current_task()
        except RuntimeError:
            current = None
        
        ws = self._ws
        self._ws = None
        
        if self._recv_task is not None:
            if self._recv_task is not current:
                self._recv_task.cancel()
            self._recv_task = None
        
        if self._heartbeat_task is not None:
            if self._heartbeat_task is not current:
                self._heartbeat_task.cancel()
            self._heartbeat_task = None
        
        if ws is not None:
            try:
                await ws.close()
            except Exception:
                pass
        
        logger.info(f"WS CLOSED reason={reason}")
        self._set_state(WsConnectionState.CLOSED, reason)
    
    async def _heartbeat_loop(self) -> None:
        """Heartbeat loop to keep connection alive."""
        while True:
            await asyncio.sleep(self._heartbeat_interval_s)
            ws = self._ws
            if ws is None:
                continue
            
            try:
                pong_waiter = await ws.ping()
                await asyncio.wait_for(
                    pong_waiter, timeout=self._heartbeat_interval_s
                )
            except Exception as e:
                await self._on_transport_error(f"heartbeat failed: {e}")
                return
    
    async def _recv_loop(self) -> None:
        """Receive loop for incoming messages."""
        ws = self._ws
        if ws is None:
            return
        
        try:
            async for raw in ws:
                try:
                    self._handle_incoming(raw)
                except WsProtocolError as e:
                    raw_str = _truncate_for_log(
                        _mask_sensitive_data(str(raw)), 2000
                    )
                    logger.warning(
                        f"WS protocol error (ignored): {e}; raw={raw_str}"
                    )
                    try:
                        msg_any = json.loads(raw)
                        if isinstance(msg_any, dict):
                            invocation_id = None
                            try:
                                invocation_id = _extract_invocation_id(msg_any)
                            except Exception:
                                invocation_id = None
                            if invocation_id:
                                pending = self._pending_by_id.pop(invocation_id, None)
                                if pending is not None:
                                    if pending.on_error is not None:
                                        try:
                                            pending.on_error(invocation_id, e)
                                        except Exception:
                                            logger.exception("on_error callback failed")
                                    if not pending.end_future.done():
                                        pending.end_future.set_exception(e)
                    except Exception:
                        pass
                    continue
            
            await self._on_transport_error("connection closed")
        except Exception as e:
            await self._on_transport_error(f"recv loop closed: {e}")
    
    def _handle_incoming(self, raw: Any) -> None:
        """Handle incoming WebSocket message."""
        try:
            msg = json.loads(raw)
        except Exception as e:
            raise WsProtocolError(f"Invalid JSON message: {e}") from e
        
        if not isinstance(msg, dict):
            raise WsProtocolError("Message must be a JSON object")
        
        invocation_id = _extract_invocation_id(msg)
        source = msg.get("source")
        target = msg.get("target")
        data_any = msg.get("data")
        
        # Parse data
        if isinstance(data_any, dict):
            data = data_any
        elif isinstance(data_any, str):
            try:
                parsed = json.loads(data_any)
            except Exception as e:
                raise WsProtocolError(
                    f"data is a string but not valid JSON: {e}"
                ) from e
            if not isinstance(parsed, dict):
                raise WsProtocolError(
                    "data is a string but decoded JSON is not an object"
                )
            data = parsed
        else:
            raise WsProtocolError("data is required and must be an object")
        
        self._log_frame(
            "<<",
            {
                "invocationId": invocation_id,
                "source": source,
                "target": target,
                "data": data,
            },
        )
        
        pending = self._pending_by_id.get(invocation_id)
        
        # Handle push messages (no pending stream)
        if pending is None:
            self._handle_push_message(invocation_id, source, target, data)
            return
        
        # Handle stream messages
        self._handle_stream_message(invocation_id, pending, data)
    
    def _handle_push_message(
        self,
        invocation_id: str,
        source: Optional[str],
        target: Optional[str],
        data: Dict[str, Any],
    ) -> None:
        """Handle push message (no pending stream)."""
        if not target:
            logger.debug(f"Dropping message with no target: {invocation_id}")
            return
        
        route_target = target
        if route_target == "SDK" and isinstance(source, str) and source and source != "SDK":
            route_target = source
        
        callbacks = list(self._callbacks_by_target.get(route_target, []))
        if not callbacks:
            logger.debug(
                f"Dropping push message with no callback: "
                f"requestId={invocation_id}, target={route_target}"
            )
            return
        
        payload = {
            "requestId": invocation_id,
            "target": route_target,
            "data": data,
        }
        
        for cb in callbacks:
            try:
                r = cb(payload)
                if inspect.isawaitable(r):
                    asyncio.create_task(r)  # type: ignore[arg-type]
            except Exception:
                logger.exception("Push callback failed")
    
    def _handle_stream_message(
        self,
        invocation_id: str,
        pending: PendingStream,
        data: Dict[str, Any],
    ) -> None:
        """Handle stream message."""

        # Check for explicit error
        if isinstance(data.get("error"), str) and data.get("error"):
            err = WsRemoteError(_truncate_for_log(_mask_sensitive_data(str(data)), 2000))
            if pending.on_error is not None:
                pending.on_error(invocation_id, err)
            if not pending.end_future.done():
                pending.end_future.set_exception(err)
            self._pending_by_id.pop(invocation_id, None)
            return

        phase = data.get("phase")

        if phase == "event":
            if pending.on_event is not None:
                pending.on_event(invocation_id, data)
            return

        if phase == "end":
            if pending.on_end is not None:
                pending.on_end(invocation_id, data)
            if not pending.end_future.done():
                pending.end_future.set_result(data)
            self._pending_by_id.pop(invocation_id, None)
            return

        if phase == "error":
            err = WsRemoteError(_truncate_for_log(_mask_sensitive_data(str(data)), 2000))
            if pending.on_error is not None:
                pending.on_error(invocation_id, err)
            if not pending.end_future.done():
                pending.end_future.set_exception(err)
            self._pending_by_id.pop(invocation_id, None)
            return

        # Unknown or missing phase
        if phase is None:
            phase_err = WsProtocolError(
                "WS message missing required data.phase; "
                f"invocationId={invocation_id}, data={_truncate_for_log(_mask_sensitive_data(str(data)), 2000)}"
            )
        else:
            phase_err = WsProtocolError(
                "WS message has unsupported data.phase; "
                f"invocationId={invocation_id}, phase={phase!r}, data={_truncate_for_log(_mask_sensitive_data(str(data)), 2000)}"
            )
        if pending.on_error is not None:
            pending.on_error(invocation_id, phase_err)
        if not pending.end_future.done():
            pending.end_future.set_exception(phase_err)
        self._pending_by_id.pop(invocation_id, None)
    
    async def _on_transport_error(self, reason: str) -> None:
        """Handle transport error."""
        if self._closed_explicitly:
            await self._close_transport(reason)
            return
        
        logger.warning(f"WS transport error: {reason}")
        await self._close_transport(reason)
        self._fail_all_pending(WsConnectionClosedError(reason))
        
        if self._reconnect_task is None or self._reconnect_task.done():
            self._reconnect_task = asyncio.create_task(self._reconnect_loop())
    
    def _fail_all_pending(self, err: Exception) -> None:
        """Fail all pending streams."""
        pending_items = list(self._pending_by_id.items())
        self._pending_by_id.clear()
        
        for invocation_id, pending in pending_items:
            if pending.on_error is not None:
                try:
                    pending.on_error(invocation_id, err)
                except Exception:
                    logger.exception("on_error callback failed")
            
            if not pending.end_future.done():
                pending.end_future.set_exception(err)
    
    async def _reconnect_loop(self) -> None:
        """Reconnection loop."""
        delay = self._reconnect_initial_delay_s
        
        while not self._closed_explicitly:
            try:
                await asyncio.sleep(delay + random.random() * 0.1)
                async with self._connect_lock:
                    if self._ws is not None and self._recv_task is not None:
                        return
                    await self._open()
                return
            except Exception as e:
                self._set_state(
                    WsConnectionState.RECONNECTING, f"reconnect failed: {e}"
                )
                delay = min(delay * 1.5, self._reconnect_max_delay_s)
                continue
    
    async def _write_business(
        self,
        *,
        invocation_id: str,
        target: str,
        data: Dict[str, Any],
    ) -> None:
        """Write business message to WebSocket."""
        ws = self._ws
        if ws is None:
            raise WsConnectionClosedError("WS is not connected")
        
        payload = {
            "invocationId": invocation_id,
            "source": "SDK",
            "target": target,
            "data": data,
        }
        
        self._log_frame(">>", payload)
        await ws.send(_json_dumps(payload))
    
    def _cancel_pending(self, invocation_id: str) -> None:
        """Cancel a pending stream."""
        pending = self._pending_by_id.pop(invocation_id, None)
        if pending is None:
            return
        
        if pending.end_future.done():
            return
        
        err = WsCancelledError(f"Stream {invocation_id} was cancelled by caller")
        
        if pending.on_error is not None:
            try:
                pending.on_error(invocation_id, err)
            except Exception:
                logger.exception("on_error callback failed during cancel")
        
        pending.end_future.set_exception(err)
