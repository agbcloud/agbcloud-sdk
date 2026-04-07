# -*- coding: utf-8 -*-
"""
Unit tests for AGB SDK WebSocket long connection (sync WsClient).

Tests WebSocket protocol compliance, stream routing, cancellation,
disconnect handling, and error propagation using a local websockets server.
The sync WsClient is the primary public API; it wraps AsyncWsClient in a
background thread.
"""

import asyncio
import json
import threading
import time
from typing import Any, Callable

import pytest

from agb.modules.ws.sync_client import WsClient
from agb.modules.ws.exceptions import (
    WsCancelledError,
    WsConnectionClosedError,
    WsRemoteError,
)


class _WsServerContext:
    """Helper: run a websockets server in a background thread."""

    def __init__(self, handler: Callable):
        self._handler = handler
        self._loop: asyncio.AbstractEventLoop = None  # type: ignore[assignment]
        self._thread: threading.Thread = None  # type: ignore[assignment]
        self._started = threading.Event()
        self._port: int = 0
        self._server: Any = None

    @property
    def ws_url(self) -> str:
        return f"ws://127.0.0.1:{self._port}"

    def start(self) -> str:
        """Start the server and return ws_url."""

        def _runner() -> None:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

            async def _serve() -> None:
                import websockets

                # websockets 11+ requires async with context to start listening
                async with websockets.serve(
                    self._handler, host="127.0.0.1", port=0
                ) as server:
                    self._server = server
                    self._port = server.sockets[0].getsockname()[1]
                    self._started.set()
                    # keep alive until loop.stop()
                    await asyncio.Future()

            try:
                self._loop.run_until_complete(_serve())
            except Exception:
                pass

        self._thread = threading.Thread(target=_runner, daemon=True)
        self._thread.start()
        assert self._started.wait(timeout=5), "WS server failed to start"
        return self.ws_url

    def stop(self) -> None:
        """Stop the server and join the thread."""
        if self._server is not None and self._loop is not None:
            # Gracefully close the server to avoid "Event loop is closed" warnings
            async def _shutdown() -> None:
                self._server.close()
                await self._server.wait_closed()
                # Cancel the pending asyncio.Future() to exit the async with context
                for task in asyncio.all_tasks(self._loop):
                    if task is not asyncio.current_task(self._loop):
                        task.cancel()

            try:
                asyncio.run_coroutine_threadsafe(_shutdown(), self._loop).result(timeout=5)
            except Exception:
                pass
        if self._loop is not None:
            self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5)


