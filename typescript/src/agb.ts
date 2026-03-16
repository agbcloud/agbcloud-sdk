import { Client } from "./api/client";
import {
    CreateSessionRequest,
    CreateMcpSessionRequestPersistenceDataList,
    GetSessionRequest,
    ListSessionRequest,
} from "./api/models";
import { Config, ConfigOptions, loadConfig } from "./config";
import {
    ContextSync,
    WhiteList,
    BWList,
    UploadPolicy,
    RecyclePolicy,
    SyncPolicy,
    newSyncPolicy,
    syncPolicyToDict,
} from "./context-sync";
import { ContextService } from "./context";
import { AuthenticationError } from "./exceptions";
import {
    logOperationStart,
    logOperationSuccess,
    logOperationError,
    logInfo,
    logWarn,
    logDebug,
} from "./logger";
import type {
    SessionResult,
    DeleteResult,
    GetSessionResult,
    GetSessionData,
    SessionListResult,
} from "./types/api-response";
import { Session } from "./session";
import type { CreateSessionParams } from "./session-params";
import { getSdkVersion, isReleaseVersion } from "./version";

const BROWSER_DATA_PATH = "/tmp/agb_browser_data";

/**
 * Options for initializing the AGB client.
 */
export interface AGBOptions {
    /** API key for authentication. If not provided, will use AGB_API_KEY environment variable. */
    apiKey?: string;
    /** Custom configuration. If not provided, uses environment-based configuration. */
    config?: ConfigOptions;
    /** Custom path to .env file. If not provided, searches upward from current directory. */
    envFile?: string;
}

/**
 * Main class for interacting with the AGB cloud runtime environment.
 * Use this class to create, list, and manage sessions.
 */
export class AGB {
    apiKey: string;
    config: Config;
    client: Client;
    /** Context service for managing persistent contexts. */
    context: ContextService;

    /**
     * Initialize the AGB client.
     *
     * @param options - Configuration options, or a string API key
     * @param options.apiKey - API key for authentication. If not provided, will use AGB_API_KEY environment variable.
     * @param options.config - Custom configuration object. If not provided, will use environment-based configuration.
     * @param options.envFile - Custom path to .env file. If not provided, will search upward from current directory.
     */
    constructor(options?: AGBOptions | string) {
        let apiKey: string;
        let cfgOptions: ConfigOptions | undefined;
        let envFile: string | undefined;

        if (typeof options === "string") {
            apiKey = options;
        } else {
            apiKey = options?.apiKey ?? "";
            cfgOptions = options?.config;
            envFile = options?.envFile;
        }

        if (!apiKey) {
            const envKey = process.env.AGB_API_KEY;
            if (!envKey) {
                throw new AuthenticationError(
                    "API key is required. Provide it as a parameter or set the AGB_API_KEY environment variable",
                );
            }
            apiKey = envKey;
        }

        this.config = loadConfig(cfgOptions, envFile);
        this.apiKey = apiKey;
        this.client = new Client(this.config);
        this.context = new ContextService(this);
    }

    /**
     * Serialize client configuration to a plain object.
     *
     * @returns Object with endpoint and timeoutMs
     */
    toJSON(): Record<string, unknown> {
        return {
            endpoint: this.config.endpoint,
            timeoutMs: this.config.timeoutMs,
        };
    }

    private normalizeContextSyncs(params: CreateSessionParams): ContextSync[] {
        const BROWSER_WHITELIST_PATHS: WhiteList[] = [
            { path: "/Local State", excludePaths: [] },
            { path: "/Default/Cookies", excludePaths: [] },
            { path: "/Default/Cookies-journal", excludePaths: [] },
        ];

        function createBrowserSyncPolicy(autoUpload: boolean): SyncPolicy {
            return newSyncPolicy({
                uploadPolicy: { autoUpload, uploadStrategy: "UploadBeforeResourceRelease" as any, uploadMode: "File" as any },
                bwList: { whiteLists: BROWSER_WHITELIST_PATHS } as BWList,
                recyclePolicy: { lifecycle: "Lifecycle_Forever" as any, paths: [""] },
            });
        }

        const syncs: ContextSync[] = [...(params.contextSync || [])];

        if (params.browserContext) {
            syncs.push(
                new ContextSync(
                    params.browserContext.contextId,
                    BROWSER_DATA_PATH,
                    createBrowserSyncPolicy(params.browserContext.autoUpload),
                ),
            );
        }

        return syncs;
    }

