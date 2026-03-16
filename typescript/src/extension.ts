import * as fs from "fs";
import * as path from "path";
import * as crypto from "crypto";
import { AGBError } from "./exceptions";
import { logInfo, logError } from "./logger";
import { Context } from "./context";
import type { ContextService } from "./context";
import type { ContextFileEntry } from "./types/api-response";

// ==============================================================================
// Constants
// ==============================================================================
const EXTENSIONS_BASE_PATH = "/tmp/extensions";

// ==============================================================================
// 1. Data Models
// ==============================================================================
interface FileSystemError extends Error {
    code?: string;
}

/**
 * Represents a browser extension as a cloud resource.
 */
export class Extension {
    /**
     * The unique identifier of the extension.
     */
    id: string;

    /**
     * The name of the extension.
     */
    name: string;

    /**
     * Date and time when the extension was created.
     */
    createdAt?: string;

    /**
     * Initialize an Extension object.
     *
     * @param id - The unique identifier of the extension.
     * @param name - The name of the extension.
     * @param createdAt - Date and time when the extension was created.
     */
    constructor(id: string, name: string, createdAt?: string) {
        this.id = id;
        this.name = name;
        this.createdAt = createdAt;
    }
}

/**
 * Configuration options for browser extension integration.
 *
 * This class encapsulates the necessary parameters for setting up
 * browser extension synchronization and context management.
 */
export class ExtensionOption {
    /**
     * ID of the extension context for browser extensions.
     */
    contextId: string;

    /**
     * List of extension IDs to be loaded/synchronized.
     */
    extensionIds: string[];

    /**
     * Initialize ExtensionOption with context and extension configuration.
     *
     * @param contextId - ID of the extension context for browser extensions.
     *                   This should match the context where extensions are stored.
     * @param extensionIds - List of extension IDs to be loaded in the browser session.
     *                      Each ID should correspond to a valid extension in the context.
     *
     * @throws {Error} If contextId is empty or extensionIds is empty.
     */
    constructor(contextId: string, extensionIds: string[]) {
        if (!contextId?.trim()) {
            throw new Error("contextId cannot be empty");
        }
        if (!extensionIds?.length) {
            throw new Error("extensionIds cannot be empty");
        }
        this.contextId = contextId;
        this.extensionIds = extensionIds;
    }

    /**
     * String representation of ExtensionOption.
     */
    toString(): string {
        return `ExtensionOption(contextId='${this.contextId}', extensionIds=${JSON.stringify(this.extensionIds)})`;
    }

    /**
     * Human-readable string representation.
     */
    toDisplayString(): string {
        return `Extension Config: ${this.extensionIds.length} extension(s) in context '${this.contextId}'`;
    }

    /**
     * Validate the extension option configuration.
     *
     * @returns True if configuration is valid, false otherwise.
     */
    validate(): boolean {
        try {
            if (!this.contextId?.trim()) return false;
            if (!this.extensionIds?.length) return false;
            for (const extId of this.extensionIds) {
                if (typeof extId !== "string" || !extId.trim()) {
                    return false;
                }
            }
            return true;
        } catch {
            return false;
        }
    }
}

// ==============================================================================
// 2. Core Service Class (Scoped Stateless Model)
// ==============================================================================

export interface AGBLikeForExtensions {
    apiKey: string;
    context: ContextService;
}

/**
 * Provides methods to manage user browser extensions.
 * This service integrates with the existing context functionality for file operations.
 *
 * **Usage** (Simplified - Auto-detection):
 * ```typescript
 * // Service automatically detects if context exists and creates if needed
 * const extensionsService = new ExtensionsService(agb, "browser_extensions");
 *
 * // Or use with empty contextId to auto-generate context name
 * const extensionsService = new ExtensionsService(agb);  // Uses default generated name
 *
 * // Use the service immediately - initialization happens automatically
 * const extension = await extensionsService.create("/path/to/plugin.zip");
 * ```
 *
 * **Integration with ExtensionOption (Simplified)**:
 * ```typescript
 * // Create extensions and configure for browser sessions
 * const extensionsService = new ExtensionsService(agb, "my_extensions");
 * const ext1 = await extensionsService.create("/path/to/ext1.zip");
 * const ext2 = await extensionsService.create("/path/to/ext2.zip");
 *
 * // Create extension option for browser integration (no contextId needed!)
 * const extOption = extensionsService.createExtensionOption([ext1.id, ext2.id]);
 *
 * // Use with BrowserContext for session creation
 * const browserContext = new BrowserContext({
 *   contextId: "browser_session",
 *   autoUpload: true,
 *   extensionOption: extOption  // All extension config encapsulated
 * });
 * ```
 *
 * **Context Management**:
 * - If contextId provided and exists: Uses the existing context
 * - If contextId provided but doesn't exist: Creates context with provided name
 * - If contextId empty or not provided: Generates default name and creates context
 * - No need to manually manage context creation or call initialize()
 * - Context initialization happens automatically on first method call
 */
