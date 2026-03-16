import type { Client } from "./api/client";
import { BaseService } from "./api/base-service";
import { Command } from "./modules/command";
import { Code } from "./modules/code";
import { FileSystem } from "./modules/filesystem";
import { Browser } from "./modules/browser/browser";
import { Computer } from "./modules/computer/computer";
import { ContextManager } from "./context-manager";
import {
    SetLabelRequest,
    GetLabelRequest,
    GetMcpResourceRequest,
    GetLinkRequest,
    DeleteSessionAsyncRequest,
    GetSessionDetailRequest,
    ListMcpToolsRequest,
    RefreshSessionIdleTimeRequest,
} from "./api/models";
import type {
    OperationResult,
    DeleteResult,
    SessionStatusResult,
    McpToolResult,
    McpToolsResult,
    McpTool,
    SessionMetricsResult,
    SessionMetrics,
} from "./types/api-response";
import { logInfo, logOperationError } from "./logger";

/**
 * Minimal AGB client interface used by Session for API calls.
 */
export interface AGB {
    apiKey: string;
    client: Client;
}

/**
 * Represents an active session in the AGB cloud environment.
 * Provides access to command, file system, code execution, browser, computer, and context modules.
 */
export class Session {
    private _agb: AGB;
    private _sessionId: string;

    resourceUrl: string = "";
    imageId: string = "";
    appInstanceId: string = "";
    resourceId: string = "";
    enableBrowserReplay: boolean = false;

    /** Execute shell commands in the session. */
    command!: Command;
    /** File system operations (read, write, list, etc.). */
    file!: FileSystem;
    /** Execute code in the session (e.g. Python, JavaScript). */
    code!: Code;
    /** Browser automation (navigate, click, screenshot, etc.). */
    browser!: Browser;
    /** Desktop automation (mouse, keyboard, screen, windows). */
    computer!: Computer;
    /** Context management and synchronization. */
    context!: ContextManager;

    /**
     * Create a Session instance.
     *
     * @param agb - The AGB client that owns this session
     * @param sessionId - The session ID from the cloud
     */
    constructor(agb: AGB, sessionId: string) {
        this._agb = agb;
        this._sessionId = sessionId;
        this._initModules();
    }

    private _baseService!: BaseService;

    private _initModules(): void {
        this.command = new Command(this);
        this.file = new FileSystem(this);
        this.code = new Code(this);
        this.browser = new Browser(this);
        this.computer = new Computer(this);
        this.context = new ContextManager(this);
        // Internal base service for shared MCP tool call logic
        this._baseService = new BaseService(this);
    }

    /** @internal */
    getApiKey(): string {
        return this._agb.apiKey;
    }

    /**
     * Get the session ID.
     *
     * @returns The session ID string
     */
    getSessionId(): string {
        return this._sessionId;
    }

    /** @internal */
    getClient(): Client {
        return this._agb.client;
    }

    /** @internal */
    getAgb(): AGB {
        return this._agb;
    }

    /**
     * Serialize session to a plain object (sessionId, resourceUrl, imageId, etc.).
     *
     * @returns Plain object with session fields
     */
    toJSON(): Record<string, unknown> {
        return {
            sessionId: this._sessionId,
            resourceUrl: this.resourceUrl,
            imageId: this.imageId,
            appInstanceId: this.appInstanceId,
            resourceId: this.resourceId,
        };
    }

    private _validateLabels(
        labels: Record<string, string>
    ): OperationResult | null {
        if (labels == null) {
            return {
                success: false,
                errorMessage:
                    "Labels cannot be null, undefined, or invalid type. Please provide a valid labels object.",
            };
        }
        if (Array.isArray(labels)) {
            return {
                success: false,
                errorMessage:
                    "Labels cannot be an array. Please provide a valid labels object.",
            };
        }
        if (typeof labels !== "object") {
            return {
                success: false,
                errorMessage:
                    "Labels cannot be null, undefined, or invalid type. Please provide a valid labels object.",
            };
        }
        if (Object.keys(labels).length === 0) {
            return {
                success: false,
                errorMessage:
                    "Labels cannot be empty. Please provide at least one label.",
            };
        }
        for (const [key, value] of Object.entries(labels)) {
            if (!key || (typeof key === "string" && key.trim() === "")) {
                return {
                    success: false,
                    errorMessage:
                        "Label keys cannot be empty. Please provide valid keys.",
                };
            }
            if (value == null || (typeof value === "string" && value.trim() === "")) {
                return {
                    success: false,
                    errorMessage:
                        "Label values cannot be empty. Please provide valid values.",
                };
            }
        }
        return null;
    }