    private createPersistenceDataList(
        contextSyncs: ContextSync[],
    ): CreateMcpSessionRequestPersistenceDataList[] {
        const list: CreateMcpSessionRequestPersistenceDataList[] = [];
        for (const cs of contextSyncs) {
            if (cs.policy) {
                const policyJson = JSON.stringify(syncPolicyToDict(cs.policy));
                list.push(
                    new CreateMcpSessionRequestPersistenceDataList(
                        cs.contextId,
                        cs.path,
                        policyJson,
                    ),
                );
            }
        }
        return list;
    }

    /**
     * Create a new session in the AGB cloud environment.
     *
     * @param params - Parameters for creating the session (imageId is required)
     * @returns Promise resolving to SessionResult with success, session, requestId, and optional errorMessage
     *
     * @example
     * ```typescript
     * const agb = new AGB({ apiKey: 'your_api_key' });
     * const result = await agb.create({ imageId: 'agb-code-space-1' });
     * if (result.success && result.session) {
     *   await result.session.file.readFile('/etc/hostname');
     *   await agb.delete(result.session);
     * }
     * ```
     */
    async create(
        params?: CreateSessionParams | null,
    ): Promise<SessionResult> {
        try {
            if (!params) {
                const errorMessage = "params is required and cannot be null";
                logOperationError("AGB.create", errorMessage);
                return { requestId: "", success: false, errorMessage };
            }

            if (!params.imageId?.trim()) {
                const errorMessage =
                    "imageId is required and cannot be empty or null";
                logOperationError("AGB.create", errorMessage);
                return { requestId: "", success: false, errorMessage };
            }

            logOperationStart(
                "AGB.create",
                `ImageId=${params.imageId}`,
            );

            const request = new CreateSessionRequest(
                `Bearer ${this.apiKey}`,
                undefined,
                params.imageId,
            );

            if (params.policyId) {
                request.mcpPolicyId = params.policyId;
            }

            if (params.idleReleaseTimeout !== undefined) {
                request.timeout = params.idleReleaseTimeout;
            }

            if (params.labels) {
                request.labels = JSON.stringify(params.labels);
            }

            request.sdkStats = {
                source: "sdk",
                sdk_language: "typescript",
                sdk_version: getSdkVersion(),
                is_release: isReleaseVersion(),
            };

            let needsContextSync = false;
            const syncs = this.normalizeContextSyncs(params);
            const persistenceDataList = this.createPersistenceDataList(syncs);
            if (persistenceDataList.length > 0) {
                request.persistenceDataList = persistenceDataList;
                needsContextSync = true;
            }

            const response = await this.client.createMcpSession(request);
            const requestId = response.requestId ?? "";

            if (response.getData()?.success === false) {
                const errorMessage =
                    response.getData()?.errMsg ?? "Unknown error";
                logOperationError("AGB.create", errorMessage);
                return { requestId, success: false, errorMessage };
            }

            const sessionId = response.getSessionId();
            if (!sessionId) {
                const errorMessage =
                    response.getErrorMessage() ||
                    "Session ID not found in response";
                logOperationError("AGB.create", errorMessage);
                return { requestId, success: false, errorMessage };
            }

            const resourceUrl = response.getResourceUrl() ?? "";

            logInfo(`session_id = ${sessionId}`);
            logInfo(`resource_url = ${resourceUrl}`);

            const session = new Session(this, sessionId);
            session.resourceUrl = resourceUrl;
            session.imageId = params.imageId || "";

            const data = response.getData();
            if (data) {
                session.appInstanceId = data.appInstanceId ?? "";
                session.resourceId = data.resourceId ?? "";
            }

            if (needsContextSync) {
                await this.waitForContextSynchronization(session);
            }

            logOperationSuccess(
                "AGB.create",
                `SessionId=${sessionId}, RequestId=${requestId}`,
            );
            return { requestId, success: true, session };
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("AGB.create", errMsg);
            return {
                requestId: "",
                success: false,
                errorMessage: `Failed to create session: ${errMsg}`,
            };
        }
    }

