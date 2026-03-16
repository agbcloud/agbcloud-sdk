import type { Client } from "./api/client";
import {
    ListContextsRequest,
    GetContextRequest,
    ModifyContextRequest,
    DeleteContextRequest,
    ClearContextRequest,
    GetContextFileDownloadUrlRequest,
    GetContextFileUploadUrlRequest,
    DeleteContextFileRequest,
    DescribeContextFilesRequest,
} from "./api/models";
import type {
    ContextResult,
    ContextListResult,
    OperationResult,
    FileUrlResult,
    ContextFileListResult,
    ClearContextResult,
    ContextFileEntry,
} from "./types/api-response";
import {
    logOperationStart,
    logOperationSuccess,
    logOperationError,
} from "./logger";

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export interface AGBLike {
    apiKey: string;
    client: Client;
}

export class Context {
    id: string;
    name: string;
    createdAt?: string;
    lastUsedAt?: string;

    constructor(
        id: string,
        name: string,
        createdAt?: string,
        lastUsedAt?: string
    ) {
        this.id = id;
        this.name = name;
        this.createdAt = createdAt;
        this.lastUsedAt = lastUsedAt;
    }
}

export interface ContextListParams {
    maxResults?: number;
    nextToken?: string;
}

export class ContextService {
    private agb: AGBLike;

    constructor(agb: AGBLike) {
        this.agb = agb;
    }

    toJSON(): Record<string, unknown> {
        return { type: "ContextService" };
    }

