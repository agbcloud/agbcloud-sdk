export enum LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3,
    SILENT = 4,
}

export interface LoggerConfig {
    level: LogLevel;
    prefix: string;
}

let currentLevel: LogLevel = LogLevel.INFO;
const PREFIX = "AGB";

function getEnvLogLevel(): LogLevel {
    const envLevel = process.env.AGB_LOG_LEVEL?.toUpperCase();
    switch (envLevel) {
        case "DEBUG":
            return LogLevel.DEBUG;
        case "INFO":
            return LogLevel.INFO;
        case "WARN":
        case "WARNING":
            return LogLevel.WARN;
        case "ERROR":
            return LogLevel.ERROR;
        case "SILENT":
            return LogLevel.SILENT;
        default:
            return LogLevel.INFO;
    }
}

currentLevel = getEnvLogLevel();

function timestamp(): string {
    return new Date().toISOString();
}

export function setLogLevel(level: LogLevel): void {
    currentLevel = level;
}

export function getLogLevel(): LogLevel {
    return currentLevel;
}

export function logDebug(message: string, ...args: unknown[]): void {
    if (currentLevel <= LogLevel.DEBUG) {
        console.debug(`${timestamp()} | ${PREFIX} | DEBUG | ${message}`, ...args);
    }
}

export function logInfo(message: string, ...args: unknown[]): void {
    if (currentLevel <= LogLevel.INFO) {
        console.info(`${timestamp()} | ${PREFIX} | INFO  | ${message}`, ...args);
    }
}

export function logWarn(message: string, ...args: unknown[]): void {
    if (currentLevel <= LogLevel.WARN) {
        console.warn(`${timestamp()} | ${PREFIX} | WARN  | ${message}`, ...args);
    }
}

export function logError(message: string, ...args: unknown[]): void {
    if (currentLevel <= LogLevel.ERROR) {
        console.error(`${timestamp()} | ${PREFIX} | ERROR | ${message}`, ...args);
    }
}

const SENSITIVE_FIELDS = [
    "api_key",
    "apikey",
    "api-key",
    "password",
    "passwd",
    "pwd",
    "token",
    "access_token",
    "auth_token",
    "secret",
    "private_key",
    "authorization",
];

export function maskSensitiveData(
    data: unknown,
    fields: string[] = SENSITIVE_FIELDS,
): unknown {
    if (data && typeof data === "object" && !Array.isArray(data)) {
        const masked: Record<string, unknown> = {};
        for (const [key, value] of Object.entries(data as Record<string, unknown>)) {
            if (fields.some((f) => key.toLowerCase().includes(f))) {
                if (typeof value === "string" && value.length > 4) {
                    masked[key] = value.slice(0, 2) + "****" + value.slice(-2);
                } else {
                    masked[key] = "****";
                }
            } else {
                masked[key] = maskSensitiveData(value, fields);
            }
        }
        return masked;
    }
    if (Array.isArray(data)) {
        return data.map((item) => maskSensitiveData(item, fields));
    }
    return data;
}

export function logApiCall(apiName: string, requestData = ""): void {
    logDebug(`API Call: ${apiName}`);
    if (requestData) {
        logDebug(`  └─ ${requestData}`);
    }
}

export function logApiResponse(
    apiName: string,
    requestId = "",
    success = true,
    extra?: string,
): void {
    if (success) {
        let msg = requestId
            ? `API Response: ${apiName}, RequestId=${requestId}`
            : `API Response: ${apiName}`;
        if (extra) {
            msg += `, ${extra}`;
        }
        logInfo(msg);
    } else {
        logError(`API Response Failed: ${apiName}, RequestId=${requestId}`);
    }
}

export function logOperationStart(operation: string, details = ""): void {
    logInfo(`Starting: ${operation}`);
    if (details) {
        logDebug(`Details: ${details}`);
    }
}

export function logOperationSuccess(operation: string, result = ""): void {
    logInfo(`Completed: ${operation}`);
    if (result) {
        logDebug(`Result: ${result}`);
    }
}

export function logOperationError(operation: string, error: string): void {
    logError(`Failed: ${operation}`);
    logError(`Error: ${error}`);
}