    private async waitForContextSynchronization(
        session: Session,
        maxRetries = 150,
        retryIntervalS = 2,
    ): Promise<void> {
        logOperationStart("Context synchronization", "Waiting for completion");
        const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

        for (let retry = 0; retry < maxRetries; retry++) {
            const infoResult = await session.context.info();

            let allCompleted = true;
            let hasFailure = false;

            for (const item of infoResult.items) {
                logDebug(
                    `Context ${item.contextId} status: ${item.status}, path: ${item.path}`,
                );
                if (item.status !== "Success" && item.status !== "Failed") {
                    allCompleted = false;
                    break;
                }
                if (item.status === "Failed") {
                    hasFailure = true;
                }
            }

            if (allCompleted || infoResult.items.length === 0) {
                if (hasFailure) {
                    logWarn("Context synchronization completed with failures");
                } else {
                    logOperationSuccess("Context synchronization");
                }
                return;
            }

            logDebug(
                `Waiting for context synchronization, attempt ${retry + 1}/${maxRetries}`,
            );
            await sleep(retryIntervalS * 1000);
        }
    }

    /**
     * List sessions filtered by labels with pagination.
     *
     * @param labels - Optional key-value pairs to filter sessions
     * @param page - Page number (1-based). If provided, fetches that page.
     * @param limit - Maximum number of sessions per page (default 10)
     * @returns Promise resolving to SessionListResult with sessionIds, nextToken, totalCount, etc.
     */
    async list(
        labels?: Record<string, string>,
        page?: number,
        limit?: number,
    ): Promise<SessionListResult> {
        try {
            const effectiveLabels = labels ?? {};
            const effectiveLimit = limit ?? 10;

            logOperationStart(
                "AGB.list",
                `Page=${page ?? 1}, Limit=${effectiveLimit}`,
            );

            if (page !== undefined && page < 1) {
                const errorMessage = `Cannot reach page ${page}: Page number must be >= 1`;
                logOperationError("AGB.list", errorMessage);
                return {
                    requestId: "",
                    success: false,
                    errorMessage,
                    sessionIds: [],
                    nextToken: "",
                    maxResults: effectiveLimit,
                    totalCount: 0,
                };
            }

            let nextToken = "";
            if (page !== undefined && page > 1) {
                let currentPage = 1;
                while (currentPage < page) {
                    const req = new ListSessionRequest(
                        `Bearer ${this.apiKey}`,
                        effectiveLimit,
                        nextToken || undefined,
                        JSON.stringify(effectiveLabels),
                    );
                    const resp = await this.client.listSessions(req);
                    if (!resp.isSuccessful()) {
                        const errorMessage = `Cannot reach page ${page}: ${resp.getErrorMessage()}`;
                        return {
                            requestId: resp.requestId ?? "",
                            success: false,
                            errorMessage,
                            sessionIds: [],
                            nextToken: "",
                            maxResults: effectiveLimit,
                            totalCount: 0,
                        };
                    }
                    nextToken = resp.getNextToken() ?? "";
                    if (!nextToken) {
                        return {
                            requestId: resp.requestId ?? "",
                            success: false,
                            errorMessage: `Cannot reach page ${page}: No more pages available`,
                            sessionIds: [],
                            nextToken: "",
                            maxResults: effectiveLimit,
                            totalCount: resp.getCount() ?? 0,
                        };
                    }
                    currentPage++;
                }
            }

            const request = new ListSessionRequest(
                `Bearer ${this.apiKey}`,
                effectiveLimit,
                nextToken || undefined,
                JSON.stringify(effectiveLabels),
            );

            const response = await this.client.listSessions(request);
            const requestId = response.requestId ?? "";

            if (!response.isSuccessful()) {
                const errorMessage =
                    response.getErrorMessage() || "Unknown error";
                logOperationError("AGB.list", errorMessage);
                return {
                    requestId,
                    success: false,
                    errorMessage,
                    sessionIds: [],
                    nextToken: "",
                    maxResults: effectiveLimit,
                    totalCount: 0,
                };
            }

            const sessionIds: string[] = [];
            const sessionDataList = response.getSessionData();
            for (const sd of sessionDataList) {
                if (sd.sessionId) {
                    sessionIds.push(sd.sessionId);
                }
            }

            logOperationSuccess(
                "AGB.list",
                `RequestId=${requestId}, Count=${sessionIds.length}`,
            );

            return {
                requestId,
                success: true,
                sessionIds,
                nextToken: response.getNextToken() ?? "",
                maxResults: response.getMaxResults() ?? effectiveLimit,
                totalCount: response.getCount() ?? 0,
            };
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("AGB.list", errMsg);
            return {
                requestId: "",
                success: false,
                errorMessage: `Failed to list sessions: ${errMsg}`,
                sessionIds: [],
                nextToken: "",
                maxResults: 0,
                totalCount: 0,
            };
        }
    }

