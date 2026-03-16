import * as fs from "fs";
import * as path from "path";
import { GetAndLoadInternalContextRequest } from "../api/models";
import type { UploadResult, DownloadResult } from "../types/api-response";
import type { Client } from "../api/client";
import {
    logOperationStart,
    logOperationSuccess,
    logOperationError,
    logInfo,
} from "../logger";

const FINISHED_STATES = new Set([
    "success",
    "successful",
    "ok",
    "finished",
    "done",
    "completed",
    "complete",
]);

interface AgbLike {
    apiKey: string;
    client: Client;
    context: {
        getFileUploadUrl(
            contextId: string,
            filePath: string
        ): Promise<{ success: boolean; url: string; requestId?: string; errorMessage?: string }>;
        getFileDownloadUrl(
            contextId: string,
            filePath: string
        ): Promise<{ success: boolean; url: string; requestId?: string; errorMessage?: string }>;
    };
}

interface ContextStatusItem {
    contextId?: string;
    path?: string;
    taskType?: string;
    status?: string;
    errorMessage?: string;
}

interface SessionLike {
    getApiKey(): string;
    getSessionId(): string;
    context: {
        sync(
            contextId?: string,
            path?: string,
            mode?: string,
        ): Promise<{ success: boolean; requestId?: string }>;
        info(
            contextId?: string,
            path?: string,
            taskType?: string,
        ): Promise<{
            success: boolean;
            items?: ContextStatusItem[];
            contextStatusData?: ContextStatusItem[];
        }>;
    };
}

function extractRemoteDirPath(remotePath: string): string | undefined {
    const raw = remotePath.trim().replace(/\\/g, "/");
    if (!raw) return undefined;
    if (raw === "/") return "/";
    if (raw.endsWith("/")) {
        const normalized = raw.replace(/\/+$/, "");
        return normalized || "/";
    }
    const parent = path.posix.dirname(raw);
    return parent === "." ? undefined : parent;
}

export class FileTransfer {
    private agb: AgbLike;
    private session: SessionLike;
    private httpTimeout: number;
    contextId?: string;
    contextPath?: string;

    constructor(
        agb: AgbLike,
        session: SessionLike,
        httpTimeout = 60000,
    ) {
        this.agb = agb;
        this.session = session;
        this.httpTimeout = httpTimeout;
    }

