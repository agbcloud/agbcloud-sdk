export class AGBError extends Error {
    extra: Record<string, unknown>;

    constructor(message = "AGBError", extra: Record<string, unknown> = {}) {
        super(message);
        this.name = "AGBError";
        this.extra = extra;
    }
}

export class AuthenticationError extends AGBError {
    constructor(
        message = "Authentication failed",
        extra: Record<string, unknown> = {},
    ) {
        super(message, extra);
        this.name = "AuthenticationError";
    }
}

export class APIError extends AGBError {
    statusCode?: number;

    constructor(
        message = "API error",
        statusCode?: number,
        extra: Record<string, unknown> = {},
    ) {
        super(message, extra);
        this.name = "APIError";
        this.statusCode = statusCode;
    }
}

export class FileError extends AGBError {
    constructor(
        message = "File operation error",
        extra: Record<string, unknown> = {},
    ) {
        super(message, extra);
        this.name = "FileError";
    }
}

export class CommandError extends AGBError {
    constructor(
        message = "Command execution error",
        extra: Record<string, unknown> = {},
    ) {
        super(message, extra);
        this.name = "CommandError";
    }
}

export class SessionError extends AGBError {
    constructor(
        message = "Session error",
        extra: Record<string, unknown> = {},
    ) {
        super(message, extra);
        this.name = "SessionError";
    }
}

export class ApplicationError extends AGBError {
    constructor(
        message = "Application operation error",
        extra: Record<string, unknown> = {},
    ) {
        super(message, extra);
        this.name = "ApplicationError";
    }
}

export class BrowserError extends AGBError {
    constructor(
        message = "Browser operation error",
        extra: Record<string, unknown> = {},
    ) {
        super(message, extra);
        this.name = "BrowserError";
    }
}

export class ClearanceTimeoutError extends AGBError {
    constructor(
        message = "Clearance task timed out",
        extra: Record<string, unknown> = {},
    ) {
        super(message, extra);
        this.name = "ClearanceTimeoutError";
    }
}
