import { BaseService } from "../api/base-service";
import type {
    BoolResult,
    FileContentResult,
    BinaryFileContentResult,
    MultipleFileContentResult,
    FileInfoResult,
    FileInfo,
    DirectoryListResult,
    FileSearchResult,
    FileChangeResult,
    FileChangeEvent,
    DirectoryEntry,
    UploadResult,
    DownloadResult,
} from "../types/api-response";
import {
    logOperationStart,
    logOperationSuccess,
    logOperationError,
    logWarn,
} from "../logger";
import { FileTransfer } from "./file-transfer";

/** Default chunk size for read/write operations (60KB, aligned with source project). */
const DEFAULT_CHUNK_SIZE = 50 * 1024;

function parseFileInfo(fileInfoStr: string): FileInfo {
    const result: FileInfo = {
        name: "",
        path: "",
        size: 0,
        isDirectory: false,
        modTime: "",
        mode: "",
    };

    const lines = fileInfoStr.split("\n");
    for (const line of lines) {
        if (line.includes(":")) {
            const [key, value] = line.split(":", 2).map((part) => part.trim());
            switch (key) {
                case "name": result.name = value; break;
                case "path": result.path = value; break;
                case "size": result.size = parseInt(value, 10) || 0; break;
                case "isDirectory": result.isDirectory = value === "true"; break;
                case "modTime": result.modTime = value; break;
                case "mode": result.mode = value; break;
                case "owner": result.owner = value; break;
                case "group": result.group = value; break;
            }
        }
    }
    return result;
}

function parseDirectoryListing(text: string): DirectoryEntry[] {
    const entries: DirectoryEntry[] = [];
    const lines = text.split("\n");
    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;

        if (trimmed.startsWith("[DIR]")) {
            entries.push({
                type: "directory",
                name: trimmed.replace("[DIR]", "").trim(),
            });
        } else if (trimmed.startsWith("[FILE]")) {
            entries.push({
                type: "file",
                name: trimmed.replace("[FILE]", "").trim(),
            });
        }
    }
    return entries;
}

function parseMultipleFilesResponse(text: string): Record<string, string> {
    const result: Record<string, string> = {};
    if (!text) return result;

    const lines = text.split("\n");
    let currentPath: string | null = null;
    const currentContent: string[] = [];

    for (const line of lines) {
        if (line.includes(":") && !currentPath) {
            const pathEnd = line.indexOf(":");
            const path = line.slice(0, pathEnd).trim();
            currentPath = path;
            const contentStart = line.slice(pathEnd + 1).trim();
            if (contentStart) currentContent.push(contentStart);
        } else if (line.trim() === "---") {
            if (currentPath) {
                result[currentPath] = currentContent.join("\n").trim();
                currentPath = null;
                currentContent.length = 0;
            }
        } else if (currentPath !== null) {
            currentContent.push(line);
        }
    }

    if (currentPath) {
        result[currentPath] = currentContent.join("\n").trim();
    }
    return result;
}

function parseFileChangeData(rawData: string): FileChangeEvent[] {
    const events: FileChangeEvent[] = [];
    try {
        const changeData = JSON.parse(rawData);
        if (Array.isArray(changeData)) {
            for (const eventDict of changeData) {
                if (eventDict && typeof eventDict === "object") {
                    const ev = eventDict as Record<string, string>;
                    events.push({
                        eventType: ev.eventType ?? ev.EventType ?? "",
                        path: ev.path ?? ev.Path ?? "",
                        pathType: ev.pathType ?? ev.PathType ?? "",
                    });
                }
            }
        }
    } catch {
        // ignore parse errors
    }
    return events;
}

/**
 * File system module for reading, writing, listing, and managing files in the session.
 * Supports text and binary files, directory listing, search, upload/download, and file change monitoring.
 */
export class FileSystem extends BaseService {
    static readonly DEFAULT_CHUNK_SIZE = DEFAULT_CHUNK_SIZE;
    private _fileTransfer?: FileTransfer;