    async ensureContextId(): Promise<{ success: boolean; error?: string }> {
        if (this.contextId) return { success: true };

        try {
            logOperationStart(
                "FileTransfer.ensureContextId",
                `SessionId=${this.session.getSessionId()}`
            );
            const request = new GetAndLoadInternalContextRequest(
                `Bearer ${this.agb.apiKey}`,
                this.session.getSessionId(),
                ["file_transfer"],
            );

            const response = await this.agb.client.getAndLoadInternalContext(request);
            if (!response.isSuccessful()) {
                const errorMsg = response.getErrorMessage();
                logOperationError("FileTransfer.ensureContextId", errorMsg);
                return { success: false, error: errorMsg };
            }

            const data = response.getContextList();
            if (Array.isArray(data) && data.length > 0) {
                for (const item of data) {
                    const cid = item.contextId;
                    const cpath = item.contextPath;
                    if (cid && cpath) {
                        this.contextId = cid;
                        this.contextPath = cpath;
                        logOperationSuccess(
                            "FileTransfer.ensureContextId",
                            `ContextId=${cid}, ContextPath=${cpath}`
                        );
                        return { success: true };
                    }
                }
            }
            const errorMsg = "Response contains no data";
            logOperationError("FileTransfer.ensureContextId", errorMsg);
            return { success: false, error: errorMsg };
        } catch (e) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileTransfer.ensureContextId", errMsg);
            return { success: false, error: errMsg };
        }
    }

    async upload(
        localPath: string,
        remotePath: string,
        options?: {
            contentType?: string;
            wait?: boolean;
            waitTimeout?: number;
            pollInterval?: number;
            progressCallback?: (bytesSent: number) => void;
        },
    ): Promise<UploadResult> {
        const wait = options?.wait ?? true;
        const waitTimeout = options?.waitTimeout ?? 30000;
        const pollInterval = options?.pollInterval ?? 1500;

        logOperationStart(
            "FileTransfer.upload",
            `LocalPath=${localPath}, RemotePath=${remotePath}, Wait=${wait}`
        );

        if (!fs.existsSync(localPath) || !fs.statSync(localPath).isFile()) {
            const errorMsg = `Local file not found: ${localPath}`;
            logOperationError("FileTransfer.upload", errorMsg);
            return { success: false, bytesSent: 0, path: remotePath, errorMessage: errorMsg };
        }

        if (!this.contextId) {
            const ensureResult = await this.ensureContextId();
            if (!ensureResult.success) {
                return { success: false, bytesSent: 0, path: remotePath, errorMessage: ensureResult.error };
            }
        }
        if (!this.contextId) {
            return { success: false, bytesSent: 0, path: remotePath, errorMessage: "Context ID not available" };
        }

        const urlRes = await this.agb.context.getFileUploadUrl(this.contextId, remotePath);
        const urlPreview =
            urlRes.url && urlRes.url.length > 120
                ? `${urlRes.url.slice(0, 80)}...${urlRes.url.slice(-40)}`
                : urlRes.url;
        logInfo(
            "getFileUploadUrl result:",
            JSON.stringify({
                success: urlRes.success,
                requestId: urlRes.requestId,
                errorMessage: urlRes.errorMessage,
                urlLength: urlRes.url?.length ?? 0,
                urlPreview,
            }),
        );
        if (!urlRes.success || !urlRes.url) {
            const errorMsg = `getFileUploadUrl failed: ${urlRes.errorMessage ?? "unknown error"}`;
            logOperationError("FileTransfer.upload", errorMsg);
            return {
                success: false,
                requestIdUploadUrl: urlRes.requestId,
                bytesSent: 0,
                path: remotePath,
                errorMessage: errorMsg,
            };
        }

        const uploadUrl = urlRes.url;
        const reqIdUpload = urlRes.requestId;

        let httpStatus: number | undefined;
        let etag: string | undefined;
        let bytesSent = 0;
        try {
            const fileBuffer = fs.readFileSync(localPath);
            bytesSent = fileBuffer.length;
            const headers: Record<string, string> = {};
            if (options?.contentType) {
                headers["Content-Type"] = options.contentType;
            }

            const fetchResp = await fetch(uploadUrl, {
                method: "PUT",
                body: fileBuffer,
                headers,
                signal: AbortSignal.timeout(this.httpTimeout),
            });
            httpStatus = fetchResp.status;
            etag = fetchResp.headers.get("etag") ?? undefined;

            if (!fetchResp.ok) {
                let respBody = "";
                try { respBody = await fetchResp.text(); } catch { /* ignore */ }
                const errorMsg = `Upload failed with HTTP ${httpStatus}`;
                logOperationError("FileTransfer.upload", `${errorMsg} body=${respBody}`);
                return {
                    success: false,
                    requestIdUploadUrl: reqIdUpload,
                    httpStatus,
                    etag,
                    bytesSent,
                    path: remotePath,
                    errorMessage: errorMsg,
                };
            }
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileTransfer.upload", errMsg);
            return {
                success: false,
                requestIdUploadUrl: reqIdUpload,
                bytesSent: 0,
                path: remotePath,
                errorMessage: `Upload exception: ${errMsg}`,
            };
        }

        let reqIdSync: string | undefined;
        try {
            reqIdSync = await this.awaitSync("download", remotePath, this.contextId);
        } catch (e) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileTransfer.upload", `Sync failed: ${errMsg}`);
            return {
                success: false,
                requestIdUploadUrl: reqIdUpload,
                requestIdSync: reqIdSync,
                httpStatus,
                etag,
                bytesSent,
                path: remotePath,
                errorMessage: `session.context.sync(download) failed: ${errMsg}`,
            };
        }

        if (wait) {
            const waitResult = await this.waitForTask(
                this.contextId,
                remotePath,
                "download",
                waitTimeout,
                pollInterval,
            );
            if (!waitResult.success) {
                return {
                    success: false,
                    requestIdUploadUrl: reqIdUpload,
                    requestIdSync: reqIdSync,
                    httpStatus,
                    etag,
                    bytesSent,
                    path: remotePath,
                    errorMessage: `Upload sync not finished: ${waitResult.error ?? "timeout"}`,
                };
            }
        }

        logOperationSuccess(
            "FileTransfer.upload",
            `RemotePath=${remotePath}, BytesSent=${bytesSent}`
        );
        return {
            success: true,
            requestIdUploadUrl: reqIdUpload,
            requestIdSync: reqIdSync,
            httpStatus,
            etag,
            bytesSent,
            path: remotePath,
        };
    }

    async download(
        remotePath: string,
        localPath: string,
        options?: {
            overwrite?: boolean;
            wait?: boolean;
            waitTimeout?: number;
            pollInterval?: number;
            progressCallback?: (bytesReceived: number) => void;
        },
    ): Promise<DownloadResult> {
        const overwrite = options?.overwrite ?? true;
        const wait = options?.wait ?? true;
        const waitTimeout = options?.waitTimeout ?? 30000;
        const pollInterval = options?.pollInterval ?? 1500;

        logOperationStart(
            "FileTransfer.download",
            `RemotePath=${remotePath}, LocalPath=${localPath}, Wait=${wait}`
        );

        if (!this.contextId) {
            const ensureResult = await this.ensureContextId();
            if (!ensureResult.success) {
                return {
                    success: false, bytesReceived: 0, path: remotePath,
                    localPath, errorMessage: ensureResult.error,
                };
            }
        }
        if (!this.contextId) {
            return {
                success: false, bytesReceived: 0, path: remotePath,
                localPath, errorMessage: "Context ID not available",
            };
        }

        let reqIdSync: string | undefined;
        try {
            reqIdSync = await this.awaitSync("upload", remotePath, this.contextId);
        } catch (e) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileTransfer.download", `Sync failed: ${errMsg}`);
            return {
                success: false, requestIdSync: reqIdSync, bytesReceived: 0,
                path: remotePath, localPath,
                errorMessage: `session.context.sync(upload) failed: ${errMsg}`,
            };
        }

        if (wait) {
            const waitResult = await this.waitForTask(
                this.contextId,
                remotePath,
                "upload",
                waitTimeout,
                pollInterval,
            );
            if (!waitResult.success) {
                return {
                    success: false, requestIdSync: reqIdSync, bytesReceived: 0,
                    path: remotePath, localPath,
                    errorMessage: `Download sync not finished: ${waitResult.error ?? "timeout"}`,
                };
            }
        }

        const urlRes = await this.agb.context.getFileDownloadUrl(this.contextId, remotePath);
        if (!urlRes.success || !urlRes.url) {
            const errorMsg = `getFileDownloadUrl failed: ${urlRes.errorMessage ?? "unknown error"}`;
            logOperationError("FileTransfer.download", errorMsg);
            return {
                success: false,
                requestIdDownloadUrl: urlRes.requestId,
                requestIdSync: reqIdSync,
                bytesReceived: 0,
                path: remotePath,
                localPath,
                errorMessage: errorMsg,
            };
        }

        const downloadUrl = urlRes.url;
        const reqIdDownload = urlRes.requestId;

        if (!overwrite && fs.existsSync(localPath)) {
            return {
                success: false,
                requestIdDownloadUrl: reqIdDownload,
                requestIdSync: reqIdSync,
                bytesReceived: 0,
                path: remotePath,
                localPath,
                errorMessage: `Destination exists and overwrite=false: ${localPath}`,
            };
        }

        try {
            const dir = path.dirname(localPath);
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }

            const fetchResp = await fetch(downloadUrl, {
                signal: AbortSignal.timeout(this.httpTimeout),
            });

            if (!fetchResp.ok) {
                const errorMsg = `Download failed with HTTP ${fetchResp.status}`;
                logOperationError("FileTransfer.download", errorMsg);
                return {
                    success: false,
                    requestIdDownloadUrl: reqIdDownload,
                    requestIdSync: reqIdSync,
                    httpStatus: fetchResp.status,
                    bytesReceived: 0,
                    path: remotePath,
                    localPath,
                    errorMessage: errorMsg,
                };
            }

            const arrayBuf = await fetchResp.arrayBuffer();
            const buffer = Buffer.from(arrayBuf);
            fs.writeFileSync(localPath, buffer);
            const bytesReceived = buffer.length;

            logOperationSuccess(
                "FileTransfer.download",
                `RemotePath=${remotePath}, LocalPath=${localPath}, BytesReceived=${bytesReceived}`
            );
            return {
                success: true,
                requestIdDownloadUrl: reqIdDownload,
                requestIdSync: reqIdSync,
                httpStatus: 200,
                bytesReceived,
                path: remotePath,
                localPath,
            };
        } catch (e) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileTransfer.download", errMsg);
            return {
                success: false,
                requestIdDownloadUrl: reqIdDownload,
                requestIdSync: reqIdSync,
                bytesReceived: 0,
                path: remotePath,
                localPath,
                errorMessage: `Download exception: ${errMsg}`,
            };
        }
    }

    private async awaitSync(
        mode: string,
        remotePath: string,
        contextId: string,
    ): Promise<string | undefined> {
        const syncFn = this.session.context.sync.bind(this.session.context);
        const dirPath = extractRemoteDirPath(remotePath);

        try {
            const result = await syncFn(contextId, dirPath, mode);
            return result.requestId;
        } catch {
            try {
                const result = await syncFn(undefined, dirPath, mode);
                return result.requestId;
            } catch {
                try {
                    const result = await syncFn(undefined, undefined, mode);
                    return result.requestId;
                } catch {
                    const result = await syncFn();
                    return result.requestId;
                }
            }
        }
    }

    private async waitForTask(
        contextId: string,
        remotePath: string,
        taskType: string,
        timeout: number,
        interval: number,
    ): Promise<{ success: boolean; error?: string }> {
        const deadline = Date.now() + timeout;
        const dirPath = extractRemoteDirPath(remotePath);
        let lastErr: string | undefined;

        while (Date.now() < deadline) {
            try {
                let res: {
                    success: boolean;
                    items?: ContextStatusItem[];
                    contextStatusData?: ContextStatusItem[];
                };
                try {
                    res = await this.session.context.info(contextId, dirPath, taskType);
                } catch {
                    res = await this.session.context.info();
                }
                const statusList = res.items ?? res.contextStatusData ?? [];
                for (const item of statusList) {
                    if (
                        item.contextId === contextId &&
                        item.path === dirPath &&
                        (taskType === undefined || item.taskType === taskType)
                    ) {
                        if (item.errorMessage) {
                            return { success: false, error: `Task error: ${item.errorMessage}` };
                        }
                        if (item.status && FINISHED_STATES.has(item.status.toLowerCase())) {
                            return { success: true };
                        }
                    }
                }
                lastErr = "task not finished";
            } catch (e) {
                lastErr = `info error: ${e instanceof Error ? e.message : String(e)}`;
            }
            await new Promise((r) => setTimeout(r, interval));
        }
        return { success: false, error: lastErr ?? "timeout" };
    }
}
