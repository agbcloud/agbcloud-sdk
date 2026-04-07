/**
 * WebSocket client for AGB SDK.
 *
 * Provides session-scoped WebSocket communication with message routing
 * by invocationId, streaming calls, push message callbacks, automatic
 * reconnection, and heartbeat support.
 *
 * TypeScript uses native async/await, so there is no need for a separate
 * sync wrapper layer (unlike the Python implementation).
 */

import { randomUUID } from "crypto";
import WebSocket, { ErrorEvent, CloseEvent, MessageEvent } from "ws";
import {
    WsProtocolError,
    WsHandshakeRejectedError,
    WsConnectionClosedError,
    WsRemoteError,
    WsCancelledError,
} from "./exceptions";
import {
    WsConnectionState,
    type OnEvent,
    type OnEnd,
    type OnError,
    type PushCallback,
    type ConnectionStateListener,
    type PendingStream,
} from "./models";
import {
    logDebug,
    logInfo,
    logWarn,
    logError,
} from "../../logger";

function newInvocationId(): string {
    return randomUUID().replace(/-/g, "");
}

function jsonDumps(obj: unknown): string {
    return JSON.stringify(obj);
}

function truncateForLog(text: string, maxLength: number = 1200): string {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + "...";
}

function maskSensitiveData(text: string): string {
     // Mask common sensitive fields like token, password, accessToken, etc.
    return text.replace(/"(token|password|accessToken|secret)":\s*"[^"]*"/gi,
        (match) => {
            const key = match.split(":")[0];
            return `${key}:"***"`;
        }
    );
}

function extractInvocationId(msg: Record<string, unknown>): string {
     const invocationId = (msg["invocationId"] || msg["requestId"]) as string | undefined;
    if (typeof invocationId !== "string" || !invocationId) {
        const rawId = msg["invocationId"] ?? msg["requestId"];
        throw new WsProtocolError(
            `invocationId is required and must be a non-empty string, got: ${typeof rawId}=${JSON.stringify(rawId)}`
        );
    }
    return invocationId;
}

/**
 * Handle for an active WebSocket stream.
 *
 * Provides methods to write data, cancel the stream, and wait for completion.
 */
export class WsStreamHandle {
    private readonly _client: WsClient;
    private readonly _pending: PendingStream;

    constructor(client: WsClient, pending: PendingStream) {
        this._client = client;
        this._pending = pending;
    }

    get invocationId(): string {
        return this._pending.invocationId;
    }

    /**
     * Write additional data to the stream.
     */
    async write(data: Record<string, unknown>): Promise<void> {
        await this._client._writeBusiness(
            this._pending.invocationId,
            this._pending.target,
            data
        );
    }

    /**
     * Cancel the stream.
     */
    cancel(): void {
        this._client._cancelPending(this._pending.invocationId);
    }

    /**
     * Wait for the stream to complete and return the final response data.
     */
    waitEnd(): Promise<Record<string, unknown>> {
        if (this._pending.settled) {
            return Promise.reject(new WsConnectionClosedError("Stream already settled"));
        }
        return new Promise((resolve, reject) => {
            const originalResolve = this._pending.resolve;
            const originalReject = this._pending.reject;
            this._pending.resolve = (data) => {
                originalResolve(data);
                resolve(data);
            };
            this._pending.reject = (err) => {
                originalReject(err);
                reject(err);
            };
        });
    }
}

/**
 * Session-scoped WebSocket client with message routing by invocationId.
 *
 * Features:
 * - Automatic reconnection with exponential backoff
 * - Message routing by invocation ID
 * - Stream-based communication
 * - Push message callbacks
 * - Heartbeat / ping-pong
 */
export class WsClient {
    private readonly _wsUrl: string;
    private readonly _wsToken: string;
    private readonly _heartbeatIntervalMs: number;
    private readonly _reconnectInitialDelayMs: number;
    private readonly _reconnectMaxDelayMs: number;

    private _ws: WebSocket | null = null;
    private _heartbeatTimer: ReturnType<typeof setInterval> | null = null;
    private _reconnectTimer: ReturnType<typeof setTimeout> | null = null;