class TestWsLongConnection:
    """WebSocket long connection unit tests using a local WS server
    and the synchronous WsClient wrapper."""

    @staticmethod
    def _make_client(ws_url: str, **kwargs: Any) -> WsClient:
        return WsClient(ws_url=ws_url, ws_token="test_token", **kwargs)

    # ── basic lifecycle ───────────────────────────────────────────

    def test_ws_client_connect_and_close(self):
        """Test basic WsClient connect and close lifecycle."""
        async def ws_handler(ws):
            assert ws.request is not None
            assert ws.request.headers.get("X-Access-Token") == "test_token"
            try:
                await ws.recv()
            except Exception:
                pass

        ctx = _WsServerContext(ws_handler)
        ws_url = ctx.start()
        try:
            client = self._make_client(ws_url)
            client.connect()
            client.close()
        finally:
            ctx.stop()

    # ── stream routing success ────────────────────────────────────

    def test_call_stream_connect_and_routing_success(self):
        """Test call_stream delivers events and end correctly."""
        received_frames: list = []

        async def ws_handler(ws):
            assert ws.request is not None
            assert (
                ws.request.headers.get("X-Access-Token") == "test_token"
            ), "X-Access-Token header not set on WS connect"

            req_raw = await ws.recv()
            req = json.loads(req_raw)
            received_frames.append(req)
            assert req["source"] == "SDK"
            assert req["target"] == "wuying_codespace"
            assert req["data"]["method"] == "run_code"
            invocation_id = req["invocationId"]

            await ws.send(
                json.dumps(
                    {
                        "invocationId": invocation_id,
                        "target": req["target"],
                        "data": {
                            "method": "run_code",
                            "mode": "stream",
                            "phase": "event",
                            "seq": 1,
                            "eventType": "stdout",
                            "chunk": "hello ",
                        },
                    }
                )
            )
            await ws.send(
                json.dumps(
                    {
                        "invocationId": invocation_id,
                        "target": req["target"],
                        "data": {
                            "method": "run_code",
                            "mode": "stream",
                            "phase": "end",
                            "seq": 2,
                            "status": "finished",
                        },
                    }
                )
            )

        ctx = _WsServerContext(ws_handler)
        ws_url = ctx.start()
        try:
            client = self._make_client(ws_url)

            events: list = []
            ended: list = []
            errors: list = []

            def on_event(invocation_id: str, data: dict) -> None:
                assert invocation_id
                events.append(data)

            def on_end(invocation_id: str, data: dict) -> None:
                assert invocation_id
                ended.append(data)

            def on_error(invocation_id: str, err: Exception) -> None:
                assert invocation_id
                errors.append(err)

            handle = client.call_stream(
                target="wuying_codespace",
                data={"method": "run_code", "mode": "stream", "params": {"code": "x=1"}},
                on_event=on_event,
                on_end=on_end,
                on_error=on_error,
            )

            end_data = handle.wait_end()

            assert errors == []
            assert len(events) == 1
            assert events[0]["eventType"] == "stdout"
            assert events[0]["chunk"] == "hello "
            assert len(ended) == 1
            assert end_data["status"] == "finished"
            client.close()
        finally:
            ctx.stop()

    # ── cancel ────────────────────────────────────────────────────

    def test_call_stream_cancel_raises_ws_cancelled_error(self):
        """Test cancel() causes wait_end() to raise WsCancelledError."""
        server_received = threading.Event()

        async def ws_handler(ws):
            assert ws.request is not None
            assert ws.request.headers.get("X-Access-Token") == "test_token"
            await ws.recv()
            server_received.set()
            await asyncio.sleep(10)

        ctx = _WsServerContext(ws_handler)
        ws_url = ctx.start()
        try:
            client = self._make_client(ws_url)

            errors: list = []

            def on_error(invocation_id: str, err: Exception) -> None:
                assert invocation_id
                errors.append(err)

            handle = client.call_stream(
                target="wuying_codespace",
                data={"method": "run_code", "mode": "stream"},
                on_event=None,
                on_end=None,
                on_error=on_error,
            )
            assert server_received.wait(timeout=3), "Server did not receive message"

            handle.cancel()
            with pytest.raises(WsCancelledError):
                handle.wait_end()

            assert len(errors) == 1
            assert isinstance(errors[0], WsCancelledError)
            client.close()
        finally:
            ctx.stop()

    # ── disconnect ────────────────────────────────────────────────

    def test_disconnect_fails_pending_streams(self):
        """Test server disconnect fails pending streams with connection closed error."""
        async def ws_handler(ws):
            assert ws.request is not None
            assert ws.request.headers.get("X-Access-Token") == "test_token"
            await ws.recv()
            await ws.close(code=1001, reason="server shutdown")

        ctx = _WsServerContext(ws_handler)
        ws_url = ctx.start()
        try:
            client = self._make_client(ws_url, reconnect_initial_delay_s=999)

            errors: list = []

            def on_error(invocation_id: str, err: Exception) -> None:
                errors.append(err)

            handle = client.call_stream(
                target="wuying_codespace",
                data={"method": "run_code", "mode": "stream"},
                on_event=None,
                on_end=None,
                on_error=on_error,
            )

            with pytest.raises(Exception) as excinfo:
                handle.wait_end()
            err_msg = str(excinfo.value).lower()
            assert "closed" in err_msg or "disconnect" in err_msg
            assert len(errors) >= 1
            client.close()
        finally:
            ctx.stop()

    # ── protocol error ────────────────────────────────────────────

    def test_missing_invocation_id_is_protocol_error(self):
        """Test message without invocationId triggers protocol error."""
        async def ws_handler(ws):
            assert ws.request is not None
            assert ws.request.headers.get("X-Access-Token") == "test_token"

            req_raw = await ws.recv()
            req = json.loads(req_raw)
            assert req["source"] == "SDK"
            await ws.send(
                json.dumps(
                    {
                        "target": req["target"],
                        "data": {"phase": "end", "status": "finished"},
                    }
                )
            )

        ctx = _WsServerContext(ws_handler)
        ws_url = ctx.start()
        try:
            client = self._make_client(ws_url, reconnect_initial_delay_s=999)

            errors: list = []

            def on_error(invocation_id: str, err: Exception) -> None:
                errors.append(err)

            handle = client.call_stream(
                target="wuying_codespace",
                data={"method": "run_code", "mode": "stream"},
                on_event=None,
                on_end=None,
                on_error=on_error,
            )

            with pytest.raises(Exception) as excinfo:
                handle.wait_end()
            err_msg = str(excinfo.value).lower()
            assert "invocationid" in err_msg or "closed" in err_msg
            client.close()
        finally:
            ctx.stop()

    # ── server errors ─────────────────────────────────────────────

    def test_server_error_with_data_error_field(self):
        """Test server sending data.error string triggers WsRemoteError."""
        async def ws_handler(ws):
            assert ws.request is not None
            assert ws.request.headers.get("X-Access-Token") == "test_token"

            req_raw = await ws.recv()
            req = json.loads(req_raw)
            invocation_id = req["invocationId"]

            await ws.send(
                json.dumps(
                    {
                        "invocationId": invocation_id,
                        "source": "WEBSOCKET_SERVER",
                        "data": {"error": "bad request"},
                    }
                )
            )

        ctx = _WsServerContext(ws_handler)
        ws_url = ctx.start()
        try:
            client = self._make_client(ws_url)

            errors: list = []

            def on_error(invocation_id: str, err: Exception) -> None:
                errors.append(err)

            handle = client.call_stream(
                target="wuying_codespace",
                data={"method": "run_code", "mode": "stream"},
                on_event=None,
                on_end=None,
                on_error=on_error,
            )

            with pytest.raises(WsRemoteError) as excinfo:
                handle.wait_end()
            assert "bad request" in str(excinfo.value).lower()
            assert len(errors) == 1
            assert isinstance(errors[0], WsRemoteError)
            assert "bad request" in str(errors[0]).lower()
            client.close()
        finally:
            ctx.stop()

    def test_phase_error_triggers_remote_error(self):
        """Test message with phase='error' triggers WsRemoteError."""
        async def ws_handler(ws):
            assert ws.request is not None
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            invocation_id = req["invocationId"]

            await ws.send(
                json.dumps(
                    {
                        "invocationId": invocation_id,
                        "target": req["target"],
                        "data": {
                            "phase": "error",
                            "message": "execution failed",
                        },
                    }
                )
            )

        ctx = _WsServerContext(ws_handler)
        ws_url = ctx.start()
        try:
            client = self._make_client(ws_url)

            errors: list = []

            def on_error(invocation_id: str, err: Exception) -> None:
                errors.append(err)

            handle = client.call_stream(
                target="wuying_codespace",
                data={"method": "run_code", "mode": "stream"},
                on_event=None,
                on_end=None,
                on_error=on_error,
            )

            with pytest.raises(WsRemoteError):
                handle.wait_end()
            assert len(errors) == 1
            assert isinstance(errors[0], WsRemoteError)
            client.close()
        finally:
            ctx.stop()

    # ── multiple events ───────────────────────────────────────────

    def test_multiple_events_before_end(self):
        """Test multiple event messages followed by end are all delivered."""
        async def ws_handler(ws):
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            invocation_id = req["invocationId"]

            for i in range(3):
                await ws.send(
                    json.dumps(
                        {
                            "invocationId": invocation_id,
                            "target": req["target"],
                            "data": {
                                "phase": "event",
                                "seq": i + 1,
                                "eventType": "stdout",
                                "chunk": f"line{i}\n",
                            },
                        }
                    )
                )
            await ws.send(
                json.dumps(
                    {
                        "invocationId": invocation_id,
                        "target": req["target"],
                        "data": {
                            "phase": "end",
                            "seq": 4,
                            "status": "finished",
                            "executionCount": 1,
                        },
                    }
                )
            )

        ctx = _WsServerContext(ws_handler)
        ws_url = ctx.start()
        try:
            client = self._make_client(ws_url)

            events: list = []
            ended: list = []

            handle = client.call_stream(
                target="wuying_codespace",
                data={"method": "run_code", "mode": "stream", "params": {"code": "for i in range(3): print(i)"}},
                on_event=lambda inv, d: events.append(d),
                on_end=lambda inv, d: ended.append(d),
                on_error=None,
            )

            end_data = handle.wait_end()

            assert len(events) == 3
            assert [e["chunk"] for e in events] == ["line0\n", "line1\n", "line2\n"]
            assert len(ended) == 1
            assert end_data["status"] == "finished"
            assert end_data["executionCount"] == 1
            client.close()
        finally:
            ctx.stop()

    # ── no callbacks ──────────────────────────────────────────────

    def test_call_stream_no_callbacks(self):
        """Test call_stream works with all callbacks set to None."""
        async def ws_handler(ws):
            req_raw = await ws.recv()
            req = json.loads(req_raw)
            invocation_id = req["invocationId"]

            await ws.send(
                json.dumps(
                    {
                        "invocationId": invocation_id,
                        "target": req["target"],
                        "data": {
                            "phase": "event",
                            "seq": 1,
                            "eventType": "stdout",
                            "chunk": "output\n",
                        },
                    }
                )
            )
            await ws.send(
                json.dumps(
                    {
                        "invocationId": invocation_id,
                        "target": req["target"],
                        "data": {"phase": "end", "seq": 2, "status": "finished"},
                    }
                )
            )

        ctx = _WsServerContext(ws_handler)
        ws_url = ctx.start()
        try:
            client = self._make_client(ws_url)

            handle = client.call_stream(
                target="wuying_codespace",
                data={"method": "run_code", "mode": "stream"},
                on_event=None,
                on_end=None,
                on_error=None,
            )

            end_data = handle.wait_end()
            assert end_data["status"] == "finished"
            client.close()
        finally:
            ctx.stop()