    private _ensureFileTransfer(): FileTransfer {
        if (!this._fileTransfer) {
            const session = this.session as unknown as {
                getAgb(): {
                    apiKey: string;
                    client: import("../api/client").Client;
                    context: {
                        getFileUploadUrl(contextId: string, filePath: string): Promise<{
                            success: boolean; url: string; requestId?: string; errorMessage?: string;
                        }>;
                        getFileDownloadUrl(contextId: string, filePath: string): Promise<{
                            success: boolean; url: string; requestId?: string; errorMessage?: string;
                        }>;
                    };
                };
                getApiKey(): string;
                getSessionId(): string;
                context: {
                    sync(contextId?: string, path?: string, mode?: string): Promise<{
                        success: boolean; requestId?: string;
                    }>;
                    info(contextId?: string, path?: string, taskType?: string): Promise<{
                        success: boolean;
                        contextStatusData?: Array<{
                            contextId?: string; path?: string; taskType?: string;
                            status?: string; errorMessage?: string;
                        }>;
                    }>;
                };
            };
            const agb = session.getAgb();
            this._fileTransfer = new FileTransfer(agb, session);
        }
        return this._fileTransfer;
    }

    async createDirectory(path: string): Promise<BoolResult> {
        logOperationStart("FileSystem.createDirectory", `Path=${path}`);
        try {
            const result = await this.callMcpTool("create_directory", { path });
            if (result.success) {
                logOperationSuccess("FileSystem.createDirectory", `Path=${path}, RequestId=${result.requestId}`);
                return {
                    requestId: result.requestId,
                    success: true,
                    data: true,
                };
            }
            const errorMsg = result.errorMessage ?? "Unknown error";
            logOperationError("FileSystem.createDirectory", errorMsg);
            return {
                requestId: result.requestId,
                success: false,
                errorMessage: errorMsg,
            };
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileSystem.createDirectory", errMsg);
            return {
                requestId: "",
                success: false,
                errorMessage: `Failed to create directory: ${errMsg}`,
            };
        }
    }

    async deleteFile(path: string): Promise<BoolResult> {
        logOperationStart("FileSystem.deleteFile", `Path=${path}`);
        try {
            const result = await this.callMcpTool("delete_file", { path });
            if (result.success) {
                logOperationSuccess("FileSystem.deleteFile", `Path=${path}, RequestId=${result.requestId}`);
                return {
                    requestId: result.requestId,
                    success: true,
                    data: true,
                };
            }
            const errorMsg = result.errorMessage ?? "Failed to delete file";
            logOperationError("FileSystem.deleteFile", errorMsg);
            return {
                requestId: result.requestId,
                success: false,
                errorMessage: errorMsg,
            };
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileSystem.deleteFile", errMsg);
            return {
                requestId: "",
                success: false,
                errorMessage: `Failed to delete file: ${errMsg}`,
            };
        }
    }

    async editFile(
        path: string,
        edits: Array<{ oldText: string; newText: string }>,
        dryRun = false,
    ): Promise<BoolResult> {
        logOperationStart(
            "FileSystem.editFile",
            `Path=${path}, EditsCount=${edits.length}, DryRun=${dryRun}`,
        );
        try {
            const result = await this.callMcpTool("edit_file", {
                path,
                edits,
                dryRun,
            });
            if (result.success) {
                logOperationSuccess("FileSystem.editFile", `Path=${path}, RequestId=${result.requestId}`);
                return {
                    requestId: result.requestId,
                    success: true,
                    data: true,
                };
            }
            const errorMsg = result.errorMessage ?? "Unknown error";
            logOperationError("FileSystem.editFile", errorMsg);
            return {
                requestId: result.requestId,
                success: false,
                errorMessage: errorMsg,
            };
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileSystem.editFile", errMsg);
            return {
                requestId: "",
                success: false,
                errorMessage: `Failed to edit file: ${errMsg}`,
            };
        }
    }

    async getFileInfo(path: string): Promise<FileInfoResult> {
        logOperationStart("FileSystem.getFileInfo", `Path=${path}`);
        try {
            const result = await this.callMcpTool("get_file_info", { path });
            if (result.success) {
                const dataStr = typeof result.data === "string" ? result.data : String(result.data ?? "");
                const fileInfo = parseFileInfo(dataStr);
                logOperationSuccess(
                    "FileSystem.getFileInfo",
                    `Path=${path}, RequestId=${result.requestId}, IsDirectory=${fileInfo.isDirectory}`,
                );
                return {
                    requestId: result.requestId,
                    success: true,
                    fileInfo,
                };
            }
            const errorMsg = result.errorMessage ?? "Failed to get file info";
            logOperationError("FileSystem.getFileInfo", errorMsg);
            return {
                requestId: result.requestId,
                success: false,
                errorMessage: errorMsg,
            };
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileSystem.getFileInfo", errMsg);
            return {
                requestId: "",
                success: false,
                errorMessage: `Failed to get file info: ${errMsg}`,
            };
        }
    }

