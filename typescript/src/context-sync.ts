/** When to upload context data (e.g. before session release). */
export enum UploadStrategy {
    UPLOAD_BEFORE_RESOURCE_RELEASE = "UploadBeforeResourceRelease",
}

export enum DownloadStrategy {
    DOWNLOAD_ASYNC = "DownloadAsync",
}

export enum UploadMode {
    FILE = "File",
    ARCHIVE = "Archive",
}

export enum Lifecycle {
    LIFECYCLE_1DAY = "Lifecycle_1Day",
    LIFECYCLE_3DAYS = "Lifecycle_3Days",
    LIFECYCLE_5DAYS = "Lifecycle_5Days",
    LIFECYCLE_10DAYS = "Lifecycle_10Days",
    LIFECYCLE_15DAYS = "Lifecycle_15Days",
    LIFECYCLE_30DAYS = "Lifecycle_30Days",
    LIFECYCLE_90DAYS = "Lifecycle_90Days",
    LIFECYCLE_180DAYS = "Lifecycle_180Days",
    LIFECYCLE_360DAYS = "Lifecycle_360Days",
    LIFECYCLE_FOREVER = "Lifecycle_Forever",
}

export interface UploadPolicy {
    autoUpload: boolean;
    uploadStrategy: UploadStrategy;
    uploadMode: UploadMode;
}

export interface DownloadPolicy {
    autoDownload: boolean;
    downloadStrategy: DownloadStrategy;
}

export interface DeletePolicy {
    syncLocalFile: boolean;
}

export interface ExtractPolicy {
    extract: boolean;
    deleteSrcFile: boolean;
    extractCurrentFolder: boolean;
}

export interface RecyclePolicy {
    lifecycle: Lifecycle;
    paths: string[];
}

export interface WhiteList {
    path: string;
    excludePaths: string[];
}

export interface BWList {
    whiteLists: WhiteList[];
}

export interface MappingPolicy {
    path: string;
}

/** Policy for context sync: upload, download, delete, recycle, whitelist, mapping. */
export interface SyncPolicy {
    uploadPolicy?: UploadPolicy;
    downloadPolicy?: DownloadPolicy;
    deletePolicy?: DeletePolicy;
    extractPolicy?: ExtractPolicy;
    recyclePolicy?: RecyclePolicy;
    bwList?: BWList;
    mappingPolicy?: MappingPolicy;
}

function containsWildcard(p: string): boolean {
    return /[*?\[\]]/.test(p);
}

export function newUploadPolicy(
    options: Partial<UploadPolicy> = {},
): UploadPolicy {
    return {
        autoUpload: options.autoUpload ?? true,
        uploadStrategy:
            options.uploadStrategy ??
            UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
        uploadMode: options.uploadMode ?? UploadMode.FILE,
    };
}

export function newDownloadPolicy(
    options: Partial<DownloadPolicy> = {},
): DownloadPolicy {
    return {
        autoDownload: options.autoDownload ?? true,
        downloadStrategy:
            options.downloadStrategy ?? DownloadStrategy.DOWNLOAD_ASYNC,
    };
}

export function newDeletePolicy(
    options: Partial<DeletePolicy> = {},
): DeletePolicy {
    return {
        syncLocalFile: options.syncLocalFile ?? true,
    };
}

export function newExtractPolicy(
    options: Partial<ExtractPolicy> = {},
): ExtractPolicy {
    return {
        extract: options.extract ?? true,
        deleteSrcFile: options.deleteSrcFile ?? true,
        extractCurrentFolder: options.extractCurrentFolder ?? false,
    };
}

export function newRecyclePolicy(
    options: Partial<RecyclePolicy> = {},
): RecyclePolicy {
    const paths = options.paths ?? [""];
    for (const p of paths) {
        if (p && p.trim() !== "" && containsWildcard(p)) {
            throw new Error(
                `Wildcard patterns are not supported in recycle policy paths. Got: ${p}`,
            );
        }
    }
    return {
        lifecycle: options.lifecycle ?? Lifecycle.LIFECYCLE_FOREVER,
        paths,
    };
}