    private readonly _pendingById: Map<string, PendingStream> = new Map();
    private readonly _stateListeners: ConnectionStateListener[] = [];
    private readonly _callbacksByTarget: Map<string, PushCallback[]> = new Map();
    private _state: WsConnectionState = WsConnectionState.CLOSED;
    private _closedExplicitly = false;

    constructor(
        wsUrl: string,
        wsToken: string,
        options: {
            heartbeatIntervalMs?: number;
            reconnectInitialDelayMs?: number;
            reconnectMaxDelayMs?: number;
        } = {}
    ) {
        this._wsUrl = wsUrl;
        this._wsToken = wsToken;
        this._heartbeatIntervalMs = options.heartbeatIntervalMs ?? 20_000;
        this._reconnectInitialDelayMs = options.reconnectInitialDelayMs ?? 500;
        this._reconnectMaxDelayMs = options.reconnectMaxDelayMs ?? 5_000;
    }

    onConnectionStateChange(listener: ConnectionStateListener): void {
        this._stateListeners.push(listener);
    }

    /**
     * Establish WebSocket connection.
     */
    async connect(): Promise<void> {
        await this._ensureOpen();
    }

    /**
     * Register a push callback routed by target.
     *
     * @returns Unsubscribe function
     */
    registerCallback(target: string, callback: PushCallback): () => void {
        if (!target) throw new Error("target must be a non-empty string");
        if (typeof callback !== "function") throw new Error("callback must be a function");

        const callbacks = this._callbacksByTarget.get(target) ?? [];
        callbacks.push(callback);
        this._callbacksByTarget.set(target, callbacks);

        return () => this.unregisterCallback(target, callback);
    }

    /**
     * Unregister a previously registered callback.
     * If callback is omitted, all callbacks for the target are removed.
     */
    unregisterCallback(target: string, callback?: PushCallback): void {
        if (!target) throw new Error("target must be a non-empty string");

        if (callback === undefined) {
            this._callbacksByTarget.delete(target);
            return;
        }

        const callbacks = this._callbacksByTarget.get(target);
        if (!callbacks) return;

        const filtered = callbacks.filter((cb) => cb !== callback);
        if (filtered.length === 0) {
            this._callbacksByTarget.delete(target);
        } else {
            this._callbacksByTarget.set(target, filtered);
        }
    }

    /**
     * Close the WebSocket connection.
     */
    async close(): Promise<void> {
        this._closedExplicitly = true;

        if (this._reconnectTimer !== null) {
            clearTimeout(this._reconnectTimer);
            this._reconnectTimer = null;
        }

        this._closeTransport("explicit close");
    }

    /**
     * Initiate a streaming call.
     *
     * @returns WsStreamHandle for the stream
     */
    async callStream(options: {
        target: string;
        data: Record<string, unknown>;
        onEvent?: OnEvent;
        onEnd?: OnEnd;
        onError?: OnError;
    }): Promise<WsStreamHandle> {
        const { target, data, onEvent, onEnd, onError } = options;

        if (!target) throw new Error("target must be a non-empty string");
        if (typeof data !== "object" || data === null) throw new Error("data must be an object");

        await this._ensureOpen();

        const invocationId = newInvocationId();

        let resolveFn!: (data: Record<string, unknown>) => void;
        let rejectFn!: (err: Error) => void;

        const endPromise = new Promise<Record<string, unknown>>((resolve, reject) => {
            resolveFn = resolve;
            rejectFn = reject;
        });

        const pending: PendingStream = {
            invocationId,
            target,
            onEvent,
            onEnd,
            onError,
            resolve: resolveFn,
            reject: rejectFn,
            settled: false,
        };

        this._pendingById.set(invocationId, pending);

        try {
            await this._writeBusiness(invocationId, target, data);
        } catch (err) {
            this._pendingById.delete(invocationId);
            const error = err instanceof Error ? err : new Error(String(err));
            pending.settled = true;
            rejectFn(error);
            if (onError) onError(invocationId, error);
            throw error;
        }

        const handle = new WsStreamHandle(this, pending);

        // Attach the end promise to the handle
        (handle as unknown as { _endPromise: Promise<Record<string, unknown>> })._endPromise = endPromise;

        // Override waitEnd to use the original promise
        handle.waitEnd = () => endPromise;

        return handle;
    }

