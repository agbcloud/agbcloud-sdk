import { CallMcpToolRequest } from "./models";
import type { OperationResult } from "../types/api-response";
import { logDebug } from "../logger";

export interface SessionLike {
    getApiKey(): string;
    getSessionId(): string;
    getClient(): unknown;
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

    async callMcpTool(
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
}