    async list(params?: ContextListParams): Promise<ContextListResult> {
        try {
            const maxResults = params?.maxResults ?? 10;
            const nextToken = params?.nextToken;
            const requestDetails = `MaxResults=${maxResults}${nextToken ? `, NextToken=${nextToken}` : ""
                }`;
            logOperationStart("ContextService.list", requestDetails);

            const request = new ListContextsRequest(
                `Bearer ${this.agb.apiKey}`,
                maxResults,
                nextToken
            );
            const response = await this.agb.client.listContexts(request);

            const requestId = response.getRequestId?.() ?? "";

            if (!response.isSuccessful()) {
                const errorMsg = response.getErrorMessage();
                logOperationError("ContextService.list", errorMsg || "Unknown error");
                return {
                    requestId,
                    success: false,
                    contexts: [],
                    errorMessage: errorMsg,
                };
            }

            try {
                const contexts: Context[] = [];
                const responseData = response.getContextsData();
                if (responseData && Array.isArray(responseData)) {
                    for (const contextData of responseData) {
                        contexts.push(
                            new Context(
                                contextData.id ?? "",
                                contextData.name ?? "",
                                contextData.createTime,
                                contextData.lastUsedTime
                            )
                        );
                    }
                }

                const nextTokenResult = response.getNextToken();
                const maxResultsActual = response.getMaxResults() ?? maxResults;
                const totalCount = contexts.length;

                const resultMsg = `Found ${contexts.length} contexts, TotalCount=${totalCount}`;
                logOperationSuccess("ContextService.list", resultMsg);

                return {
                    requestId,
                    success: true,
                    contexts: contexts.map((c) => ({
                        id: c.id,
                        name: c.name,
                        createdAt: c.createdAt,
                        lastUsedAt: c.lastUsedAt,
                    })),
                    errorMessage: undefined,
                };
            } catch (e) {
                const errMsg = e instanceof Error ? e.message : String(e);
                logOperationError("parse ListContexts response", errMsg);
                return {
                    requestId,
                    success: false,
                    contexts: [],
                    errorMessage: errMsg,
                };
            }
        } catch (e) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("ListContexts", errMsg);
            return {
                requestId: "",
                success: false,
                contexts: [],
                errorMessage: errMsg,
            };
        }
    }

    async get(
        name?: string,
        create = false,
        loginRegionId?: string,
        contextId?: string
    ): Promise<ContextResult> {
        const originalContextId = contextId;
        const originalName = name;

        try {
            const nameVal = name?.trim() || undefined;
            const contextIdVal = contextId?.trim() || undefined;

            if (!contextIdVal && !nameVal) {
                const errorMsg =
                    "Either context_id or name must be provided (cannot both be empty)";
                logOperationError("ContextService.get", errorMsg);
                return { success: false, errorMessage: errorMsg, requestId: "" };
            }

            if (create && contextIdVal) {
                const errorMsg =
                    "context_id cannot be provided when create=True (only name is allowed when creating)";
                logOperationError("ContextService.get", errorMsg);
                return { success: false, errorMessage: errorMsg, requestId: "" };
            }

            const opDetails = `Name=${nameVal ?? "None"}, ContextId=${contextIdVal ?? "None"}, Create=${create}${loginRegionId ? `, LoginRegionId=${loginRegionId}` : ""
                }`;
            logOperationStart("ContextService.get", opDetails);

            const request = new GetContextRequest(
                `Bearer ${this.agb.apiKey}`,
                contextIdVal,
                nameVal,
                create,
                loginRegionId
            );
            const response = await this.agb.client.getContext(request);

            const requestId = response.getRequestId?.() ?? "";

            if (!response.isSuccessful()) {
                const errorMsg = response.getErrorMessage();
                logOperationError("ContextService.get", errorMsg || "Unknown error");
                return {
                    requestId,
                    success: false,
                    context: undefined,
                    errorMessage: errorMsg,
                };
            }

            try {
                const data = response.getContextData();
                if (!data) {
                    return {
                        requestId,
                        success: false,
                        context: undefined,
                        errorMessage: "No context data in response",
                    };
                }
                const resultContextId = data.id ?? contextIdVal ?? "";
                const context = new Context(
                    resultContextId,
                    data.name ?? nameVal ?? "",
                    data.createTime,
                    data.lastUsedTime
                );
                const resultMsg = `ContextId=${resultContextId}, Name=${context.name}`;
                logOperationSuccess("ContextService.get", resultMsg);
                return {
                    requestId,
                    success: true,
                    context: {
                        id: context.id,
                        name: context.name,
                        createdAt: context.createdAt,
                        lastUsedAt: context.lastUsedAt,
                    },
                };
            } catch (e) {
                const errMsg = e instanceof Error ? e.message : String(e);
                logOperationError("parse GetContext response", errMsg);
                return {
                    requestId,
                    success: false,
                    context: undefined,
                    errorMessage: `Failed to parse response: ${errMsg}`,
                };
            }
        } catch (e) {
            const errMsg = e instanceof Error ? e.message : String(e);
            const contextIdentifier = originalContextId ?? originalName ?? "unknown";
            logOperationError("GetContext", errMsg);
            return {
                requestId: "",
                success: false,
                context: undefined,
                errorMessage: `Failed to get context ${contextIdentifier}: ${errMsg}`,
            };
        }
    }

    async create(name: string): Promise<ContextResult> {
        if (!name || (typeof name === "string" && !name.trim())) {
            const errorMsg = "name cannot be empty or None";
            logOperationError("ContextService.create", errorMsg);
            return { success: false, errorMessage: errorMsg, requestId: "" };
        }
        return this.get(name.trim(), true);
    }

    async update(context: Context): Promise<OperationResult> {
        if (!context) {
            logOperationError("ContextService.update", "context cannot be None");
            return {
                requestId: "",
                success: false,
                errorMessage: "context cannot be None",
            };
        }
        if (!context.id || (typeof context.id === "string" && !context.id.trim())) {
            const errorMsg = "context.id cannot be empty or None";
            logOperationError("ContextService.update", errorMsg);
            return { requestId: "", success: false, errorMessage: errorMsg };
        }
        if (
            !context.name ||
            (typeof context.name === "string" && !context.name.trim())
        ) {
            const errorMsg = "context.name cannot be empty or None";
            logOperationError("ContextService.update", errorMsg);
            return { requestId: "", success: false, errorMessage: errorMsg };
        }

        try {
            const contextId = context.id.trim();
            const contextName = context.name.trim();
            logOperationStart("ContextService.update", `ContextId=${contextId}, Name=${contextName}`);

            const request = new ModifyContextRequest(
                `Bearer ${this.agb.apiKey}`,
                contextId,
                contextName
            );
            const response = await this.agb.client.modifyContext(request);

            const requestId = response.getRequestId?.() ?? "";

            if (!response.isSuccessful()) {
                const errorMsg = response.getErrorMessage();
                logOperationError("ContextService.update", errorMsg || "Unknown error");
                return { requestId, success: false, errorMessage: errorMsg };
            }

            const resultMsg = `ContextId=${contextId}, RequestId=${requestId}`;
            logOperationSuccess("ContextService.update", resultMsg);
            return {
                requestId,
                success: true,
                data: { context_id: contextId },
            };
        } catch (e) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("ContextService.update", errMsg);
            return {
                requestId: "",
                success: false,
                errorMessage: `Failed to update context ${context.id}: ${errMsg}`,
            };
        }
    }

    async delete(context: Context): Promise<OperationResult> {
        if (!context) {
            logOperationError("ContextService.delete", "context cannot be None");
            return {
                success: false,
                errorMessage: "context cannot be None",
                requestId: "",
            };
        }
        if (!context.id || (typeof context.id === "string" && !context.id.trim())) {
            const errorMsg = "context.id cannot be empty or None";
            logOperationError("ContextService.delete", errorMsg);
            return { requestId: "", success: false, errorMessage: errorMsg };
        }

        try {
            const contextId = context.id.trim();
            logOperationStart("ContextService.delete", `ContextId=${contextId}`);

            const request = new DeleteContextRequest(
                `Bearer ${this.agb.apiKey}`,
                contextId
            );
            const response = await this.agb.client.deleteContext(request);

            const requestId = response.getRequestId?.() ?? "";

            if (!response.isSuccessful()) {
                const errorMsg = response.getErrorMessage();
                logOperationError("ContextService.delete", errorMsg || "Unknown error");
                return { requestId, success: false, errorMessage: errorMsg };
            }

            const resultMsg = `ContextId=${contextId}, RequestId=${requestId}`;
            logOperationSuccess("ContextService.delete", resultMsg);
            return {
                requestId,
                success: true,
                data: { context_id: contextId },
            };
        } catch (e) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("ContextService.delete", errMsg);
            return {
                requestId: "",
                success: false,
                errorMessage: `Failed to delete context ${context.id}: ${errMsg}`,
            };
        }
    }

    async getFileDownloadUrl(
        contextId: string,
        filePath: string
    ): Promise<FileUrlResult> {
        if (!contextId || (typeof contextId === "string" && !contextId.trim())) {
            const errorMsg = "context_id cannot be empty or None";
            logOperationError("ContextService.getFileDownloadUrl", errorMsg);
            return { requestId: "", success: false, url: "", errorMessage: errorMsg };
        }
        if (!filePath || (typeof filePath === "string" && !filePath.trim())) {
            const errorMsg = "file_path cannot be empty or None";
            logOperationError("ContextService.getFileDownloadUrl", errorMsg);
            return { requestId: "", success: false, url: "", errorMessage: errorMsg };
        }

        const validatedContextId = contextId.trim();
        const validatedFilePath = filePath.trim();
        logOperationStart(
            "ContextService.getFileDownloadUrl",
            `ContextId=${validatedContextId}, FilePath=${validatedFilePath}`
        );

        const req = new GetContextFileDownloadUrlRequest(
            `Bearer ${this.agb.apiKey}`,
            validatedContextId,
            validatedFilePath
        );
        const resp = await this.agb.client.getContextFileDownloadUrl(req);

        const requestId = resp.getRequestId?.() ?? "";
        const downloadUrl = resp.getDownloadUrl();

        if (resp.isSuccessful()) {
            const resultMsg = `ContextId=${validatedContextId}, FilePath=${validatedFilePath}, RequestId=${requestId}`;
            logOperationSuccess("ContextService.getFileDownloadUrl", resultMsg);
        } else {
            const errorMsg = resp.getErrorMessage();
            logOperationError(
                "ContextService.getFileDownloadUrl",
                errorMsg || "Unknown error"
            );
        }

        return {
            requestId,
            success: resp.isSuccessful(),
            url: downloadUrl ?? "",
            errorMessage: resp.isSuccessful() ? undefined : resp.getErrorMessage(),
        };
    }

    async getFileUploadUrl(
        contextId: string,
        filePath: string
    ): Promise<FileUrlResult> {
        if (!contextId || (typeof contextId === "string" && !contextId.trim())) {
            const errorMsg = "context_id cannot be empty or None";
            logOperationError("ContextService.getFileUploadUrl", errorMsg);
            return { requestId: "", success: false, url: "", errorMessage: errorMsg };
        }
        if (!filePath || (typeof filePath === "string" && !filePath.trim())) {
            const errorMsg = "file_path cannot be empty or None";
            logOperationError("ContextService.getFileUploadUrl", errorMsg);
            return { requestId: "", success: false, url: "", errorMessage: errorMsg };
        }

        const validatedContextId = contextId.trim();
        const validatedFilePath = filePath.trim();
        logOperationStart(
            "ContextService.getFileUploadUrl",
            `ContextId=${validatedContextId}, FilePath=${validatedFilePath}`
        );

        const req = new GetContextFileUploadUrlRequest(
            `Bearer ${this.agb.apiKey}`,
            validatedContextId,
            validatedFilePath
        );
        const resp = await this.agb.client.getContextFileUploadUrl(req);

        const requestId = resp.getRequestId?.() ?? "";
        const uploadUrl = resp.getUploadUrl();

        if (resp.isSuccessful()) {
            const resultMsg = `ContextId=${validatedContextId}, FilePath=${validatedFilePath}, RequestId=${requestId}`;
            logOperationSuccess("ContextService.getFileUploadUrl", resultMsg);
        } else {
            const errorMsg = resp.getErrorMessage();
            logOperationError(
                "ContextService.getFileUploadUrl",
                errorMsg || "Unknown error"
            );
        }

        return {
            requestId,
            success: resp.isSuccessful(),
            url: uploadUrl ?? "",
            errorMessage: resp.isSuccessful() ? undefined : resp.getErrorMessage(),
        };
    }

    async deleteFile(
        contextId: string,
        filePath: string
    ): Promise<OperationResult> {
        if (!contextId || (typeof contextId === "string" && !contextId.trim())) {
            const errorMsg = "context_id cannot be empty or None";
            logOperationError("ContextService.deleteFile", errorMsg);
            return { requestId: "", success: false, errorMessage: errorMsg };
        }
        if (!filePath || (typeof filePath === "string" && !filePath.trim())) {
            const errorMsg = "file_path cannot be empty or None";
            logOperationError("ContextService.deleteFile", errorMsg);
            return { requestId: "", success: false, errorMessage: errorMsg };
        }

        const validatedContextId = contextId.trim();
        const validatedFilePath = filePath.trim();
        logOperationStart(
            "ContextService.deleteFile",
            `ContextId=${validatedContextId}, FilePath=${validatedFilePath}`
        );

        const req = new DeleteContextFileRequest(
            `Bearer ${this.agb.apiKey}`,
            validatedContextId,
            validatedFilePath
        );
        const resp = await this.agb.client.deleteContextFile(req);

        const requestId = resp.getRequestId?.() ?? "";

        if (resp.isSuccessful()) {
            const resultMsg = `ContextId=${validatedContextId}, FilePath=${validatedFilePath}, RequestId=${requestId}`;
            logOperationSuccess("ContextService.deleteFile", resultMsg);
        } else {
            const errorMsg = resp.getErrorMessage();
            logOperationError("ContextService.deleteFile", errorMsg || "Unknown error");
        }

        return {
            requestId,
            success: resp.isSuccessful(),
            data: resp.isSuccessful(),
            errorMessage: resp.isSuccessful() ? undefined : resp.getErrorMessage(),
        };
    }

    async listFiles(
        contextId: string,
        parentFolderPath?: string,
        pageNumber = 1,
        pageSize = 50
    ): Promise<ContextFileListResult> {
        if (!contextId || (typeof contextId === "string" && !contextId.trim())) {
            const errorMsg = "context_id cannot be empty or None";
            logOperationError("ContextService.listFiles", errorMsg);
            return { requestId: "", success: false, files: [], errorMessage: errorMsg };
        }

        const validatedContextId = contextId.trim();
        const validatedParentFolderPath =
            parentFolderPath?.trim() ?? "";
        const opDetails = `ContextId=${validatedContextId}, ParentFolderPath=${validatedParentFolderPath}, PageNumber=${pageNumber}, PageSize=${pageSize}`;
        logOperationStart("ContextService.listFiles", opDetails);

        const req = new DescribeContextFilesRequest(
            `Bearer ${this.agb.apiKey}`,
            validatedContextId,
            validatedParentFolderPath,
            pageNumber,
            pageSize
        );
        const resp = await this.agb.client.describeContextFiles(req);

        const requestId = resp.getRequestId?.() ?? "";

        if (!resp.isSuccessful()) {
            const errorMsg = resp.getErrorMessage();
            logOperationError("ContextService.listFiles", errorMsg || "Unknown error");
            return {
                requestId,
                success: false,
                files: [],
                errorMessage: errorMsg,
            };
        }

        try {
            const rawList = resp.getFilesData();
            const files: ContextFileEntry[] = rawList.map((it) => ({
                fileId: it.fileId,
                name: it.fileName ?? "",
                path: it.filePath ?? "",
                type: it.fileType ?? "",
                createdTime: it.gmtCreate,
                modifiedTime: it.gmtModified,
                size: it.size,
                status: it.status,
            }));

            const count = resp.getCount();
            const resultMsg = `ContextId=${validatedContextId}, Found ${files.length} files, TotalCount=${count}`;
            logOperationSuccess("ContextService.listFiles", resultMsg);

            return {
                requestId,
                success: true,
                files,
                count,
            };
        } catch (e) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("ContextService.listFiles", `Error parsing response: ${errMsg}`);
            return {
                requestId,
                success: false,
                files: [],
                errorMessage: `Failed to parse response: ${errMsg}`,
            };
        }
    }

    async clearAsync(contextId: string): Promise<ClearContextResult> {
        try {
            logOperationStart("ContextService.clearAsync", `ContextId=${contextId}`);

            const request = new ClearContextRequest(
                `Bearer ${this.agb.apiKey}`,
                contextId
            );
            const response = await this.agb.client.clearContext(request);

            const requestId = response.getRequestId?.() ?? "";

            if (!response.isSuccessful()) {
                const errorMsg = response.getErrorMessage() || "Unknown error";
                logOperationError("ContextService.clearAsync", errorMsg);
                return {
                    requestId,
                    success: false,
                    errorMessage: errorMsg,
                };
            }

            const resultMsg = `ContextId=${contextId}, Status=clearing, RequestId=${requestId}`;
            logOperationSuccess("ContextService.clearAsync", resultMsg);
            return {
                requestId,
                success: true,
                state: "clearing",
                errorMessage: undefined,
            };
        } catch (e) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("ContextService.clearAsync", errMsg);
            throw new Error(`Failed to start context clearing for ${contextId}: ${errMsg}`);
        }
    }

    async getClearStatus(contextId: string): Promise<ClearContextResult> {
        try {
            logOperationStart("ContextService.getClearStatus", `ContextId=${contextId}`);

            const request = new GetContextRequest(
                `Bearer ${this.agb.apiKey}`,
                contextId,
                undefined,
                false
            );
            const response = await this.agb.client.getContext(request);

            const requestId = response.getRequestId?.() ?? "";

            if (!response.isSuccessful()) {
                const errorMsg = response.getErrorMessage() || "Unknown error";
                logOperationError("ContextService.getClearStatus", errorMsg);
                return {
                    requestId,
                    success: false,
                    errorMessage: errorMsg,
                };
            }

            const data = response.getContextData();
            const resultContextId = data?.id ?? contextId ?? "";
            const state = data?.state ?? "clearing";

            const resultMsg = `ContextId=${resultContextId}, Status=${state}, RequestId=${requestId}`;
            logOperationSuccess("ContextService.getClearStatus", resultMsg);

            return {
                requestId,
                success: true,
                state,
                errorMessage: undefined,
            };
        } catch (e) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("ContextService.getClearStatus", errMsg);
            return {
                requestId: "",
                success: false,
                errorMessage: `Failed to get clear status: ${errMsg}`,
            };
        }
    }

    async clear(
        contextId: string,
        timeout = 60,
        pollInterval = 2
    ): Promise<ClearContextResult> {
        logOperationStart(
            "ContextService.clear",
            `ContextId=${contextId}, Timeout=${timeout}s, PollInterval=${pollInterval}s`
        );

        const startResult = await this.clearAsync(contextId);
        if (!startResult.success) {
            return startResult;
        }

        const startTime = Date.now();
        const maxAttempts = Math.floor(timeout / pollInterval);
        let attempt = 0;

        while (attempt < maxAttempts) {
            await sleep(pollInterval * 1000);
            attempt += 1;

            const statusResult = await this.getClearStatus(contextId);

            if (!statusResult.success) {
                logOperationError(
                    "ContextService.clear",
                    statusResult.errorMessage ?? "Failed to get clear status"
                );
                return statusResult;
            }

            const state = statusResult.state;

            if (state === "available") {
                const elapsed = (Date.now() - startTime) / 1000;
                const resultMsg = `ContextId=${contextId}, Status=${state}, Elapsed=${elapsed.toFixed(2)}s`;
                logOperationSuccess("ContextService.clear", resultMsg);
                return {
                    requestId: startResult.requestId,
                    success: true,
                    state,
                    errorMessage: undefined,
                };
            }
        }

        const elapsed = (Date.now() - startTime) / 1000;
        const errorMsg = `Context clearing timed out after ${elapsed.toFixed(2)} seconds`;
        logOperationError("ContextService.clear", errorMsg);
        throw new Error(errorMsg);
    }
}