    /**
     * Send a one-way message (fire and forget).
     */
    async sendMessage(options: {
        target: string;
        data: Record<string, unknown>;
    }): Promise<void> {
        const { target, data } = options;
        await this._ensureOpen();

        try {
            const invocationId = newInvocationId();
            await this._writeBusiness(invocationId, target, data);
        } catch (err) {
            logWarn(`[WsClient] Failed to send message: ${err}`);
        }
    }

    // ─── Internal methods ────────────────────────────────────────────────────

    private _setState(state: WsConnectionState, reason: string): void {
        this._state = state;
        for (const listener of this._stateListeners) {
            try {
                listener(state, reason);
            } catch {
                // Ignore listener errors
            }
        }
    }

    private _logFrame(direction: string, payload: unknown): void {
        try {
            const raw = jsonDumps(payload);
            const masked = maskSensitiveData(raw);
            const truncated = truncateForLog(masked, 1200);
            logDebug(`[WsClient] WS ${direction} ${truncated}`);
        }  catch (err) {
            // Fallback to simple logging when JSON.stringify fails
            const fallback = payload instanceof Error ? payload.message : String(payload);
            logDebug(`[WsClient] WS ${direction} [log error: ${fallback}]`);
        }
    }

    private async _ensureOpen(): Promise<void> {
        if (this._ws !== null && this._ws.readyState === WebSocket.OPEN) {
            return;
        }
        await this._open();
    }

    private _open(): Promise<void> {
        if (this._closedExplicitly) {
            return Promise.reject(new WsConnectionClosedError("WS client is closed"));
        }

        this._setState(WsConnectionState.RECONNECTING, "connecting");
        // Remove token from URL for logging
        const safeUrl = this._wsUrl.replace(/[?&]token=[^&]*/g, "");
        logInfo(`[WsClient] WS CONNECTING url=${safeUrl}`);

        return new Promise((resolve, reject) => {
            // Use 'ws' library which supports custom headers (unlike native WebSocket)
            const headers: Record<string, string> = {
                "X-Access-Token": this._wsToken,
            };

            const ws = new WebSocket(this._wsUrl, { headers });

            ws.onopen = () => {
                this._ws = ws;
                this._setState(WsConnectionState.OPEN, "connected");
                logInfo(`[WsClient] WS CONNECTED url=${this._wsUrl}`);
                this._startHeartbeat();
                resolve();
            };

            ws.onerror = (event: ErrorEvent) => {
                // Handle both browser ErrorEvent and Node.js Event types
                const errorEvent = event as { message?: string; error?: Error };
                const errMsg = errorEvent.message
                    ?? (errorEvent.error instanceof Error ? errorEvent.error.message : undefined)
                    ?? `WebSocket error: ${JSON.stringify(event)}`;
                reject(new WsHandshakeRejectedError(errMsg));
            };

            ws.onclose = (event: CloseEvent) => {
                if (this._ws === ws) {
                    this._onTransportError(`connection closed: code=${event.code}`);
                }
            };

            ws.onmessage = (event: MessageEvent) => {
                try {
                    this._handleIncoming(event.data as string);
                } catch (err) {
                    if (err instanceof WsProtocolError) {
                        const rawStr = truncateForLog(
                            maskSensitiveData(String(event.data)),
                            2000
                        );
                        logWarn(
                            `[WsClient] WS protocol error (ignored): ${err.message}; raw=${rawStr}`
                        );
                        // Try to notify pending stream if we can extract invocationId
                        try {
                            const msg = JSON.parse(event.data as string) as Record<string, unknown>;
                            if (typeof msg === "object" && msg !== null) {
                                let invocationId: string | undefined;
                                try {
                                    invocationId = extractInvocationId(msg);
                                } catch {
                                    invocationId = undefined;
                                }
                                if (invocationId) {
                                    const pending = this._pendingById.get(invocationId);
                                    if (pending && !pending.settled) {
                                        pending.settled = true;
                                        this._pendingById.delete(invocationId);
                                        if (pending.onError) pending.onError(invocationId, err);
                                        pending.reject(err);
                                    }
                                }
                            }
                        } catch {
                            // Ignore parse errors
                        }
                    }
                }
            };
        });
    }