    async listDirectory(path: string): Promise<DirectoryListResult> {
        logOperationStart("FileSystem.listDirectory", `Path=${path}`);
        try {
            const result = await this.callMcpTool("list_directory", { path });
            if (result.success) {
                const dataStr = typeof result.data === "string" ? result.data : String(result.data ?? "");
                const entries = parseDirectoryListing(dataStr);
                logOperationSuccess(
                    "FileSystem.listDirectory",
                    `Path=${path}, EntriesCount=${entries.length}, RequestId=${result.requestId}`,
                );
                return {
                    requestId: result.requestId,
                    success: true,
                    entries,
                };
            }
            const errorMsg = result.errorMessage ?? "Failed to list directory";
            logOperationError("FileSystem.listDirectory", errorMsg);
            return {
                requestId: result.requestId,
                success: false,
                entries: [],
                errorMessage: errorMsg,
            };
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileSystem.listDirectory", errMsg);
            return {
                requestId: "",
                success: false,
                entries: [],
                errorMessage: `Failed to list directory: ${errMsg}`,
            };
        }
    }

    async moveFile(source: string, destination: string): Promise<BoolResult> {
        logOperationStart(
            "FileSystem.moveFile",
            `Source=${source}, Destination=${destination}`,
        );
        try {
            const result = await this.callMcpTool("move_file", {
                source,
                destination,
            });
            if (result.success) {
                logOperationSuccess(
                    "FileSystem.moveFile",
                    `Source=${source}, Destination=${destination}, RequestId=${result.requestId}`,
                );
                return {
                    requestId: result.requestId,
                    success: true,
                    data: true,
                };
            }
            const errorMsg = result.errorMessage ?? "Failed to move file";
            logOperationError("FileSystem.moveFile", errorMsg);
            return {
                requestId: result.requestId,
                success: false,
                errorMessage: errorMsg,
            };
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileSystem.moveFile", errMsg);
            return {
                requestId: "",
                success: false,
                errorMessage: `Failed to move file: ${errMsg}`,
            };
        }
    }

    private async readFileChunk(
        path: string,
        offset: number,
        length: number,
        formatType: "text" | "bytes",
    ): Promise<FileContentResult | BinaryFileContentResult> {
        const args: Record<string, unknown> = { path };
        if (offset >= 0) args.offset = offset;
        if (length >= 0) args.length = length;
        if (formatType === "bytes") args.format = "binary";

        const result = await this.callMcpTool("read_file", args);

        if (result.success) {
            const dataStr = typeof result.data === "string" ? result.data : String(result.data ?? "");
            if (formatType === "bytes") {
                try {
                    if (dataStr) {
                        const base64WithoutPadding = dataStr.replace(/=+$/, "");
                        if (!/^[A-Za-z0-9+/]*$/.test(base64WithoutPadding)) {
                            throw new Error("Invalid base64 string format");
                        }
                        const paddingMatch = dataStr.match(/=+$/);
                        if (paddingMatch && paddingMatch[0].length > 2) {
                            throw new Error("Invalid base64 padding format");
                        }
                    }
                    const binaryContent = Buffer.from(dataStr, "base64");
                    return {
                        requestId: result.requestId,
                        success: true,
                        content: binaryContent,
                    };
                } catch (e: unknown) {
                    const errMsg = e instanceof Error ? e.message : String(e);
                    return {
                        requestId: result.requestId ?? "",
                        success: false,
                        content: Buffer.alloc(0),
                        errorMessage: `Failed to decode base64: ${errMsg}`,
                    };
                }
            }
            return {
                requestId: result.requestId,
                success: true,
                content: dataStr,
            };
        }

        const errorMsg = result.errorMessage ?? "Failed to read file";
        if (formatType === "bytes") {
            return {
                requestId: result.requestId ?? "",
                success: false,
                content: Buffer.alloc(0),
                errorMessage: errorMsg,
            };
        }
        return {
            requestId: result.requestId ?? "",
            success: false,
            content: "",
            errorMessage: errorMsg,
        };
    }

    private async writeFileChunk(
        path: string,
        content: string,
        mode: "overwrite" | "append" | "create_new",
    ): Promise<BoolResult> {
        const validModes = ["overwrite", "append", "create_new"];
        if (!validModes.includes(mode)) {
            return {
                requestId: "",
                success: false,
                errorMessage: `Invalid write mode: ${mode}. Must be one of ${validModes.join(", ")}`,
            };
        }

        const result = await this.callMcpTool("write_file", {
            path,
            content,
            mode,
        });

        if (result.success) {
            return {
                requestId: result.requestId,
                success: true,
                data: true,
            };
        }
        return {
            requestId: result.requestId ?? "",
            success: false,
            errorMessage: result.errorMessage ?? "Failed to write file",
        };
    }

