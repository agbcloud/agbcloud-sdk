/** WebSocket connection state. */
export enum WsConnectionState {
    OPEN = "OPEN",
    CLOSED = "CLOSED",
    RECONNECTING = "RECONNECTING",
    ERROR = "ERROR",
}
/** Callback for handling streaming event messages during a WebSocket call. */
export type OnEvent = (invocationId: string, data: Record<string, unknown>) => void;
/** Callback for handling the final end message when a WebSocket stream completes. */
export type OnEnd = (invocationId: string, data: Record<string, unknown>) => void;
/** Callback for handling errors that occur during a WebSocket call. */
export type OnError = (invocationId: string, err: Error) => void;
/** Callback for handling push messages from the server. */
export type PushCallback = (payload: Record<string, unknown>) => void | Promise<void>;
/** Callback for handling changes in the WebSocket connection state. */
export type ConnectionStateListener = (state: WsConnectionState, reason: string) => void;

/** Tracks a pending streaming call. */
export interface PendingStream {
    invocationId: string;
    target: string;
    onEvent: OnEvent | undefined;
    onEnd: OnEnd | undefined;
    onError: OnError | undefined;
    resolve: (data: Record<string, unknown>) => void;
    reject: (err: Error) => void;
    settled: boolean;
}