    /**
     * Set labels on the session (key-value metadata).
     *
     * @param labels - Non-empty object of string key-value pairs
     * @returns Promise resolving to OperationResult
     */
    async setLabels(labels: Record<string, string>): Promise<OperationResult> {
        const validationResult = this._validateLabels(labels);
        if (validationResult) {
            return validationResult;
        }

        const request = new SetLabelRequest(
            `Bearer ${this.getApiKey()}`,
            this._sessionId,
            JSON.stringify(labels)
        );

        const response = await this.getClient().setLabel(request);

        if (response.isSuccessful()) {
            return {
                requestId: (response as { requestId?: string }).requestId ?? "",
                success: true,
            };
        }

        return {
            requestId: (response as { requestId?: string }).requestId ?? "",
            success: false,
            errorMessage: response.getErrorMessage(),
        };
    }

    /**
     * Get labels for the session.
     *
     * @returns Promise resolving to OperationResult with data containing labels object
     */
    async getLabels(): Promise<OperationResult> {
        const request = new GetLabelRequest(
            `Bearer ${this.getApiKey()}`,
            this._sessionId
        );

        const response = await this.getClient().getLabel(request);

        if (response.isSuccessful()) {
            const labelsData = response.getLabelsData() as { labels?: string } | undefined;
            let labels: Record<string, string> = {};

            if (labelsData?.labels) {
                try {
                    labels = JSON.parse(labelsData.labels) as Record<string, string>;
                } catch {
                    labels = {};
                }
            }

            return {
                requestId: (response as { requestId?: string }).requestId ?? "",
                success: true,
                data: labels,
            };
        }

        return {
            requestId: (response as { requestId?: string }).requestId ?? "",
            success: false,
            errorMessage: response.getErrorMessage(),
        };
    }

    /**
     * Get session resource info (sessionId, resourceUrl, desktopInfo, etc.).
     *
     * @returns Promise resolving to OperationResult with resource data
     */
    async info(): Promise<OperationResult> {
        const request = new GetMcpResourceRequest(
            this._sessionId,
            `Bearer ${this.getApiKey()}`
        );

        const response = await this.getClient().getMcpResource(request);

        if (response == null) {
            return {
                success: false,
                errorMessage: "OpenAPI client returned None response",
            };
        }

        const requestId = (response as { requestId?: string }).requestId ?? "";

        if (response.isSuccessful()) {
            const resourceData = response.getResourceData();
            if (resourceData) {
                const resultData: Record<string, unknown> = {
                    sessionId: resourceData.sessionId,
                    resourceUrl: resourceData.resourceUrl,
                };

                if (resourceData.desktopInfo) {
                    const desktopInfo = resourceData.desktopInfo as Record<string, unknown>;
                    resultData.appId = desktopInfo.appId;
                    resultData.authCode = desktopInfo.authCode;
                    resultData.connectionProperties = desktopInfo.connectionProperties;
                    resultData.resourceId = desktopInfo.resourceId;
                    resultData.resourceType = desktopInfo.resourceType;
                    resultData.ticket = desktopInfo.ticket;
                }

                return {
                    requestId,
                    success: true,
                    data: resultData,
                };
            }

            return {
                requestId,
                success: false,
                errorMessage: "No resource data found in response",
            };
        }

        return {
            requestId,
            success: false,
            errorMessage:
                response.getErrorMessage() ?? "Failed to get MCP resource",
        };
    }

    async getLink(
        protocolType?: string,
        port?: number
    ): Promise<OperationResult> {
        const request = new GetLinkRequest(
            `Bearer ${this.getApiKey()}`,
            port,
            protocolType,
            this._sessionId
        );

        const response = await this.getClient().getLink(request);

        if (response.isSuccessful()) {
            const url = response.getUrl();
            const requestId = (response as { requestId?: string }).requestId ?? "";

            if (url) {
                return {
                    requestId,
                    success: true,
                    data: url,
                };
            }

            return {
                requestId,
                success: false,
                errorMessage: "No URL found in response",
            };
        }

        return {
            requestId: (response as { requestId?: string }).requestId ?? "",
            success: false,
            errorMessage: response.getErrorMessage() ?? "Failed to get link",
        };
    }