    async readFile(path: string): Promise<FileContentResult>;
    async readFile(path: string, opts: { format: "text" }): Promise<FileContentResult>;
    async readFile(path: string, opts: { format: "bytes" }): Promise<BinaryFileContentResult>;
    async readFile(
        path: string,
        opts?: { format?: "text" | "bytes" },
    ): Promise<FileContentResult | BinaryFileContentResult> {
        const format = opts?.format ?? "text";
        logOperationStart("FileSystem.readFile", `Path=${path}, Format=${format}`);
        try {
            const fileInfoResult = await this.getFileInfo(path);
            if (!fileInfoResult.success) {
                if (format === "bytes") {
                    return {
                        requestId: fileInfoResult.requestId,
                        success: false,
                        content: Buffer.alloc(0),
                        errorMessage: fileInfoResult.errorMessage,
                    };
                }
                return {
                    requestId: fileInfoResult.requestId,
                    success: false,
                    content: "",
                    errorMessage: fileInfoResult.errorMessage,
                };
            }

            const fileInfo = fileInfoResult.fileInfo;
            if (!fileInfo || fileInfo.isDirectory) {
                const errorMsg = `Path does not exist or is a directory: ${path}`;
                logOperationError("FileSystem.readFile", errorMsg);
                if (format === "bytes") {
                    return {
                        requestId: fileInfoResult.requestId,
                        success: false,
                        content: Buffer.alloc(0),
                        errorMessage: errorMsg,
                    };
                }
                return {
                    requestId: fileInfoResult.requestId,
                    success: false,
                    content: "",
                    errorMessage: errorMsg,
                };
            }

            const fileSize = fileInfo.size ?? 0;
            if (fileSize === 0) {
                if (format === "bytes") {
                    return {
                        requestId: fileInfoResult.requestId,
                        success: true,
                        content: Buffer.alloc(0),
                        size: 0,
                    };
                }
                return {
                    requestId: fileInfoResult.requestId,
                    success: true,
                    content: "",
                };
            }

            if (format === "bytes") {
                const contentChunks: Buffer[] = [];
                let offset = 0;
                while (offset < fileSize) {
                    const length = Math.min(DEFAULT_CHUNK_SIZE, fileSize - offset);
                    const chunkResult = await this.readFileChunk(
                        path,
                        offset,
                        length,
                        "bytes",
                    );
                    if (!chunkResult.success) return chunkResult;
                    contentChunks.push((chunkResult as BinaryFileContentResult).content);
                    offset += length;
                }
                const finalContent = Buffer.concat(contentChunks);
                logOperationSuccess(
                    "FileSystem.readFile",
                    `Path=${path}, Format=${format}, ContentLength=${finalContent.length}, RequestId=${fileInfoResult.requestId}`,
                );
                return {
                    requestId: fileInfoResult.requestId,
                    success: true,
                    content: finalContent,
                    size: finalContent.length,
                };
            }

            const contentChunks: string[] = [];
            let offset = 0;
            while (offset < fileSize) {
                const length = Math.min(DEFAULT_CHUNK_SIZE, fileSize - offset);
                const chunkResult = await this.readFileChunk(
                    path,
                    offset,
                    length,
                    "text",
                );
                if (!chunkResult.success) return chunkResult;
                contentChunks.push((chunkResult as FileContentResult).content);
                offset += length;
            }
            const contentStr = contentChunks.join("");
            logOperationSuccess(
                "FileSystem.readFile",
                `Path=${path}, Format=${format}, ContentLength=${contentStr.length}, RequestId=${fileInfoResult.requestId}`,
            );
            return {
                requestId: fileInfoResult.requestId,
                success: true,
                content: contentStr,
            };
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileSystem.readFile", errMsg);
            if (format === "bytes") {
                return {
                    requestId: "",
                    success: false,
                    content: Buffer.alloc(0),
                    errorMessage: errMsg,
                };
            }
            return {
                requestId: "",
                success: false,
                content: "",
                errorMessage: errMsg,
            };
        }
    }