export class ExtensionsService {
    private agb: AGBLikeForExtensions;
    private contextService: ContextService;
    private extensionContext!: Context;
    private _contextId!: string;
    private contextName: string;
    private autoCreated: boolean;
    private _initializationPromise: Promise<void> | null = null;

    get contextId(): string {
        return this._contextId;
    }

    /**
     * Initializes the ExtensionsService with a context.
     *
     * @param agb - The AGB client instance.
     * @param contextId - The context ID or name. If empty or not provided,
     *                   a default context name will be generated automatically.
     *                   If the context doesn't exist, it will be automatically created.
     *
     * Note:
     *   The service automatically detects if the context exists. If not,
     *   it creates a new context with the provided name or a generated default name.
     *   Context initialization is handled lazily on first use.
     */
    constructor(agb: AGBLikeForExtensions, contextId = "") {
        if (!agb) {
            throw new AGBError("AGB instance is required");
        }
        if (!agb.context) {
            throw new AGBError("AGB instance must have a context service");
        }

        this.agb = agb;
        this.contextService = agb.context;
        this.autoCreated = true;

        if (!contextId || contextId.trim() === "") {
            contextId = `extensions-${Math.floor(Date.now() / 1000)}`;
        }

        this.contextName = contextId;
        this._initializationPromise = this._initializeContext();
    }

    /**
     * Internal method to initialize the context.
     * This ensures the context is ready before any operations.
     */
    private async _initializeContext(): Promise<void> {
        try {
            const contextResult = await this.contextService.get(
                this.contextName,
                true,
            );
            if (!contextResult.success || !contextResult.context) {
                throw new AGBError(
                    `Failed to create extension repository context: ${this.contextName}`,
                );
            }
            this.extensionContext = contextResult.context;
            this._contextId = this.extensionContext.id;
        } catch (error) {
            if (error instanceof AGBError) {
                throw error;
            }
            throw new AGBError(
                `Failed to initialize ExtensionsService: ${error instanceof Error ? error.message : String(error)}`,
            );
        }
    }

    /**
     * Ensures the service is initialized before performing operations.
     */
    private async _ensureInitialized(): Promise<void> {
        if (this._initializationPromise) {
            await this._initializationPromise;
            this._initializationPromise = null;
        }
    }

    /**
     * An internal helper method that encapsulates the flow of
     * "get upload URL for a specific path and upload".
     * Uses the existing context service for file operations.
     *
     * @param localPath - The path to the local file.
     * @param remotePath - The path of the file in context storage.
     *
     * @throws {AGBError} If getting the credential or uploading fails.
     */
    private async _uploadToCloud(
        localPath: string,
        remotePath: string,
    ): Promise<void> {
        try {
            const urlResult = await this.contextService.getFileUploadUrl(
                this._contextId,
                remotePath,
            );
            if (!urlResult.success || !urlResult.url) {
                throw new AGBError(
                    `Failed to get upload URL: ${urlResult.errorMessage || "No URL returned"}`,
                );
            }

            logInfo(`Uploading file to OSS: ${localPath} -> ${remotePath}`);
            const fileBuffer = await fs.promises.readFile(localPath);
            const response = await fetch(urlResult.url, {
                method: "PUT",
                body: fileBuffer,
                signal: AbortSignal.timeout(120_000),
            });

            if (!response.ok) {
                const body = await response.text().catch(() => "");
                throw new AGBError(
                    `HTTP error uploading file: ${response.status} ${response.statusText} ${body}`,
                );
            }
            logInfo(`Successfully uploaded file to OSS: ${remotePath}`);
        } catch (error) {
            if (error instanceof AGBError) {
                throw error;
            }

            if (error instanceof Error && "code" in error) {
                const errorCode = (error as FileSystemError).code;
                if (errorCode === "ENOENT") {
                    throw new AGBError(`File not found: ${localPath}`);
                } else if (errorCode === "EACCES") {
                    throw new AGBError(
                        `Permission denied accessing file: ${localPath}`,
                    );
                } else {
                    throw new AGBError(`File system error: ${error.message}`);
                }
            }

            if (
                error instanceof TypeError &&
                error.message.includes("fetch")
            ) {
                throw new AGBError(
                    `Network error during file upload: ${error.message}`,
                );
            }

            throw new AGBError(
                `An error occurred while uploading the file: ${error instanceof Error ? error.message : String(error)}`,
            );
        }
    }