    /**
     * Release (delete) this session. Optionally sync context before releasing.
     *
     * @param syncContext - If true, sync context (e.g. upload browser data) before releasing
     * @returns Promise resolving to DeleteResult
     */
    async delete(syncContext: boolean = false): Promise<DeleteResult> {
        if (syncContext) {
            await this.context.sync();
        }

        const request = new DeleteSessionAsyncRequest(
            `Bearer ${this.getApiKey()}`,
            this._sessionId
        );

        const response = await this.getClient().deleteSessionAsync(request);

        const requestId =
            (response as { requestId?: string }).requestId ??
            (response as { body?: { requestId?: string } }).body?.requestId ??
            "";

        if (!response.isSuccessful()) {
            const body = response as { body?: { code?: string; message?: string } };
            const errorMessage = `[${body.body?.code ?? "Unknown"}] ${body.body?.message ?? "Failed to delete session"
                }`;
            return {
                requestId,
                success: false,
                errorMessage,
            };
        }

        const pollTimeout = 300000;
        const pollInterval = 1000;
        const pollStartTime = Date.now();

        while (true) {
            const elapsed = Date.now() - pollStartTime;
            if (elapsed >= pollTimeout) {
                return {
                    requestId,
                    success: false,
                    errorMessage: `Timeout waiting for session deletion after ${pollTimeout / 1000}s`,
                };
            }

            const statusResult = await this.getStatus();

            if (!statusResult.success) {
                const errorCode = statusResult.code ?? "";
                const errorMessage = statusResult.errorMessage ?? "";
                const httpStatusCode = statusResult.httpStatusCode ?? 0;

                const isNotFound =
                    errorCode === "InvalidMcpSession.NotFound" ||
                    (httpStatusCode === 400 &&
                        (errorMessage.toLowerCase().includes("not found") ||
                            errorMessage.includes("NotFound") ||
                            errorCode.toLowerCase().includes("not found"))) ||
                    errorMessage.toLowerCase().includes("not found");

                if (isNotFound) {
                    return { requestId, success: true };
                }
            } else if (statusResult.status === "FINISH") {
                return { requestId, success: true };
            }

            await new Promise((resolve) => setTimeout(resolve, pollInterval));
        }
    }

    async getStatus(): Promise<SessionStatusResult> {
        const request = new GetSessionDetailRequest(
            `Bearer ${this.getApiKey()}`,
            this._sessionId
        );

        const response = await this.getClient().getSessionDetail(request);

        const requestId = (response as { requestId?: string }).requestId ?? "";
        const httpStatusCode =
            (response as { httpStatusCode?: number }).httpStatusCode ?? 0;
        const code = (response as { code?: string }).code ?? "";

        if (!response.isSuccessful()) {
            return {
                requestId,
                httpStatusCode,
                code,
                success: false,
                status: "",
                errorMessage: response.getErrorMessage() ?? "Unknown error",
            };
        }

        const status = response.getStatus();

        return {
            requestId,
            httpStatusCode,
            code,
            success: true,
            status,
        };
    }

    async keepAlive(): Promise<OperationResult> {
        const request = new RefreshSessionIdleTimeRequest(
            `Bearer ${this.getApiKey()}`,
            this._sessionId
        );

        const response = await this.getClient().refreshSessionIdleTime(request);

        const requestId = (response as { requestId?: string }).requestId ?? "";

        if (!response.isSuccessful()) {
            return {
                requestId,
                success: false,
                errorMessage: response.getErrorMessage() ?? "Unknown error",
            };
        }

        return {
            requestId,
            success: true,
        };
    }

    async callMcpTool(
        toolName: string,
        args: Record<string, unknown>,
        readTimeout?: number,
        connectTimeout?: number
    ): Promise<McpToolResult> {
        const result = await this._baseService.callMcpTool(
            toolName,
            args,
            readTimeout,
            connectTimeout
        );

        return {
            requestId: result.requestId,
            success: result.success,
            data: result.data as string | undefined,
            errorMessage: result.errorMessage,
        };
    }