    async writeFile(
        path: string,
        content: string,
        mode: "overwrite" | "append" | "create_new" = "overwrite",
    ): Promise<BoolResult> {
        const contentLen = content.length;
        logOperationStart(
            "FileSystem.writeFile",
            `Path=${path}, Mode=${mode}, ContentLength=${contentLen}`,
        );

        if (contentLen <= DEFAULT_CHUNK_SIZE) {
            return this.writeFileChunk(path, content, mode);
        }

        try {
            const firstChunk = content.slice(0, DEFAULT_CHUNK_SIZE);
            let result = await this.writeFileChunk(path, firstChunk, mode);
            if (!result.success) return result;

            let offset = DEFAULT_CHUNK_SIZE;
            while (offset < contentLen) {
                const end = Math.min(offset + DEFAULT_CHUNK_SIZE, contentLen);
                const currentChunk = content.slice(offset, end);
                result = await this.writeFileChunk(path, currentChunk, "append");
                if (!result.success) {
                    logOperationError(
                        "FileSystem.writeFile",
                        result.errorMessage ?? "Failed to write file chunk",
                    );
                    return result;
                }
                offset = end;
            }

            logOperationSuccess(
                "FileSystem.writeFile",
                `Path=${path}, ContentLength=${contentLen}, RequestId=${result.requestId}`,
            );
            return {
                requestId: result.requestId,
                success: true,
                data: true,
            };
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileSystem.writeFile", errMsg);
            return {
                requestId: "",
                success: false,
                errorMessage: `Failed to write file: ${errMsg}`,
            };
        }
    }

    async readMultipleFiles(paths: string[]): Promise<MultipleFileContentResult> {
        logOperationStart(
            "FileSystem.readMultipleFiles",
            `PathsCount=${paths.length}`,
        );
        try {
            const result = await this.callMcpTool("read_multiple_files", {
                paths,
            });
            if (result.success) {
                const dataStr = typeof result.data === "string" ? result.data : String(result.data ?? "");
                const files = parseMultipleFilesResponse(dataStr);
                logOperationSuccess(
                    "FileSystem.readMultipleFiles",
                    `RequestId=${result.requestId}, FilesCount=${Object.keys(files).length}`,
                );
                return {
                    requestId: result.requestId,
                    success: true,
                    files,
                };
            }
            return {
                requestId: result.requestId ?? "",
                success: false,
                files: {},
                errorMessage: result.errorMessage ?? "Failed to read multiple files",
            };
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileSystem.readMultipleFiles", errMsg);
            return {
                requestId: "",
                success: false,
                files: {},
                errorMessage: `Failed to read multiple files: ${errMsg}`,
            };
        }
    }

    async searchFiles(
        path: string,
        pattern: string,
        excludePatterns?: string[],
    ): Promise<FileSearchResult> {
        logOperationStart(
            "FileSystem.searchFiles",
            `Path=${path}, Pattern=${pattern}`,
        );
        try {
            const args: Record<string, unknown> = { path, pattern };
            if (excludePatterns && excludePatterns.length > 0) {
                args.excludePatterns = excludePatterns;
            }

            const result = await this.callMcpTool("search_files", args);
            if (result.success) {
                const dataStr = typeof result.data === "string" ? result.data : String(result.data ?? "");
                const trimmed = dataStr.trim();
                const matches =
                    trimmed && trimmed !== "No matches found"
                        ? trimmed.split("\n")
                        : [];
                logOperationSuccess(
                    "FileSystem.searchFiles",
                    `Path=${path}, MatchesCount=${matches.length}, RequestId=${result.requestId}`,
                );
                return {
                    requestId: result.requestId,
                    success: true,
                    matches,
                };
            }
            return {
                requestId: result.requestId ?? "",
                success: false,
                errorMessage: result.errorMessage ?? "Failed to search files",
            };
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileSystem.searchFiles", errMsg);
            return {
                requestId: "",
                success: false,
                errorMessage: `Failed to search files: ${errMsg}`,
            };
        }
    }

    async getFileChange(path: string): Promise<FileChangeResult> {
        logOperationStart("FileSystem.getFileChange", `Path=${path}`);
        try {
            const result = await this.callMcpTool("get_file_change", { path });
            if (result.success) {
                const dataStr = typeof result.data === "string" ? result.data : String(result.data ?? "");
                const events = parseFileChangeData(dataStr);
                logOperationSuccess(
                    "FileSystem.getFileChange",
                    `Path=${path}, EventsCount=${events.length}, RequestId=${result.requestId}`,
                );
                return {
                    requestId: result.requestId,
                    success: true,
                    events,
                    rawData: dataStr,
                };
            }
            return {
                requestId: result.requestId ?? "",
                success: false,
                events: [],
                rawData: "",
                errorMessage: result.errorMessage ?? "Failed to get file change",
            };
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("FileSystem.getFileChange", errMsg);
            return {
                requestId: "",
                success: false,
                events: [],
                rawData: "",
                errorMessage: `Failed to get file change: ${errMsg}`,
            };
        }
    }