    /**
     * Lists all available browser extensions within this context from the cloud.
     * Uses the context service to list files under the extensions directory.
     *
     * @returns Promise that resolves to an array of Extension objects.
     * @throws {AGBError} If listing extensions fails.
     *
     * @example
     * ```typescript
     * const agb = new AGB({ apiKey: 'your_api_key' });
     * const service = new ExtensionsService(agb, 'my_extensions');
     * await service.create('/path/to/ext1.zip');
     * const extensions = await service.list();
     * console.log(`Found ${extensions.length} extensions`);
     * await service.cleanup();
     * ```
     */
    async list(): Promise<Extension[]> {
        await this._ensureInitialized();

        try {
            const fileListResult = await this.contextService.listFiles(
                this._contextId,
                EXTENSIONS_BASE_PATH,
                1,
                100,
            );

            if (!fileListResult.success) {
                throw new AGBError(
                    "Failed to list extensions: Context file listing failed.",
                );
            }

            const extensions: Extension[] = [];
            for (const fileEntry of fileListResult.files) {
                const extensionId = fileEntry.name || fileEntry.path;
                extensions.push(
                    new Extension(
                        extensionId,
                        fileEntry.name || extensionId,
                        fileEntry.createdTime,
                    ),
                );
            }
            return extensions;
        } catch (error) {
            if (error instanceof AGBError) {
                throw error;
            }
            throw new AGBError(
                `An error occurred while listing browser extensions: ${error instanceof Error ? error.message : String(error)}`,
            );
        }
    }

    /**
     * Uploads a new browser extension from a local path into the current context.
     *
     * @param localPath - Path to the local extension file (must be a .zip file).
     * @returns Promise that resolves to an Extension object.
     * @throws {Error} If the local file doesn't exist.
     * @throws {Error} If the file format is not supported (only .zip is supported).
     * @throws {AGBError} If upload fails.
     *
     * @example
     * ```typescript
     * const agb = new AGB({ apiKey: 'your_api_key' });
     * const service = new ExtensionsService(agb);
     * const extension = await service.create('/path/to/my-extension.zip');
     * console.log(`Extension ID: ${extension.id}`);
     * await service.cleanup();
     * ```
     */
    async create(localPath: string): Promise<Extension> {
        await this._ensureInitialized();

        if (!fs.existsSync(localPath)) {
            throw new Error(
                `The specified local file was not found: ${localPath}`,
            );
        }

        const fileExtension = path.extname(localPath).toLowerCase();
        if (fileExtension !== ".zip") {
            throw new Error(
                `Unsupported plugin format '${fileExtension}'. Only ZIP format (.zip) is supported.`,
            );
        }

        const extensionId = `ext_${crypto.randomUUID().replace(/-/g, "")}${fileExtension}`;
        const extensionName = path.basename(localPath);
        const remotePath = `${EXTENSIONS_BASE_PATH}/${extensionId}`;

        await this._uploadToCloud(localPath, remotePath);
        return new Extension(extensionId, extensionName);
    }

    /**
     * Updates an existing browser extension in the current context with a new file.
     *
     * @param extensionId - ID of the extension to update.
     * @param newLocalPath - Path to the new local extension file.
     * @returns Promise that resolves to an Extension object.
     * @throws {Error} If the new local file doesn't exist.
     * @throws {Error} If the extension doesn't exist in the context.
     * @throws {AGBError} If update fails.
     *
     * @example
     * ```typescript
     * const agb = new AGB({ apiKey: 'your_api_key' });
     * const service = new ExtensionsService(agb, 'my_extensions');
     * const ext = await service.create('/path/to/ext-v1.zip');
     * const updated = await service.update(ext.id, '/path/to/ext-v2.zip');
     * console.log('Extension updated:', updated.name);
     * await service.cleanup();
     * ```
     */
    async update(
        extensionId: string,
        newLocalPath: string,
    ): Promise<Extension> {
        await this._ensureInitialized();

        if (!fs.existsSync(newLocalPath)) {
            throw new Error(
                `The specified new local file was not found: ${newLocalPath}`,
            );
        }

        const existingExtensions = await this.list();
        if (!existingExtensions.some((ext) => ext.id === extensionId)) {
            throw new Error(
                `Browser extension with ID '${extensionId}' not found in the context. Cannot update.`,
            );
        }

        const remotePath = `${EXTENSIONS_BASE_PATH}/${extensionId}`;
        await this._uploadToCloud(newLocalPath, remotePath);
        return new Extension(extensionId, path.basename(newLocalPath));
    }

