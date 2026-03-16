import type { Session } from "../session";

/* ------------------------------------------------------------------ */
/*  Base                                                               */
/* ------------------------------------------------------------------ */

export interface ApiResponse {
    requestId?: string;
}

/* ------------------------------------------------------------------ */
/*  Session                                                            */
/* ------------------------------------------------------------------ */

export interface SessionResult extends ApiResponse {
    success: boolean;
    errorMessage?: string;
    /** When success is false (e.g. session not found or deleted), session is explicitly null. */
    session?: Session | null;
}

export interface GetSessionData {
    appInstanceId: string;
    resourceId: string;
    sessionId: string;
    success: boolean;
    resourceUrl: string;
    status: string;
}

export interface GetSessionResult extends ApiResponse {
    httpStatusCode: number;
    code: string;
    success: boolean;
    data?: GetSessionData;
    errorMessage?: string;
}

export interface SessionListResult extends ApiResponse {
    success: boolean;
    errorMessage?: string;
    sessionIds: string[];
    nextToken: string;
    maxResults: number;
    totalCount: number;
}

export interface SessionStatusResult extends ApiResponse {
    httpStatusCode: number;
    code: string;
    success: boolean;
    status: string;
    errorMessage?: string;
}

export interface SessionMetrics {
    cpuCount: number;
    cpuUsedPct: number;
    diskTotal: number;
    diskUsed: number;
    memTotal: number;
    memUsed: number;
    rxRateKbytePerS: number;
    txRateKbytePerS: number;
    rxUsedKbyte: number;
    txUsedKbyte: number;
    timestamp: string;
}

export interface SessionMetricsResult extends ApiResponse {
    success: boolean;
    metrics?: SessionMetrics;
    errorMessage?: string;
    raw?: Record<string, unknown>;
}

/* ------------------------------------------------------------------ */
/*  Generic operations                                                 */
/* ------------------------------------------------------------------ */

export interface DeleteResult extends ApiResponse {
    success: boolean;
    errorMessage?: string;
}

export interface OperationResult extends ApiResponse {
    success: boolean;
    data?: unknown;
    errorMessage?: string;
}

export interface BoolResult extends ApiResponse {
    success: boolean;
    data?: boolean;
    errorMessage?: string;
}

/* ------------------------------------------------------------------ */
/*  MCP Tools                                                          */
/* ------------------------------------------------------------------ */

export interface McpTool {
    name: string;
    description: string;
    inputSchema: Record<string, unknown>;
    server: string;
    tool: string;
}

export interface McpToolResult extends ApiResponse {
    success: boolean;
    data?: string;
    errorMessage?: string;
}

export interface McpToolsResult extends ApiResponse {
    success: boolean;
    tools: McpTool[];
    errorMessage?: string;
}

/* ------------------------------------------------------------------ */
/*  Command                                                            */
/* ------------------------------------------------------------------ */

export interface CommandResult extends ApiResponse {
    success: boolean;
    output: string;
    exitCode: number;
    stdout: string;
    stderr: string;
    traceId: string;
    errorMessage?: string;
}

/* ------------------------------------------------------------------ */
/*  Code Execution                                                     */
/* ------------------------------------------------------------------ */

export interface ExecutionResult {
    text?: string;
    html?: string;
    markdown?: string;
    png?: string;
    jpeg?: string;
    svg?: string;
    json?: unknown;
    latex?: string;
    chart?: unknown;
    isMainResult: boolean;
}

export interface ExecutionLogs {
    stdout: string[];
    stderr: string[];
}

export interface EnhancedCodeExecutionResult extends ApiResponse {
    executionCount?: number;
    executionTime: number;
    logs: ExecutionLogs;
    results: ExecutionResult[];
    errorMessage: string;
    success: boolean;
}

/* ------------------------------------------------------------------ */
/*  FileSystem                                                         */
/* ------------------------------------------------------------------ */

export interface FileContentResult extends ApiResponse {
    success: boolean;
    content: string;
    errorMessage?: string;
}

export interface BinaryFileContentResult extends ApiResponse {
    success: boolean;
    content: Buffer;
    errorMessage?: string;
    size?: number;
}

export interface MultipleFileContentResult extends ApiResponse {
    success: boolean;
    files: Record<string, string>;
    errorMessage?: string;
}

export interface FileInfo {
    name: string;
    path: string;
    size: number;
    isDirectory: boolean;
    modTime: string;
    mode: string;
    owner?: string;
    group?: string;
}

