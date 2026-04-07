# -*- coding: utf-8 -*-
"""
Synchronous WebSocket client for AGB SDK.

This module provides a synchronous wrapper around the async WebSocket client,
making it easy to use in synchronous code. It runs the async client in a
background thread with its own event loop.
"""

import asyncio
import threading
from concurrent.futures import Future
from typing import Any, Callable, Dict, Optional

from agb.logger import get_logger

from .async_client import AsyncWsClient, AsyncWsStreamHandle
from .models import WsConnectionState
from .exceptions import WsError

logger = get_logger(__name__)

# Type aliases
PushCallback = Callable[[Dict[str, Any]], Any]
OnEvent = Callable[[str, Dict[str, Any]], None]
OnEnd = Callable[[str, Dict[str, Any]], None]
OnError = Callable[[str, Exception], None]


class WsStreamHandle:
    """
    Synchronous handle for an active WebSocket stream.
    
    This is a synchronous wrapper around AsyncWsStreamHandle that runs
    async operations in a background thread.
    """
    
    def __init__(
        self,
        client: "WsClient",
        handle: AsyncWsStreamHandle,
        *,
        loop: asyncio.AbstractEventLoop,
    ):
        """
        Initialize synchronous stream handle.
        
        Args:
            client: Parent synchronous WebSocket client
            handle: Underlying async stream handle
            loop: Event loop running in background thread
        """
        self._client = client
        self._handle = handle
        self._loop = loop
    
    @property
    def invocation_id(self) -> str:
        """Get the invocation ID for this stream."""
        return self._handle.invocation_id
    
    def write(self, data: Dict[str, Any]) -> None:
        """
        Write data to the stream (synchronous).
        
        Args:
            data: Data to send
        """
        fut = asyncio.run_coroutine_threadsafe(
            self._handle.write(data), self._loop
        )
        fut.result(timeout=30.0)
    
    def cancel(self) -> None:
        """Cancel the stream (synchronous)."""
        fut = asyncio.run_coroutine_threadsafe(
            self._handle.cancel(), self._loop
        )
        fut.result()
    
    def wait_end(self) -> Dict[str, Any]:
        """
        Wait for the stream to end (synchronous).
        
        Returns:
            Dict[str, Any]: Final response data
        """
        fut = asyncio.run_coroutine_threadsafe(
            self._handle.wait_end(), self._loop
        )
        return fut.result(timeout=300.0)