    private _closeTransport(reason: string): void {
        const ws = this._ws;
        this._ws = null;

        if (this._heartbeatTimer !== null) {
            clearInterval(this._heartbeatTimer);
            this._heartbeatTimer = null;
        }

        if (ws !== null) {
            try {
                ws.close();
            } catch {
                // Ignore close errors
            }
        }

        logInfo(`[WsClient] WS CLOSED reason=${reason}`);
        this._setState(WsConnectionState.CLOSED, reason);
    }

    private _startHeartbeat(): void {
        if (this._heartbeatTimer !== null) {
            clearInterval(this._heartbeatTimer);
        }

        this._heartbeatTimer = setInterval(() => {
            const ws = this._ws;
            if (ws === null || ws.readyState !== WebSocket.OPEN) {
                return;
            }
            // Send a ping frame via a lightweight JSON message
            try {
                ws.send(jsonDumps({ type: "ping" }));
            } catch (err) {
                this._onTransportError(`heartbeat failed: ${err}`);
            }
        }, this._heartbeatIntervalMs);
    }

    private _handleIncoming(raw: string): void {
        let msg: Record<string, unknown>;
        try {
            msg = JSON.parse(raw) as Record<string, unknown>;
        } catch (err) {
            throw new WsProtocolError(`Invalid JSON message: ${err}`);
        }

        if (typeof msg !== "object" || msg === null) {
            throw new WsProtocolError("Message must be a JSON object");
        }

        const invocationId = extractInvocationId(msg);
        const source = msg["source"] as string | undefined;
        const target = msg["target"] as string | undefined;
        const dataAny = msg["data"];

        // Parse data field
        let data: Record<string, unknown>;
        if (typeof dataAny === "object" && dataAny !== null) {
            data = dataAny as Record<string, unknown>;
        } else if (typeof dataAny === "string") {
            try {
                const parsed = JSON.parse(dataAny) as unknown;
                if (typeof parsed !== "object" || parsed === null) {
                    throw new WsProtocolError(
                        "data is a string but decoded JSON is not an object"
                    );
                }
                data = parsed as Record<string, unknown>;
                logWarn(
                    "[WsClient] WS protocol violation: backend sent data as string; decoded to object"
                );
            } catch (err) {
                if (err instanceof WsProtocolError) throw err;
                throw new WsProtocolError(`data is a string but not valid JSON: ${err}`);
            }
        } else {
            throw new WsProtocolError("data is required and must be an object");
        }

        this._logFrame("<<", { invocationId, source, target, data });

        const pending = this._pendingById.get(invocationId);

        if (pending === undefined) {
            this._handlePushMessage(invocationId, source, target, data);
            return;
        }

        this._handleStreamMessage(invocationId, pending, data);
    }

    private _handlePushMessage(
        invocationId: string,
        source: string | undefined,
        target: string | undefined,
        data: Record<string, unknown>
    ): void {
        if (!target) {
            logDebug(`[WsClient] Dropping message with no target: ${invocationId}`);
            return;
        }

        let routeTarget = target;
        if (routeTarget === "SDK" && source && source !== "SDK") {
            routeTarget = source;
        }

        const callbacks = this._callbacksByTarget.get(routeTarget) ?? [];
        if (callbacks.length === 0) {
            logDebug(
                `[WsClient] Dropping push message with no callback: requestId=${invocationId}, target=${routeTarget}`
            );
            return;
        }

        const payload: Record<string, unknown> = {
            requestId: invocationId,
            target: routeTarget,
            data,
        };

        for (const cb of callbacks) {
            try {
                const result = cb(payload);
                if (result instanceof Promise) {
                    result.catch((err) => {
                        logError(`[WsClient] Push callback failed: ${err}`);
                    });
                }
            } catch (err) {
                logError(`[WsClient] Push callback failed: ${err}`);
            }
        }
    }

