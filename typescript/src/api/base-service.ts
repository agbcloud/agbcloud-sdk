import { CallMcpToolRequest } from "./models";
import type { OperationResult, McpTool } from "../types/api-response";
import { logDebug, logOperationStart, logOperationSuccess, logOperationError } from "../logger";
import { WsClient } from "../modules/ws/ws-client";

export interface SessionLike {
    getApiKey(): string;
    getSessionId(): string;
    getClient(): unknown;
    // Properties for LinkUrl routing
    linkUrl?: string;
    token?: string;
    toolList?: string;
    mcpTools?: McpTool[];
    // WebSocket client access for streaming operations
    _getWsClient?(): WsClient;
}

export class BaseService {
    protected session: SessionLike;

    constructor(session: SessionLike) {
        this.session = session;
    }

    toJSON(): Record<string, unknown> {
        return { sessionId: this.session.getSessionId() };
    }

    protected handleError(e: unknown): unknown {
        return e;
    }

    /**
     * Resolve MCP server name by tool name from session tool list.
     */
    protected getMcpServerForTool(toolName: string): string | null {
        // First try mcpTools (parsed array)
        const mcpTools = this.session.mcpTools;
        if (mcpTools && Array.isArray(mcpTools)) {
            for (const tool of mcpTools) {
                if (tool && tool.name === toolName) {
                    return tool.server ?? null;
                }
            }
        }

        // Fallback to parsing toolList string
        const toolList = this.session.toolList;
        if (!toolList) {
            return null;
        }

        try {
            const toolListData = JSON.parse(toolList) as unknown;
            if (Array.isArray(toolListData)) {
                for (const tool of toolListData as Record<string, unknown>[]) {
                    if (tool.name === toolName) {
                        return (tool.server as string) ?? null;
                    }
                }
            }
        } catch (e) {
            logDebug(`Failed to parse tool list: ${e}`);
        }

        return null;
    }