export function newSyncPolicy(
    options: Partial<SyncPolicy> = {},
): SyncPolicy {
    return {
        uploadPolicy: options.uploadPolicy ?? newUploadPolicy(),
        downloadPolicy: options.downloadPolicy ?? newDownloadPolicy(),
        deletePolicy: options.deletePolicy ?? newDeletePolicy(),
        extractPolicy: options.extractPolicy ?? newExtractPolicy(),
        recyclePolicy: options.recyclePolicy ?? newRecyclePolicy(),
        bwList: options.bwList ?? { whiteLists: [] },
        mappingPolicy: options.mappingPolicy,
    };
}

function uploadPolicyToDict(p: UploadPolicy): Record<string, unknown> {
    return {
        autoUpload: p.autoUpload,
        uploadStrategy: p.uploadStrategy,
        uploadMode: p.uploadMode,
    };
}

function downloadPolicyToDict(p: DownloadPolicy): Record<string, unknown> {
    return {
        autoDownload: p.autoDownload,
        downloadStrategy: p.downloadStrategy,
    };
}

function deletePolicyToDict(p: DeletePolicy): Record<string, unknown> {
    return { syncLocalFile: p.syncLocalFile };
}

function extractPolicyToDict(p: ExtractPolicy): Record<string, unknown> {
    return {
        extract: p.extract,
        deleteSrcFile: p.deleteSrcFile,
        extractToCurrentFolder: p.extractCurrentFolder,
    };
}

function recyclePolicyToDict(p: RecyclePolicy): Record<string, unknown> {
    return { lifecycle: p.lifecycle, paths: p.paths };
}

function bwListToDict(
    b: BWList,
): Record<string, unknown> {
    return {
        whiteLists: b.whiteLists.map((wl) => ({
            path: wl.path,
            excludePaths: wl.excludePaths,
        })),
    };
}

function mappingPolicyToDict(m: MappingPolicy): Record<string, unknown> {
    return { path: m.path };
}

export function syncPolicyToDict(
    policy: SyncPolicy,
): Record<string, unknown> {
    const result: Record<string, unknown> = {};
    if (policy.uploadPolicy)
        result.uploadPolicy = uploadPolicyToDict(policy.uploadPolicy);
    if (policy.downloadPolicy)
        result.downloadPolicy = downloadPolicyToDict(policy.downloadPolicy);
    if (policy.deletePolicy)
        result.deletePolicy = deletePolicyToDict(policy.deletePolicy);
    if (policy.extractPolicy)
        result.extractPolicy = extractPolicyToDict(policy.extractPolicy);
    if (policy.recyclePolicy)
        result.recyclePolicy = recyclePolicyToDict(policy.recyclePolicy);
    if (policy.bwList) result.bwList = bwListToDict(policy.bwList);
    if (policy.mappingPolicy)
        result.mappingPolicy = mappingPolicyToDict(policy.mappingPolicy);
    return result;
}

/**
 * Binds a local path in the session to a named context for sync (upload/download) across sessions.
 */
export class ContextSync {
    contextId: string;
    path: string;
    policy?: SyncPolicy;

    /**
     * @param contextId - Context ID (or name) to sync with
     * @param path - Local path in the session to sync
     * @param policy - Optional sync policy (upload, download, recycle, etc.)
     */
    constructor(contextId: string, path: string, policy?: SyncPolicy) {
        this.contextId = contextId;
        this.path = path;
        this.policy = policy;
    }

    static new(
        contextId: string,
        path: string,
        policy?: SyncPolicy,
    ): ContextSync {
        return new ContextSync(contextId, path, policy);
    }

    withPolicy(policy: SyncPolicy): ContextSync {
        this.policy = policy;
        return this;
    }
}
