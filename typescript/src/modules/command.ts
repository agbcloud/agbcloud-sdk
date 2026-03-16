import { BaseService } from "../api/base-service";
import type { CommandResult } from "../types/api-response";
import {
    logOperationStart,
    logOperationSuccess,
    logOperationError,
    logDebug,
} from "../logger";

/**
 * Command module for executing shell commands in the session.
 */
export class Command extends BaseService {
    /**
     * Execute a shell command in the session.
     *
     * @param command - The command string to execute
     * @param timeoutMs - Timeout in milliseconds (default 1000)
     * @param cwd - Optional working directory
     * @param envs - Optional environment variables (key-value pairs)
     * @returns Promise resolving to CommandResult with stdout, stderr, exitCode
     */
    async execute(
        command: string,
        timeoutMs = 1000,
        cwd?: string,
        envs?: Record<string, string>,
    ): Promise<CommandResult> {
        if (envs) {
            for (const [key, value] of Object.entries(envs)) {
                if (typeof key !== "string" || typeof value !== "string") {
                    throw new Error(
                        "Invalid environment variables: all keys and values must be strings",
                    );
                }
            }
        }

        try {
            const args: Record<string, unknown> = { command, timeout_ms: timeoutMs };
            if (cwd !== undefined) args.cwd = cwd;
            if (envs !== undefined) args.envs = envs;

            logOperationStart(
                "Command.execute",
                `Command=${command}, TimeoutMs=${timeoutMs}`,
            );

            const result = await this.callMcpTool("shell", args);

            if (result.success) {
                try {
                    const dataJson =
                        typeof result.data === "string"
                            ? JSON.parse(result.data)
                            : result.data;

                    const stdout = (dataJson as Record<string, unknown>)?.stdout as string ?? "";
                    const stderr = (dataJson as Record<string, unknown>)?.stderr as string ?? "";
                    const exitCode = (dataJson as Record<string, unknown>)?.exit_code as number ?? 0;
                    const traceId = (dataJson as Record<string, unknown>)?.traceId as string ?? "";
                    const success = exitCode === 0;
                    const output = stdout + stderr;

                    logOperationSuccess(
                        "Command.execute",
                        `RequestId=${result.requestId}, ExitCode=${exitCode}`,
                    );

                    return {
                        requestId: result.requestId,
                        success,
                        output,
                        exitCode,
                        stdout,
                        stderr,
                        traceId,
                    };
                } catch {
                    logOperationSuccess("Command.execute", `RequestId=${result.requestId}`);
                    return {
                        requestId: result.requestId,
                        success: true,
                        output: typeof result.data === "string" ? result.data : String(result.data),
                        exitCode: 0,
                        stdout: typeof result.data === "string" ? result.data : String(result.data),
                        stderr: "",
                        traceId: "",
                    };
                }
            }

            try {
                const errorData =
                    typeof result.errorMessage === "string"
                        ? JSON.parse(result.errorMessage)
                        : null;
                if (errorData && typeof errorData === "object") {
                    const stdout = (errorData as Record<string, unknown>).stdout as string ?? "";
                    const stderr = (errorData as Record<string, unknown>).stderr as string ?? "";
                    const exitCode =
                        ((errorData as Record<string, unknown>).exit_code as number) ??
                        ((errorData as Record<string, unknown>).errorCode as number) ??
                        0;
                    const traceId = (errorData as Record<string, unknown>).traceId as string ?? "";
                    const output = stdout + stderr;
                    const errorMsg = stderr || result.errorMessage || "Failed to execute command";
                    logOperationError("Command.execute", errorMsg);
                    return {
                        requestId: result.requestId,
                        success: false,
                        output,
                        exitCode,
                        stdout,
                        stderr,
                        traceId,
                        errorMessage: errorMsg,
                    };
                }
            } catch {
                // not JSON, use original error message
            }

            const errorMessage = result.errorMessage || "Failed to execute command";
            logOperationError("Command.execute", errorMessage);
            return {
                requestId: result.requestId,
                success: false,
                output: "",
                exitCode: -1,
                stdout: "",
                stderr: "",
                traceId: "",
                errorMessage,
            };
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("Command.execute", errMsg);
            return {
                requestId: "",
                success: false,
                output: "",
                exitCode: -1,
                stdout: "",
                stderr: "",
                traceId: "",
                errorMessage: `Failed to execute command: ${errMsg}`,
            };
        }
    }

    /** Alias for execute */
    run = this.execute.bind(this);
    exec = this.execute.bind(this);
}