class WsClient:
    """
    Synchronous WebSocket client for AGB SDK.
    
    This client provides a synchronous API by running an async WebSocket
    client in a background thread with its own event loop. This makes it
    easy to use WebSocket functionality in synchronous code.
    
    Features:
    - Automatic reconnection
    - Message routing by invocation ID
    - Stream-based communication
    - Push message callbacks
    - Thread-safe operation
    
    Example:
        ```python
        # Create client
        ws_client = WsClient(
            ws_url="wss://example.com/ws",
            ws_token="your_token",
        )
        
        # Connect
        ws_client.connect()
        
        # Register callback
        def on_message(payload):
            print(f"Received: {payload}")
        
        ws_client.register_callback("my_target", on_message)
        
        # Send message
        ws_client.send_message(
            target="my_target",
            data={"action": "ping"},
        )
        
        # Close
        ws_client.close()
        ```
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
        Initialize synchronous WebSocket client.
        
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
        
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._thread_started = threading.Event()
        self._thread_error: Optional[BaseException] = None
        self._async_client: Optional[AsyncWsClient] = None
        self._closed = False
    
    def _ensure_thread(self) -> None:
        """Ensure background thread and event loop are running."""
        if self._closed:
            raise WsError("WS client is closed")
        
        if self._thread is not None and self._loop is not None:
            return
        
        loop = asyncio.new_event_loop()
        self._loop = loop
        
        def _runner() -> None:
            try:
                asyncio.set_event_loop(loop)
                self._async_client = AsyncWsClient(
                    ws_url=self._ws_url,
                    ws_token=self._ws_token,
                    heartbeat_interval_s=self._heartbeat_interval_s,
                    reconnect_initial_delay_s=self._reconnect_initial_delay_s,
                    reconnect_max_delay_s=self._reconnect_max_delay_s,
                )
                self._thread_started.set()
                loop.run_forever()
            except BaseException as e:
                self._thread_error = e
                self._thread_started.set()
            finally:
                try:
                    loop.close()
                except Exception:
                    pass
        
        t = threading.Thread(
            target=_runner, name="agb-ws-loop", daemon=True
        )
        self._thread = t
        t.start()
        
        self._thread_started.wait(timeout=10.0)
        
        if self._thread_error is not None:
            raise WsError(
                f"Failed to start WS loop thread: {self._thread_error}"
            )
        
        if self._async_client is None:
            raise WsError("Failed to initialize async WS client")
    
    def _call_in_loop(self, fn: Callable[[AsyncWsClient], Any]) -> Any:
        """
        Execute a function in the background event loop.
        
        Args:
            fn: Function to execute with async client
            
        Returns:
            Any: Result from the function
        """
        self._ensure_thread()
        assert self._loop is not None
        assert self._async_client is not None
        
        fut: Future[Any] = Future()
        async_client = self._async_client
        
        def _do() -> None:
            try:
                fut.set_result(fn(async_client))
            except BaseException as e:
                fut.set_exception(e)
        
        self._loop.call_soon_threadsafe(_do)
        return fut.result(timeout=30.0)
    
    def on_connection_state_change(
        self, listener: Callable[[WsConnectionState, str], None]
    ) -> None:
        """
        Register a connection state change listener.
        
        Args:
            listener: Callback function(state, reason)
        """
        self._call_in_loop(lambda c: c.on_connection_state_change(listener))
    
    def connect(self) -> None:
        """Establish WebSocket connection (synchronous)."""
        self._ensure_thread()
        assert self._loop is not None
        assert self._async_client is not None
        
        f = asyncio.run_coroutine_threadsafe(
            self._async_client.connect(), self._loop
        )
        f.result(timeout=30.0)
    
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
        unsubscribe = self._call_in_loop(
            lambda c: c.register_callback(target, callback)
        )
        
        def _unsub() -> None:
            self._call_in_loop(lambda c: unsubscribe())
        
        return _unsub
    
    def unregister_callback(
        self, target: str, callback: Optional[PushCallback] = None
    ) -> None:
        """
        Unregister a previously registered callback.
        
        Args:
            target: Target identifier
            callback: Specific callback to remove, or None to remove all
        """
        self._call_in_loop(
            lambda c: c.unregister_callback(target, callback)
        )
    
    def close(self) -> None:
        """Close the WebSocket connection (synchronous)."""
        if self._closed:
            return
        
        self._closed = True
        loop = self._loop
        client = self._async_client
        
        if loop is None or client is None:
            return
        
        try:
            f = asyncio.run_coroutine_threadsafe(client.close(), loop)
            f.result(timeout=10.0)
        except Exception:
            pass
        
        try:
            loop.call_soon_threadsafe(loop.stop)
        except Exception:
            pass
    
    def call_stream(
        self,
        *,
        target: str,
        data: Dict[str, Any],
        on_event: Optional[OnEvent],
        on_end: Optional[OnEnd],
        on_error: Optional[OnError],
    ) -> WsStreamHandle:
        """
        Initiate a streaming call (synchronous).
        
        Args:
            target: Target endpoint
            data: Initial data to send
            on_event: Callback for stream events
            on_end: Callback for stream completion
            on_error: Callback for errors
            
        Returns:
            WsStreamHandle: Handle for the stream
        """
        self._ensure_thread()
        assert self._loop is not None
        assert self._async_client is not None
        
        f = asyncio.run_coroutine_threadsafe(
            self._async_client.call_stream(
                target=target,
                data=data,
                on_event=on_event,
                on_end=on_end,
                on_error=on_error,
            ),
            self._loop,
        )
        
        async_handle = f.result()
        return WsStreamHandle(self, async_handle, loop=self._loop)
    
    def send_message(
        self,
        *,
        target: str,
        data: Dict[str, Any],
    ) -> None:
        """
        Send a one-way message (synchronous).
        
        Args:
            target: Target endpoint
            data: Data to send
        """
        self._ensure_thread()
        assert self._loop is not None
        assert self._async_client is not None
        
        f = asyncio.run_coroutine_threadsafe(
            self._async_client.send_message(
                target=target,
                data=data,
            ),
            self._loop,
        )
        f.result(timeout=30.0)
    
    def __enter__(self) -> "WsClient":
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
