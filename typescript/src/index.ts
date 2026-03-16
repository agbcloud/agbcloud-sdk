// Core
export { AGB } from "./agb";
export type { AGBOptions } from "./agb";
export { Session } from "./session";
export { CreateSessionParams } from "./session-params";
export type { CreateSessionParamsOptions } from "./session-params";
export { BrowserContext } from "./session-params";

// Config
export { loadConfig, defaultConfig } from "./config";
export type { Config, ConfigOptions } from "./config";

// Exceptions
export {
    AGBError,
    AuthenticationError,
    APIError,
    FileError,
    CommandError,
    SessionError,
    ApplicationError,
    BrowserError,
    ClearanceTimeoutError,
} from "./exceptions";

// Modules
export { Command } from "./modules/command";
export { Code } from "./modules/code";
export { FileSystem } from "./modules/filesystem";
export { Browser } from "./modules/browser/browser";
export type {
    BrowserOption,
    BrowserProxy,
    BrowserFingerprint,
    BrowserViewport,
    BrowserScreen,
    BrowserProxyType,
    BrowserProxyStrategy,
} from "./modules/browser/browser";
export {
    BrowserOptionClass,
    BrowserProxyClass,
    BrowserFingerprintContext,
} from "./modules/browser/browser";
export { BrowserAgent } from "./modules/browser/browser-agent";
export type {
    ActOptions,
    ActResult,
    ObserveOptions,
    ObserveResult,
    ExtractOptions,
    ExtractResult,
} from "./modules/browser/browser-agent";
export {
    FingerprintFormat,
    BrowserFingerprintGenerator,
} from "./modules/browser/fingerprint";
export type {
    ScreenFingerprint,
    Brand,
    UserAgentData,
    ExtraProperties,
    NavigatorFingerprint,
    VideoCard,
    Fingerprint,
} from "./modules/browser/fingerprint";
export {
    Computer,
    MouseController,
    KeyboardController,
    WindowManager,
    ApplicationManager,
    ScreenController,
    MouseButton,
    ScrollDirection,
} from "./modules/computer/computer";

// Context
export { Context, ContextService } from "./context";
export type { ContextListParams } from "./context";
export { ContextManager } from "./context-manager";
export type { ContextStatusData, ContextInfoResult, ContextSyncResult } from "./context-manager";
export {
    ContextSync,
    UploadStrategy,
    DownloadStrategy,
    UploadMode,
    Lifecycle,
    newSyncPolicy,
    newUploadPolicy,
    newDownloadPolicy,
    newDeletePolicy,
    newExtractPolicy,
    newRecyclePolicy,
    syncPolicyToDict,
} from "./context-sync";
export type {
    SyncPolicy,
    UploadPolicy,
    DownloadPolicy,
    DeletePolicy,
    ExtractPolicy,
    RecyclePolicy,
    WhiteList,
    BWList,
    MappingPolicy,
} from "./context-sync";

// Extensions
export { Extension, ExtensionOption, ExtensionsService } from "./extension";

// Types
export type {
    ApiResponse,
    SessionResult,
    DeleteResult,
    OperationResult,
    BoolResult,
    GetSessionResult,
    GetSessionData,
    SessionListResult,
    SessionStatusResult,
    SessionMetrics,
    SessionMetricsResult,
    McpTool,
    McpToolResult,
    McpToolsResult,
    CommandResult,
    ExecutionResult,
    ExecutionLogs,
    EnhancedCodeExecutionResult,
    FileContentResult,
    BinaryFileContentResult,
    MultipleFileContentResult,
    FileInfoResult,
    DirectoryEntry,
    DirectoryListResult,
    FileSearchResult,
    FileChangeEvent,
    FileChangeResult,
    UploadResult,
    DownloadResult,
    CursorPosition,
    ScreenSize,
    WindowInfo,
    WindowInfoResult,
    WindowListResult,
    AppOperationResult,
    ProcessInfo,
    ProcessListResult,
    InstalledAppInfo,
    InstalledAppListResult,
    ContextData,
    ContextResult,
    ContextListResult,
    ClearContextResult,
    FileUrlResult,
    ContextFileEntry,
    ContextFileListResult,
    ContextStatusData as ContextStatusDataType,
    ContextInfoResult as ContextInfoResultType,
    ContextSyncResult as ContextSyncResultType,
} from "./types/api-response";

// Logger
export {
    setLogLevel,
    getLogLevel,
    LogLevel,
    logDebug,
    logInfo,
    logWarn,
    logError,
} from "./logger";

// Version
export { getSdkVersion, isReleaseVersion, VERSION } from "./version";

// API (for advanced use)
export { Client } from "./api/client";
export { HTTPClient } from "./api/http-client";
export { BaseService } from "./api/base-service";
export type { SessionLike } from "./api/base-service";
