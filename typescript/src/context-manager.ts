import type { Client } from "./api/client";
import { GetContextInfoRequest, SyncContextRequest } from "./api/models";
import {
    logOperationStart,
    logOperationSuccess,
    logOperationError,
} from "./logger";

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export interface SessionLike {
    getApiKey(): string;
    getSessionId(): string;
    getClient(): Client;
}

export interface ContextStatusData {
    contextId: string;
    path: string;
    errorMessage: string;
    status: string;
    startTime: number;
    finishTime: number;
    taskType: string;
}

export interface ContextInfoResult {
    requestId: string;
    success: boolean;
    items: ContextStatusData[];
    errorMessage?: string;
}

export interface ContextSyncResult {
    requestId: string;
    success: boolean;
    errorMessage?: string;
}

function parseContextStatusData(data: Record<string, unknown>): ContextStatusData {
    return {
        contextId: (data.contextId as string) ?? "",
        path: (data.path as string) ?? "",
        errorMessage: (data.errorMessage as string) ?? "",
        status: (data.status as string) ?? "",
        startTime: (data.startTime as number) ?? 0,
        finishTime: (data.finishTime as number) ?? 0,
        taskType: (data.taskType as string) ?? "",
    };
}

/**
 * Context manager for the session: query context sync status and trigger sync (upload/download).
 */
export class ContextManager {
    private session: SessionLike;

    constructor(session: SessionLike) {
        this.session = session;
    }

    toJSON(): Record<string, unknown> {
        return { sessionId: this.session.getSessionId() };
    }