    /**
     * Delete (release) a session.
     *
     * @param session - The session to delete
     * @param syncContext - If true, sync context before releasing (e.g. upload browser data)
     * @returns Promise resolving to DeleteResult with success and requestId
     */
    async delete(
        session: Session,
        syncContext = false,
    ): Promise<DeleteResult> {
        logOperationStart(
            "AGB.delete",
            `SessionId=${session.getSessionId()}, SyncContext=${syncContext}`,
        );
        try {
            const result = await session.delete(syncContext);
            if (result.success) {
                logOperationSuccess(
                    "AGB.delete",
                    `SessionId=${session.getSessionId()}`,
                );
            } else {
                logOperationError(
                    "AGB.delete",
                    result.errorMessage || "Unknown error",
                );
            }
            return result;
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("AGB.delete", errMsg);
            return {
                requestId: "",
                success: false,
                errorMessage: `Failed to delete session: ${errMsg}`,
            };
        }
    }

    /**
     * Get session details by session ID (raw API result).
     *
     * @param sessionId - The session ID to look up
     * @returns Promise resolving to GetSessionResult with session data or error
     */
    async getSession(sessionId: string): Promise<GetSessionResult> {
        logOperationStart("AGB.getSession", `SessionId=${sessionId}`);
        try {
            const request = new GetSessionRequest(
                `Bearer ${this.apiKey}`,
                sessionId,
            );
            const response = await this.client.getMcpSession(request);
            const requestId = response.requestId ?? "";
            const success = response.isSuccessful();

            if (!success) {
                const errorMessage =
                    response.getErrorMessage() || "Unknown error";
                logWarn(`AGB.getSession: ${errorMessage}`);
                return {
                    requestId,
                    httpStatusCode: response.statusCode,
                    code: response.code ?? "",
                    success: false,
                    errorMessage,
                };
            }

            const data = response.getData();
            let sessionData: GetSessionData | undefined;
            if (data) {
                sessionData = {
                    appInstanceId: data.appInstanceId ?? "",
                    resourceId: data.resourceId ?? "",
                    sessionId: data.sessionId ?? sessionId,
                    success: true,
                    resourceUrl: data.resourceUrl ?? "",
                    status: data.status ?? "",
                };
            }

            logOperationSuccess(
                "AGB.getSession",
                `SessionId=${sessionId}, RequestId=${requestId}`,
            );

            return {
                requestId,
                httpStatusCode: response.statusCode,
                code: response.code ?? "",
                success: true,
                data: sessionData,
            };
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("AGB.getSession", errMsg);
            return {
                requestId: "",
                httpStatusCode: 0,
                code: "",
                success: false,
                errorMessage: `Failed to get session ${sessionId}: ${errMsg}`,
            };
        }
    }

    /**
     * Get a Session instance by session ID.
     *
     * @param sessionId - The session ID
     * @returns Promise resolving to SessionResult with a Session object or error
     */
    async get(sessionId: string): Promise<SessionResult> {
        logOperationStart("AGB.get", `SessionId=${sessionId}`);

        if (!sessionId?.trim()) {
            const errorMessage = "sessionId is required";
            logOperationError("AGB.get", errorMessage);
            return { requestId: "", success: false, errorMessage, session: null };
        }

        const getResult = await this.getSession(sessionId);
        if (!getResult.success) {
            const errorMessage =
                getResult.errorMessage || "Unknown error";
            logOperationError("AGB.get", errorMessage);
            return {
                requestId: getResult.requestId ?? "",
                success: false,
                errorMessage: `Failed to get session ${sessionId}: ${errorMessage}`,
                session: null,
            };
        }

        const session = new Session(this, sessionId);
        if (getResult.data) {
            session.resourceUrl = getResult.data.resourceUrl || "";
            session.appInstanceId = getResult.data.appInstanceId || "";
            session.resourceId = getResult.data.resourceId || "";
        }

        logOperationSuccess(
            "AGB.get",
            `SessionId=${sessionId}, RequestId=${getResult.requestId}`,
        );

        return {
            requestId: getResult.requestId ?? "",
            success: true,
            session,
        };
    }
}
