/**
 * Base error class for all AGB errors.
 */
export class AGBError extends Error {
    extra: Record<string, unknown>;

    constructor(message = "AGBError", extra: Record<string, unknown> = {}) {
        super(message);
        this.name = this.constructor.name;
        this.extra = extra;
    }
}

/**
 * Factory function to create error classes with minimal boilerplate.
 */
export function createErrorClass(
    name: string,
    defaultMessage: string,
): typeof AGBError {
    return class extends AGBError {
        constructor(message = defaultMessage, extra: Record<string, unknown> = {}) {
            super(message, extra);
            this.name = name;
        }
    };
}

export const AuthenticationError = createErrorClass("AuthenticationError", "Authentication failed");
export const FileError = createErrorClass("FileError", "File operation error");
export const CommandError = createErrorClass("CommandError", "Command execution error");
export const SessionError = createErrorClass("SessionError", "Session error");
export const ApplicationError = createErrorClass("ApplicationError", "Application operation error");
export const BrowserError = createErrorClass("BrowserError", "Browser operation error");
export const ScreenError = createErrorClass("ScreenError", "Screen operation error");
export const ClearanceTimeoutError = createErrorClass("ClearanceTimeoutError", "Clearance task timed out");

/**
 * API error with optional status code.
 */
export class APIError extends AGBError {
    statusCode?: number;

    constructor(message = "API error", statusCode?: number, extra: Record<string, unknown> = {}) {
        super(message, extra);
        this.statusCode = statusCode;
    }
}