    /**
     * Gets detailed information about a specific browser extension.
     *
     * @param extensionId - The ID of the extension to get info for.
     * @returns Promise that resolves to an Extension object if found, undefined otherwise.
     */
    private async _getExtensionInfo(
        extensionId: string,
    ): Promise<Extension | undefined> {
        await this._ensureInitialized();

        try {
            const extensions = await this.list();
            return extensions.find((ext) => ext.id === extensionId);
        } catch (error) {
            logError(
                `An error occurred while getting extension info for '${extensionId}': ${error instanceof Error ? error.message : String(error)}`,
            );
            return undefined;
        }
    }

    /**
     * Cleans up the auto-created context if it was created by this service.
     *
     * @returns Promise that resolves to true if cleanup was successful or not needed,
     *          false if cleanup failed.
     *
     * Note:
     *   This method only works if the context was auto-created by this service.
     *   For existing contexts, no cleanup is performed.
     *
     * @example
     * ```typescript
     * const agb = new AGB({ apiKey: 'your_api_key' });
     * const service = new ExtensionsService(agb);
     * await service.create('/path/to/my-extension.zip');
     * const success = await service.cleanup();
     * console.log('Cleanup success:', success);
     * ```
     */
    async cleanup(): Promise<boolean> {
        await this._ensureInitialized();

        if (!this.autoCreated) {
            return true;
        }

        try {
            const deleteResult = await this.contextService.delete(
                this.extensionContext,
            );
            if (deleteResult.success) {
                logInfo(
                    `Extension context deleted: ${this.contextName} (ID: ${this._contextId})`,
                );
                return true;
            }
            logError(
                `Failed to delete extension context: ${this.contextName}`,
            );
            return false;
        } catch (error) {
            logError(
                `Failed to delete extension context: ${error instanceof Error ? error.message : String(error)}`,
            );
            return false;
        }
    }

    /**
     * Deletes a browser extension from the current context.
     *
     * @param extensionId - ID of the extension to delete.
     * @returns Promise that resolves to true if deletion was successful, false otherwise.
     *
     * @example
     * ```typescript
     * const agb = new AGB({ apiKey: 'your_api_key' });
     * const service = new ExtensionsService(agb, 'my_extensions');
     * const ext = await service.create('/path/to/my-extension.zip');
     * const success = await service.delete(ext.id);
     * console.log('Delete success:', success);
     * await service.cleanup();
     * ```
     */
    async delete(extensionId: string): Promise<boolean> {
        await this._ensureInitialized();

        const remotePath = `${EXTENSIONS_BASE_PATH}/${extensionId}`;
        try {
            const deleteResult = await this.contextService.deleteFile(
                this._contextId,
                remotePath,
            );
            return deleteResult.success;
        } catch (error) {
            logError(
                `An error occurred while deleting browser extension '${extensionId}': ${error instanceof Error ? error.message : String(error)}`,
            );
            return false;
        }
    }

    /**
     * Create an ExtensionOption for the current context with specified extension IDs.
     *
     * This is a convenience method that creates an ExtensionOption using the current
     * service's contextId and the provided extension IDs. This option can then be
     * used with BrowserContext for browser session creation.
     *
     * @param extensionIds - List of extension IDs to include in the option.
     *                      These should be extensions that exist in the current context.
     * @returns ExtensionOption configuration object for browser extension integration.
     * @throws {Error} If extensionIds is empty or invalid.
     *
     * @example
     * ```typescript
     * // Create extensions
     * const ext1 = await extensionsService.create("/path/to/ext1.zip");
     * const ext2 = await extensionsService.create("/path/to/ext2.zip");
     *
     * // Create extension option for browser integration
     * const extOption = extensionsService.createExtensionOption([ext1.id, ext2.id]);
     *
     * // Use with BrowserContext
     * const browserContext = new BrowserContext({
     *   contextId: "browser_session",
     *   autoUpload: true,
     *   extensionContextId: extOption.contextId,
     *   extensionIds: extOption.extensionIds
     * });
     * ```
     */
    createExtensionOption(extensionIds: string[]): ExtensionOption {
        if (!this._contextId) {
            throw new Error(
                "Service not initialized. Please call an async method first or ensure context is created.",
            );
        }
        return new ExtensionOption(this._contextId, extensionIds);
    }
}