    /**
     * Call MCP tool via LinkUrl route (direct HTTP call).
     */
    protected async callMcpToolLinkUrl(
        toolName: string,
        args: Record<string, unknown>,
        serverName: string
    ): Promise<OperationResult> {
        const linkUrl = this.session.linkUrl ?? "";
        const token = this.session.token ?? "";

        if (!linkUrl || !token) {
            return {
                requestId: "",
                success: false,
                errorMessage: "LinkUrl/token not available",
            };
        }

        const requestId = `link-${Date.now()}-${Math.floor(Math.random() * 1000000000).toString().padStart(9, "0")}`;

        logOperationStart(
            "BaseService.callMcpToolLinkUrl",
            `Tool=${toolName}, SessionId=${this.session.getSessionId()}, RequestId=${requestId}`
        );

        const url = linkUrl.replace(/\/$/, "") + "/callTool";
        const payload = {
            args,
            server: serverName,
            requestId,
            tool: toolName,
            token,
        };

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Access-Token": token,
                },
                body: JSON.stringify(payload),
            });

            if (response.status < 200 || response.status >= 300) {
                const errorMsg = `HTTP request failed with code: ${response.status}`;
                logOperationError("BaseService.callMcpToolLinkUrl", errorMsg);
                return {
                    requestId,
                    success: false,
                    errorMessage: errorMsg,
                };
            }

            const outer = (await response.json()) as Record<string, unknown>;
            const dataField = outer.data;

            if (dataField == null) {
                const errorMsg = "No data field in LinkUrl response";
                logOperationError("BaseService.callMcpToolLinkUrl", errorMsg);
                return {
                    requestId,
                    success: false,
                    errorMessage: errorMsg,
                };
            }

            let parsedData: Record<string, unknown>;
            if (typeof dataField === "string") {
                parsedData = JSON.parse(dataField) as Record<string, unknown>;
            } else if (typeof dataField === "object") {
                parsedData = dataField as Record<string, unknown>;
            } else {
                const errorMsg = "Invalid data field type in LinkUrl response";
                logOperationError("BaseService.callMcpToolLinkUrl", errorMsg);
                return {
                    requestId,
                    success: false,
                    errorMessage: errorMsg,
                };
            }

            const resultField = parsedData.result as Record<string, unknown> | undefined;
            if (!resultField || typeof resultField !== "object") {
                const errorMsg = "No result field in LinkUrl response data";
                logOperationError("BaseService.callMcpToolLinkUrl", errorMsg);
                return {
                    requestId,
                    success: false,
                    errorMessage: errorMsg,
                };
            }

            const isError = Boolean(resultField.isError);
            const content = resultField.content as unknown[] | undefined;
            let textContent = "";

            if (Array.isArray(content) && content.length > 0) {
                const first = content[0];
                if (typeof first === "string") {
                    textContent = first;
                } else if (typeof first === "object" && first != null) {
                    const firstObj = first as Record<string, unknown>;
                    textContent = (firstObj.text as string) ?? (firstObj.blob as string) ?? (firstObj.data as string) ?? "";
                }
            }

            if (isError) {
                logOperationError("BaseService.callMcpToolLinkUrl", String(textContent));
                return {
                    requestId,
                    success: false,
                    errorMessage: String(textContent),
                };
            }

            logOperationSuccess(
                "BaseService.callMcpToolLinkUrl",
                `Tool=${toolName}, SessionId=${this.session.getSessionId()}, RequestId=${requestId}`
            );
            return {
                requestId,
                success: true,
                data: String(textContent),
            };
        } catch (e) {
            const errorMsg = `HTTP request failed: ${e}`;
            logOperationError("BaseService.callMcpToolLinkUrl", errorMsg);
            return {
                requestId,
                success: false,
                errorMessage: errorMsg,
            };
        }
    }

    /**
     * Call MCP tool via traditional API route.
     */
    protected async callMcpToolApi(
        name: string,
        args: Record<string, unknown>,
        readTimeout?: number,
        connectTimeout?: number,
    ): Promise<OperationResult> {
        try {
            const argsJson = JSON.stringify(args);

            const request = new CallMcpToolRequest(
                argsJson,
                `Bearer ${this.session.getApiKey()}`,
                undefined,
                name,
                undefined,
                this.session.getSessionId(),
            );

            const client = this.session.getClient() as {
                callMcpTool: (
                    req: CallMcpToolRequest,
                    rt?: number,
                    ct?: number,
                ) => Promise<{
                    requestId?: string;
                    isSuccessful: () => boolean;
                    getToolResult: () => string | null;
                    getErrorMessage: () => string | null;
                    json_data?: Record<string, unknown>;
                }>;
            };

            const response = await client.callMcpTool(
                request,
                readTimeout,
                connectTimeout,
            );

            if (!response) {
                return {
                    requestId: "",
                    success: false,
                    errorMessage: "API client returned null response",
                };
            }

            const requestId = response.requestId ?? "";

            if (response.isSuccessful()) {
                const result = response.getToolResult();
                return {
                    requestId,
                    success: true,
                    data: result,
                };
            }

            const errorMsg =
                response.getErrorMessage() || "Tool execution failed";
            return {
                requestId,
                success: false,
                errorMessage: errorMsg,
            };
        } catch (e: unknown) {
            this.handleError(e);
            const errMsg =
                e instanceof Error ? e.message : String(e);
            return {
                requestId: "",
                success: false,
                errorMessage: `Failed to call MCP tool ${name}: ${errMsg}`,
            };
        }
    }

    /**
     * Call MCP tool with intelligent routing.
     *
     * This method routes the call to either:
     * 1. LinkUrl route (direct HTTP) - when linkUrl, token, and serverName are available
     * 2. Traditional API route - fallback method
     */
    async callMcpTool(
        name: string,
        args: Record<string, unknown>,
        readTimeout?: number,
        connectTimeout?: number,
    ): Promise<OperationResult> {
        // Try to resolve server name from tool list
        const serverName = this.getMcpServerForTool(name) ?? "";

        // Check if we can use LinkUrl route
        const linkUrl = this.session.linkUrl ?? "";
        const token = this.session.token ?? "";

        if (linkUrl && token && serverName) {
            logDebug(`Using LinkUrl route for tool: ${name}`);
            return this.callMcpToolLinkUrl(name, args, serverName);
        }

        // Fallback to traditional API route
        logDebug(`Using API route for tool: ${name}`);
        return this.callMcpToolApi(name, args, readTimeout, connectTimeout);
    }
}