    private _handleStreamMessage(
        invocationId: string,
        pending: PendingStream,
        data: Record<string, unknown>
    ): void {
        // Check for explicit error
        const phase = data["phase"] as string | undefined;

        // Check for explicit error field or error phase
        const hasExplicitError = typeof data["error"] === "string" && data["error"];
        if (hasExplicitError || phase === "error") {
            const err = new WsRemoteError(
                truncateForLog(maskSensitiveData(JSON.stringify(data)), 2000)
            );
            if (!pending.settled) {
                pending.settled = true;
                this._pendingById.delete(invocationId);
                if (pending.onError) pending.onError(invocationId, err);
                pending.reject(err);
            }
            return;
        }

        if (phase === "event") {
            if (pending.onEvent) pending.onEvent(invocationId, data);
            return;
        }

        if (phase === "end") {
            if (pending.onEnd) pending.onEnd(invocationId, data);
            if (!pending.settled) {
                pending.settled = true;
                this._pendingById.delete(invocationId);
                pending.resolve(data);
            }
            return;
        }

        // Unknown or missing phase
        const err =
            phase === undefined
                ? new WsProtocolError(
                      `WS message missing required data.phase; invocationId=${invocationId}, data=${truncateForLog(maskSensitiveData(JSON.stringify(data)), 2000)}`
                  )
                : new WsProtocolError(
                      `WS message has unsupported data.phase; invocationId=${invocationId}, phase=${JSON.stringify(phase)}, data=${truncateForLog(maskSensitiveData(JSON.stringify(data)), 2000)}`
                  );

        if (!pending.settled) {
            pending.settled = true;
            this._pendingById.delete(invocationId);
            if (pending.onError) pending.onError(invocationId, err);
            pending.reject(err);
        }
    }

    private _onTransportError(reason: string): void {
        if (this._closedExplicitly) {
            this._closeTransport(reason);
            return;
        }

        logWarn(`[WsClient] WS transport error: ${reason}`);
        this._closeTransport(reason);
        this._failAllPending(new WsConnectionClosedError(reason));

        if (this._reconnectTimer === null) {
            this._scheduleReconnect(this._reconnectInitialDelayMs);
        }
    }

    private _failAllPending(err: Error): void {
        const items = Array.from(this._pendingById.entries());
        this._pendingById.clear();

        for (const [invocationId, pending] of items) {
            if (!pending.settled) {
                pending.settled = true;
                if (pending.onError) {
                    try {
                        pending.onError(invocationId, err);
                    } catch {
                        // Ignore callback errors
                    }
                }
                pending.reject(err);
            }
        }
    }

    private _scheduleReconnect(delayMs: number): void {
        this._reconnectTimer = setTimeout(async () => {
            this._reconnectTimer = null;

            if (this._closedExplicitly) return;
            if (this._ws !== null && this._ws.readyState === WebSocket.OPEN) return;

            try {
                await this._open();
            } catch (err) {
                this._setState(
                    WsConnectionState.RECONNECTING,
                    `reconnect failed: ${err}`
                );
                const nextDelay = Math.min(
                    delayMs * 1.5 + Math.random() * 100,
                    this._reconnectMaxDelayMs
                );
                this._scheduleReconnect(nextDelay);
            }
        }, delayMs + Math.random() * 100);
    }

    /** @internal */
    async _writeBusiness(
        invocationId: string,
        target: string,
        data: Record<string, unknown>
    ): Promise<void> {
        const ws = this._ws;
        if (ws === null || ws.readyState !== WebSocket.OPEN) {
            throw new WsConnectionClosedError("WS is not connected");
        }

        const payload = {
            invocationId,
            source: "SDK",
            target,
            data,
        };

        this._logFrame(">>", payload);
        ws.send(jsonDumps(payload));
    }

    /** @internal */
    _cancelPending(invocationId: string): void {
        const pending = this._pendingById.get(invocationId);
        if (!pending || pending.settled) return;

        pending.settled = true;
        this._pendingById.delete(invocationId);

        const err = new WsCancelledError(
            `Stream ${invocationId} was cancelled by caller`
        );

        if (pending.onError) {
            try {
                pending.onError(invocationId, err);
            } catch {
                // Ignore callback errors
            }
        }

        pending.reject(err);
    }
}