    async transferPath(): Promise<string | undefined> {
        const ft = this._ensureFileTransfer();
        if (!ft.contextId) {
            const result = await ft.ensureContextId();
            if (!result.success) {
                logWarn(`Failed to ensure context_id: ${result.error}`);
                return undefined;
            }
        }
        return ft.contextPath;
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
        const ft = this._ensureFileTransfer();
        const result = await ft.upload(localPath, remotePath, options);

        if (result.success && ft.contextId) {
            try {
                const agb = (this.session as unknown as { getAgb(): { context: { deleteFile(cid: string, fp: string): Promise<{ success: boolean }> } } }).getAgb();
                const delResult = await agb.context.deleteFile(ft.contextId, remotePath);
                if (!delResult.success) {
                    logWarn(`Failed to delete uploaded file from OSS: contextId=${ft.contextId}, path=${remotePath}`);
                }
            } catch (e: unknown) {
                logWarn(`Error deleting uploaded file from OSS: ${e instanceof Error ? e.message : String(e)}`);
            }
        }

        return result;
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
        const ft = this._ensureFileTransfer();
        const result = await ft.download(remotePath, localPath, options);

        if (result.success && ft.contextId) {
            try {
                const agb = (this.session as unknown as { getAgb(): { context: { deleteFile(cid: string, fp: string): Promise<{ success: boolean }> } } }).getAgb();
                const delResult = await agb.context.deleteFile(ft.contextId, remotePath);
                if (!delResult.success) {
                    logWarn(`Failed to delete downloaded file from OSS: contextId=${ft.contextId}, path=${remotePath}`);
                }
            } catch (e: unknown) {
                logWarn(`Error deleting downloaded file from OSS: ${e instanceof Error ? e.message : String(e)}`);
            }
        }

        return result;
    }

    async watchDirectory(
        path: string,
        callback: (events: FileChangeEvent[]) => void,
        interval = 1000,
        signal?: AbortSignal,
    ): Promise<void> {
        while (!signal?.aborted) {
            try {
                const result = await this.getFileChange(path);
                if (result.success && result.events.length > 0) {
                    try {
                        callback(result.events);
                    } catch (e: unknown) {
                        logWarn(`Error in watchDirectory callback: ${e instanceof Error ? e.message : String(e)}`);
                    }
                } else if (!result.success) {
                    const errorMsg = (result.errorMessage ?? "").toLowerCase();
                    if (errorMsg.includes("session") && (errorMsg.includes("expired") || errorMsg.includes("invalid"))) {
                        break;
                    }
                }
            } catch (e: unknown) {
                const errorStr = String(e).toLowerCase();
                if (errorStr.includes("session") && (errorStr.includes("expired") || errorStr.includes("invalid"))) {
                    break;
                }
            }
            await new Promise<void>((resolve) => {
                const timeoutId = setTimeout(resolve, interval);
                signal?.addEventListener("abort", () => {
                    clearTimeout(timeoutId);
                    resolve();
                }, { once: true });
            });
        }
    }

    /** @deprecated Use watchDirectory instead */
    watchDir(
        dirPath: string,
        callback: (events: FileChangeEvent[]) => void,
        interval = 1000,
    ): { stop: () => void } {
        const controller = new AbortController();
        this.watchDirectory(dirPath, callback, interval, controller.signal);
        return { stop: () => controller.abort() };
    }

    // Aliases
    read(path: string): Promise<FileContentResult>;
    read(path: string, opts: { format: "text" }): Promise<FileContentResult>;
    read(path: string, opts: { format: "bytes" }): Promise<BinaryFileContentResult>;
    read(path: string, opts?: { format?: "text" | "bytes" }): Promise<FileContentResult | BinaryFileContentResult> {
        return this.readFile(path, opts as any);
    }
    write = this.writeFile.bind(this);
    list = this.listDirectory.bind(this);
    ls = this.listDirectory.bind(this);
    delete = this.deleteFile.bind(this);
    remove = this.deleteFile.bind(this);
    rm = this.deleteFile.bind(this);
    mkdir = this.createDirectory.bind(this);
}