    /**
     * Get context sync status (optionally filtered by contextId, path, taskType).
     *
     * @param contextId - Optional context ID filter
     * @param path - Optional path filter
     * @param taskType - Optional task type filter
     * @returns Promise resolving to ContextInfoResult with items (contextId, path, status, etc.)
     */
    async info(
        contextId?: string,
        path?: string,
        taskType?: string
    ): Promise<ContextInfoResult> {
        let opDetails = `SessionId=${this.session.getSessionId()}`;
        if (contextId) opDetails += `, ContextId=${contextId}`;
        if (path) opDetails += `, Path=${path}`;
        if (taskType) opDetails += `, TaskType=${taskType}`;
        logOperationStart("ContextManager.info", opDetails);

        const request = new GetContextInfoRequest(
            `Bearer ${this.session.getApiKey()}`,
            this.session.getSessionId(),
            contextId,
            path,
            taskType
        );

        const response = await this.session.getClient().getContextInfo(request);

        const requestId = response.getRequestId?.() ?? "";

        if (!response.isSuccessful()) {
            const errorMsg = response.getErrorMessage();
            logOperationError("ContextManager.info", errorMsg || "Unknown error");
            return {
                requestId,
                success: false,
                items: [],
                errorMessage: errorMsg,
            };
        }

        try {
            const contextStatusRaw = response.getContextStatus();
            const contextStatusData: ContextStatusData[] = [];

            if (contextStatusRaw) {
                try {
                    const statusStr =
                        typeof contextStatusRaw === "string"
                            ? contextStatusRaw
                            : JSON.stringify(contextStatusRaw);
                    const statusItems = JSON.parse(statusStr) as unknown[];

                    for (const item of statusItems) {
                        const obj = item as Record<string, unknown>;
                        if (obj.type === "data") {
                            const dataStr = (obj.data as string) ?? "[]";
                            const dataItems = JSON.parse(dataStr) as unknown[];

                            for (const dataItem of dataItems) {
                                try {
                                    contextStatusData.push(
                                        parseContextStatusData(
                                            dataItem as Record<string, unknown>
                                        )
                                    );
                                } catch (e) {
                                    const errMsg = e instanceof Error ? e.message : String(e);
                                    logOperationError(
                                        "ContextManager.info",
                                        `Error parsing data item: ${errMsg}`
                                    );
                                    return {
                                        requestId,
                                        success: false,
                                        items: [],
                                        errorMessage: `Failed to parse data item: ${errMsg}`,
                                    };
                                }
                            }
                        }
                    }
                } catch (e) {
                    const errMsg = e instanceof Error ? e.message : String(e);
                    logOperationError(
                        "ContextManager.info",
                        `Unexpected error parsing context status: ${errMsg}`
                    );
                    return {
                        requestId,
                        success: false,
                        items: [],
                        errorMessage: `Unexpected error parsing context status: ${errMsg}`,
                    };
                }
            }

            const resultMsg = `Found ${contextStatusData.length} status entries, RequestId=${requestId}`;
            logOperationSuccess("ContextManager.info", resultMsg);

            return {
                requestId,
                success: true,
                items: contextStatusData,
            };
        } catch (e) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("ContextManager.info", `Error parsing response: ${errMsg}`);
            return {
                requestId,
                success: false,
                items: [],
                errorMessage: `Failed to parse response: ${errMsg}`,
            };
        }
    }

    /**
     * Trigger context sync (upload or download). Omit contextId and path to sync all contexts.
     *
     * @param contextId - Optional; if provided, path must also be provided
     * @param path - Optional; sync only this context path
     * @param mode - Optional sync mode
     * @param maxRetries - Max poll retries (default 150)
     * @param retryInterval - Poll interval ms (default 1500)
     * @param callback - Optional callback with success
     * @returns Promise resolving to ContextSyncResult
     */
    async sync(
        contextId?: string,
        path?: string,
        mode?: string,
        maxRetries = 150,
        retryInterval = 1500,
        callback?: (success: boolean) => void
    ): Promise<ContextSyncResult> {
        const hasContextId = contextId != null && contextId.trim() !== "";
        const hasPath = path != null && path.trim() !== "";

        if (hasContextId !== hasPath) {
            const errorMessage =
                "context_id and path must be provided together or both omitted. " +
                "If you want to sync a specific context, both context_id and path are required. " +
                "If you want to sync all contexts, omit both parameters.";
            return {
                requestId: "",
                success: false,
                errorMessage,
            };
        }

        let opDetails = `SessionId=${this.session.getSessionId()}`;
        if (contextId) opDetails += `, ContextId=${contextId}`;
        if (path) opDetails += `, Path=${path}`;
        if (mode) opDetails += `, Mode=${mode}`;
        logOperationStart("ContextManager.sync", opDetails);

        const request = new SyncContextRequest(
            `Bearer ${this.session.getApiKey()}`,
            this.session.getSessionId(),
            contextId,
            path,
            mode
        );

        const response = await this.session.getClient().syncContext(request);

        const requestId = response.getRequestId?.() ?? "";
        const success = response.isSuccessful();

        if (!success) {
            const errorMsg = response.getErrorMessage();
            logOperationError("ContextManager.sync", errorMsg || "Unknown error");
            return {
                requestId,
                success: false,
                errorMessage: errorMsg,
            };
        }

        logOperationSuccess("ContextManager.sync", `RequestId=${requestId}`);

        if (callback != null) {
            this.pollForCompletion(
                contextId,
                path,
                maxRetries,
                retryInterval
            ).then((finalSuccess) => {
                callback(finalSuccess);
            }).catch(() => {
                callback(false);
            });
            return { requestId, success: true };
        }

        const finalSuccess = await this.pollForCompletion(
            contextId,
            path,
            maxRetries,
            retryInterval
        );
        return { requestId, success: finalSuccess };
    }

    private async pollForCompletion(
        contextId?: string,
        path?: string,
        maxRetries = 150,
        retryInterval = 1500
    ): Promise<boolean> {
        for (let retry = 0; retry < maxRetries; retry++) {
            try {
                const infoResult = await this.info(contextId, path);

                let allCompleted = true;
                let hasFailure = false;
                let hasSyncTasks = false;

                for (const item of infoResult.items) {
                    if (item.taskType !== "upload" && item.taskType !== "download") {
                        continue;
                    }

                    hasSyncTasks = true;

                    if (item.status !== "Success" && item.status !== "Failed") {
                        allCompleted = false;
                        break;
                    }

                    if (item.status === "Failed") {
                        hasFailure = true;
                    }
                }

                if (allCompleted || !hasSyncTasks) {
                    if (hasFailure) {
                        return false;
                    }
                    return true;
                }

                await sleep(retryInterval);
            } catch (e) {
                const errMsg = e instanceof Error ? e.message : String(e);
                logOperationError(
                    "ContextManager.pollForCompletion",
                    `Error checking context status on attempt ${retry + 1}: ${errMsg}`
                );
                await sleep(retryInterval);
            }
        }

        logOperationError(
            "ContextManager.pollForCompletion",
            `Context sync polling timed out after ${maxRetries} attempts`
        );
        return false;
    }
}