export interface FileInfoResult extends ApiResponse {
    success: boolean;
    fileInfo?: FileInfo;
    errorMessage?: string;
}

export interface DirectoryEntry {
    type: "file" | "directory";
    name: string;
}

export interface DirectoryListResult extends ApiResponse {
    success: boolean;
    entries: DirectoryEntry[];
    errorMessage?: string;
}

export interface FileSearchResult extends ApiResponse {
    success: boolean;
    matches?: string[];
    errorMessage?: string;
}

export interface FileChangeEvent {
    eventType: string;
    path: string;
    pathType: string;
}

export interface FileChangeResult extends ApiResponse {
    success: boolean;
    events: FileChangeEvent[];
    rawData?: string;
    errorMessage?: string;
}

export interface UploadResult {
    success: boolean;
    requestIdUploadUrl?: string;
    requestIdSync?: string;
    httpStatus?: number;
    etag?: string;
    bytesSent: number;
    path: string;
    errorMessage?: string;
}

export interface DownloadResult {
    success: boolean;
    requestIdDownloadUrl?: string;
    requestIdSync?: string;
    httpStatus?: number;
    bytesReceived: number;
    path: string;
    localPath: string;
    errorMessage?: string;
}

/* ------------------------------------------------------------------ */
/*  Computer                                                           */
/* ------------------------------------------------------------------ */

export interface CursorPosition extends ApiResponse {
    success: boolean;
    errorMessage?: string;
    x: number;
    y: number;
}

export interface ScreenSize extends ApiResponse {
    success: boolean;
    errorMessage?: string;
    width: number;
    height: number;
    dpiScalingFactor: number;
}

export interface WindowInfo {
    id?: string;
    window_id?: number;
    title?: string;
    x?: number;
    y?: number;
    width?: number;
    height?: number;
    [key: string]: unknown;
}

export interface WindowInfoResult extends ApiResponse {
    success: boolean;
    window?: WindowInfo;
    errorMessage?: string;
}

export interface WindowListResult extends ApiResponse {
    success: boolean;
    windows: WindowInfo[];
    errorMessage?: string;
}

export interface AppOperationResult extends ApiResponse {
    success: boolean;
    errorMessage?: string;
}

export interface ProcessInfo {
    pid?: number;
    name?: string;
    [key: string]: unknown;
}

export interface ProcessListResult extends ApiResponse {
    success: boolean;
    data: ProcessInfo[];
    errorMessage?: string;
}

export interface InstalledAppInfo {
    name?: string;
    [key: string]: unknown;
}

export interface InstalledAppListResult extends ApiResponse {
    success: boolean;
    data: InstalledAppInfo[];
    errorMessage?: string;
}

/* ------------------------------------------------------------------ */
/*  Context                                                            */
/* ------------------------------------------------------------------ */

export interface ContextData {
    id: string;
    name: string;
    createdAt?: string;
    lastUsedAt?: string;
}

export interface ContextResult extends ApiResponse {
    success: boolean;
    context?: ContextData;
    errorMessage?: string;
}

export interface ContextListResult extends ApiResponse {
    success: boolean;
    contexts: ContextData[];
    errorMessage?: string;
}

export interface ClearContextResult extends ApiResponse {
    success: boolean;
    state?: string;
    errorMessage?: string;
}

export interface FileUrlResult extends ApiResponse {
    success: boolean;
    url?: string;
    errorMessage?: string;
}

export interface ContextFileEntry {
    fileId?: string;
    name: string;
    path: string;
    type: string;
    createdTime?: string;
    modifiedTime?: string;
    size?: number;
    status?: string;
}

export interface ContextFileListResult extends ApiResponse {
    success: boolean;
    files: ContextFileEntry[];
    count?: number;
    errorMessage?: string;
}

export interface ContextStatusData {
    contextId: string;
    path: string;
    errorMessage?: string;
    status: string;
    startTime?: string;
    finishTime?: string;
    taskType?: string;
}

export interface ContextInfoResult extends ApiResponse {
    success: boolean;
    items: ContextStatusData[];
    errorMessage?: string;
}

export interface ContextSyncResult extends ApiResponse {
    success: boolean;
    errorMessage?: string;
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

export function extractRequestId(
    response: Record<string, unknown>,
): string | undefined {
    return (response?.requestId as string) ?? undefined;
}