    async listMcpTools(imageId?: string): Promise<McpToolsResult> {
        const imageIdStr = imageId ?? this.imageId;
        if (!imageIdStr) {
            throw new Error(
                "imageId is required. Provide it as a parameter or set it on the session.",
            );
        }

        const request = new ListMcpToolsRequest(
            imageIdStr,
            `Bearer ${this.getApiKey()}`
        );

        const response = await this.getClient().listMcpTools(request);

        const requestId = (response as { requestId?: string }).requestId ?? "";

        if (!response.isSuccessful()) {
            return {
                requestId,
                success: false,
                tools: [],
                errorMessage:
                    response.getErrorMessage() ?? "Failed to list MCP tools",
            };
        }

        const toolsDataStr = response.getToolsList();
        const tools: McpTool[] = [];

        if (toolsDataStr) {
            try {
                const toolsData = JSON.parse(toolsDataStr) as unknown;
                if (Array.isArray(toolsData)) {
                    for (const toolData of toolsData as Record<string, unknown>[]) {
                        tools.push({
                            name: (toolData.name as string) ?? "",
                            description: (toolData.description as string) ?? "",
                            inputSchema: (toolData.inputSchema as Record<string, unknown>) ?? {},
                            server: (toolData.server as string) ?? "",
                            tool: (toolData.tool as string) ?? "",
                        });
                    }
                }
            } catch (e) {
                return {
                    requestId,
                    success: false,
                    tools: [],
                    errorMessage: `Failed to parse tools list: ${e}`,
                };
            }
        }

        return {
            requestId,
            success: true,
            tools,
        };
    }

    async getMetrics(
        readTimeout?: number,
        connectTimeout?: number
    ): Promise<SessionMetricsResult> {
        const toolResult = await this.callMcpTool(
            "get_metrics",
            {},
            readTimeout,
            connectTimeout
        );

        if (!toolResult.success) {
            return {
                requestId: toolResult.requestId,
                success: false,
                metrics: undefined,
                errorMessage: toolResult.errorMessage ?? "Failed to get metrics",
                raw: {},
            };
        }

        try {
            const raw =
                typeof toolResult.data === "string"
                    ? (JSON.parse(toolResult.data) as Record<string, unknown>)
                    : (toolResult.data as unknown as Record<string, unknown> | undefined) ?? {};

            if (raw == null || typeof raw !== "object") {
                throw new Error("get_metrics returned non-object JSON");
            }

            const floatFromFirstKey = (
                data: Record<string, unknown>,
                keys: string[],
                defaultVal: number = 0
            ): number => {
                for (const k of keys) {
                    if (k in data && data[k] != null) {
                        try {
                            return parseFloat(String(data[k] ?? 0));
                        } catch {
                            /* ignore */
                        }
                    }
                }
                return defaultVal;
            };

            const metrics: SessionMetrics = {
                cpuCount: Number(raw.cpu_count ?? 0) || 0,
                cpuUsedPct: Number(raw.cpu_used_pct ?? 0) || 0,
                diskTotal: Number(raw.disk_total ?? 0) || 0,
                diskUsed: Number(raw.disk_used ?? 0) || 0,
                memTotal: Number(raw.mem_total ?? 0) || 0,
                memUsed: Number(raw.mem_used ?? 0) || 0,
                rxRateKbytePerS: floatFromFirstKey(raw, [
                    "rx_rate_kbyte_per_s",
                    "rx_rate_kbps",
                    "rx_rate_KBps",
                ]),
                txRateKbytePerS: floatFromFirstKey(raw, [
                    "tx_rate_kbyte_per_s",
                    "tx_rate_kbps",
                    "tx_rate_KBps",
                ]),
                rxUsedKbyte: floatFromFirstKey(raw, [
                    "rx_used_kbyte",
                    "rx_used_kb",
                    "rx_used_KB",
                ]),
                txUsedKbyte: floatFromFirstKey(raw, [
                    "tx_used_kbyte",
                    "tx_used_kb",
                    "tx_used_KB",
                ]),
                timestamp: String(raw.timestamp ?? ""),
            };

            return {
                requestId: toolResult.requestId,
                success: true,
                metrics,
                raw,
            };
        } catch (e) {
            return {
                requestId: toolResult.requestId,
                success: false,
                metrics: undefined,
                errorMessage: `Failed to parse get_metrics response: ${e}`,
                raw: {},
            };
        }
    }
}
