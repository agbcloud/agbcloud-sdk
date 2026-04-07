import { BaseService, SessionLike } from "../api/base-service";
import type {
    EnhancedCodeExecutionResult,
    ExecutionResult,
    ExecutionLogs,
    ExecutionError,
} from "../types/api-response";
import {
    logOperationStart,
    logOperationSuccess,
    logOperationError,
} from "../logger";
import type { WsStreamHandle, WsClient } from "./ws/ws-client";

const LANGUAGE_ALIASES: Record<string, string> = {
    python3: "python",
    py: "python",
    js: "javascript",
    node: "javascript",
    nodejs: "javascript",
};

const SUPPORTED_LANGUAGES = new Set(["python", "javascript", "java", "r"]);
const DEFAULT_STREAM_TARGET = "wuying_codespace";

function emptyResult(
    requestId: string,
    success: boolean,
    errorMessage: string,
): EnhancedCodeExecutionResult {
    return {
        requestId,
        success,
        executionCount: undefined,
        executionTime: 0,
        logs: { stdout: [], stderr: [] },
        results: [],
        errorMessage,
    };
}

function parseResultItem(item: unknown): ExecutionResult | null {
    if (typeof item === "object" && item !== null) {
        const d = item as Record<string, unknown>;
        return {
            text: (d["text/plain"] as string) ?? (d.text as string) ?? undefined,
            html: (d["text/html"] as string) ?? (d.html as string) ?? undefined,
            markdown:
                (d["text/markdown"] as string) ?? (d.markdown as string) ?? undefined,
            png: (d["image/png"] as string) ?? (d.png as string) ?? undefined,
            jpeg: (d["image/jpeg"] as string) ?? (d.jpeg as string) ?? undefined,
            svg: (d["image/svg+xml"] as string) ?? (d.svg as string) ?? undefined,
            json:
                (d["application/json"] as unknown) ?? (d.json as unknown) ?? undefined,
            latex: (d["text/latex"] as string) ?? (d.latex as string) ?? undefined,
            chart:
                (d["application/vnd.vegalite.v4+json"] as unknown) ??
                (d["application/vnd.vegalite.v5+json"] as unknown) ??
                (d.chart as unknown) ??
                undefined,
            isMainResult:
                (d.isMainResult as boolean) ?? (d.is_main_result as boolean) ?? false,
        };
    }
    if (typeof item === "string") {
        try {
            let parsed = JSON.parse(item);
            // Handle double encoding
            if (typeof parsed === "string") {
                try {
                    parsed = JSON.parse(parsed);
                } catch {
                    // Ignore: if the string is not valid JSON after the first parse,
                    // it means it was single-encoded, so we use the already-parsed value
                }
            }
            if (typeof parsed === "object" && parsed !== null) {
                return parseResultItem(parsed);
            }
            return { text: String(parsed), isMainResult: false };
        } catch {
            return { text: item, isMainResult: false };
        }
    }
    return { text: String(item), isMainResult: false };
}

/**
 * Code execution module for running code in the session (Python, JavaScript, Java, R).
 */
export class Code extends BaseService {
    /**
     * Execute code in the specified language with a timeout.
     *
     * This is the primary public method for code execution. For real-time
     * streaming output, set streamBeta=true and provide callback functions.
     *
     * @param code - Source code to execute
     * @param language - Language identifier. Case-insensitive.
     *   Supported values: 'python', 'javascript', 'java', 'r'.
     *   Aliases: 'py' -> 'python', 'js'/'node' -> 'javascript'.
     * @param timeoutS - Timeout in seconds (default 60)
     * @param options - Optional streaming parameters
     * @param options.streamBeta - If true, use WebSocket streaming for real-time output
     * @param options.onStdout - Callback invoked with each stdout chunk during streaming
     * @param options.onStderr - Callback invoked with each stderr chunk during streaming
     * @param options.onError - Callback invoked when an error occurs during streaming
     * @returns Promise resolving to EnhancedCodeExecutionResult with results and logs
     *
     * @example
     * ```typescript
     * // Simple execution
     * const result = await session.code.run("print('Hello')", "python");
     * console.log(result.results);
     *
     * // Streaming execution for long-running code
     * const result = await session.code.run(
     *   "import time\nfor i in range(5):\n    print(f'Progress: {i+1}/5')\n    time.sleep(1)",
     *   "python",
     *   60,
     *   { streamBeta: true, onStdout: (chunk) => console.log(chunk) }
     * );
     * ```
     */
    async run(
        code: string,
        language: string,
        timeoutS = 60,
        options?: {
            streamBeta?: boolean;
            onStdout?: (chunk: string) => void;
            onStderr?: (chunk: string) => void;
            onError?: (err: unknown) => void;
        },
    ): Promise<EnhancedCodeExecutionResult> {
        return this.runCode(code, language, timeoutS, options);
    }

    /**
     * Internal implementation for code execution.
     * Use the public `run()` method instead.
     */
    private async runCode(
        code: string,
        language: string,
        timeoutS = 60,
        options?: {
            streamBeta?: boolean;
            onStdout?: (chunk: string) => void;
            onStderr?: (chunk: string) => void;
            onError?: (err: unknown) => void;
        },
    ): Promise<EnhancedCodeExecutionResult> {
        try {
            const rawLang = language ?? "";
            const normalized = rawLang.trim().toLowerCase();
            const canonical = LANGUAGE_ALIASES[normalized] ?? normalized;

            if (!SUPPORTED_LANGUAGES.has(canonical)) {
                const errorMessage = `Unsupported language: ${rawLang}. Supported: ${[...SUPPORTED_LANGUAGES].sort().join(", ")}`;
                logOperationError("Code.run", errorMessage);
                return emptyResult("", false, errorMessage);
            }

            if (options?.streamBeta) {
                return this.runCodeStreamWs({
                    code,
                    language: canonical,
                    timeoutS,
                    onStdout: options.onStdout,
                    onStderr: options.onStderr,
                    onError: options.onError,
                });
            }

            logOperationStart("Code.run", `Language=${canonical}, TimeoutS=${timeoutS}`);

            const result = await this.callMcpTool("run_code", {
                code,
                language: canonical,
                timeout_s: timeoutS,
            });

            if (!result.success) {
                const errorMessage = result.errorMessage || "Failed to run code";
                logOperationError("Code.run", errorMessage);
                return emptyResult(result.requestId ?? "", false, errorMessage);
            }

            logOperationSuccess("Code.run", `RequestId=${result.requestId}`);
            return this.parseRunCodeResult(result.data, result.requestId ?? "");
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("Code.run", errMsg);
            return emptyResult("", false, `Failed to run code: ${errMsg}`);
        }
    }

    // ── WebSocket streaming ──────────────────────────────────────────

    private async runCodeStreamWs(params: {
        code: string;
        language: string;
        timeoutS: number;
        onStdout?: (chunk: string) => void;
        onStderr?: (chunk: string) => void;
        onError?: (err: unknown) => void;
    }): Promise<EnhancedCodeExecutionResult> {
        const { code, language, timeoutS, onStdout, onStderr, onError } = params;

        const stdoutChunks: string[] = [];
        const stderrChunks: string[] = [];
        const results: ExecutionResult[] = [];
        let errorObj: ExecutionError | undefined;
        let errorReported = false;

        const target = this.resolveStreamTarget();
        const session = this.session as SessionLike;
        if (!session._getWsClient) {
            throw new Error("WebSocket streaming is not supported by this session");
        }
        const wsClient = session._getWsClient() as WsClient;

        // ── callback helpers ──────────────────────────────────────

        const appendStream = (
            chunks: string[],
            callback: ((chunk: string) => void) | undefined,
            chunk: string,
        ): void => {
            chunks.push(chunk);
            if (callback) callback(chunk);
        };

        const handleErrorPayload = (errPayload: unknown): void => {
            errorReported = true;
            if (typeof errPayload === "object" && errPayload !== null) {
                const ep = errPayload as Record<string, unknown>;
                const name = String(ep.code ?? "ExecutionError");
                const value = String(ep.message ?? ep.error ?? "");
                const traceId = String(ep.traceId ?? "");
                errorObj = {
                    name,
                    value,
                    traceback: traceId ? `traceId=${traceId}` : "",
                };
            } else {
                errorObj = { name: "ExecutionError", value: String(errPayload), traceback: "" };
            }
            if (onError) onError(errPayload);
        };

        const parseResultEvent = (resultPayload: unknown): void => {
            if (typeof resultPayload !== "object" || resultPayload === null) {
                results.push({ text: String(resultPayload), isMainResult: false });
                return;
            }
            const rp = resultPayload as Record<string, unknown>;
            const isMain = Boolean(rp.isMainResult ?? rp.is_main_result) || false;
            const rawMime = rp.mime;
            const mime = (typeof rawMime === "object" && rawMime !== null)
                ? rawMime as Record<string, unknown>
                : {} as Record<string, unknown>;
            results.push({
                text: mime["text/plain"] as string | undefined,
                html: mime["text/html"] as string | undefined,
                markdown: mime["text/markdown"] as string | undefined,
                png: mime["image/png"] as string | undefined,
                jpeg: mime["image/jpeg"] as string | undefined,
                svg: mime["image/svg+xml"] as string | undefined,
                json: mime["application/json"],
                latex: mime["text/latex"] as string | undefined,
                chart:
                    (mime["application/vnd.vegalite.v4+json"] as unknown) ??
                    (mime["application/vnd.vegalite.v5+json"] as unknown) ??
                    undefined,
                isMainResult: isMain,
            });
        };

        const onEvent = (_invocationId: string, data: Record<string, unknown>): void => {
            const eventType = data.eventType as string | undefined;
            if (eventType === "stdout") {
                const chunk = data.chunk;
                if (typeof chunk === "string") appendStream(stdoutChunks, onStdout, chunk);
            } else if (eventType === "stderr") {
                const chunk = data.chunk;
                if (typeof chunk === "string") appendStream(stderrChunks, onStderr, chunk);
            } else if (eventType === "result") {
                parseResultEvent(data.result);
            } else if (eventType === "error") {
                handleErrorPayload(data.error ?? data);
            }
        };

        // ── execute via WebSocket ─────────────────────────────────

        let handle: WsStreamHandle;
        try {
            handle = await wsClient.callStream({
                target,
                data: {
                    method: "run_code",
                    mode: "stream",
                    params: { language, timeoutS, code },
                },
                onEvent,
                onEnd: undefined,
                onError: (_inv: string, err: Error) => handleErrorPayload(err),
            });
        } catch (e) {
            if (onError && !errorReported) onError(e);
            return {
                requestId: "",
                success: false,
                logs: { stdout: stdoutChunks, stderr: stderrChunks },
                results,
                error: errorObj,
                errorMessage: e instanceof Error ? e.message : String(e),
                executionTime: 0,
            };
        }

        try {
            const endData = await handle.waitEnd();

            const execCount = endData.executionCount;
            const executionCount = typeof execCount === "number" ? execCount : undefined;
            const executionTime = Number(endData.executionTime ?? 0);

            const executionError = endData.executionError as string | undefined;
            if (executionError && !errorObj) {
                errorObj = { name: "ExecutionError", value: String(executionError), traceback: "" };
            }

            const ok = !errorObj && !executionError && endData.status !== "failed";
            const errMsg = ok
                ? ""
                : (executionError ? String(executionError) : (errorObj?.value ?? ""));

            return {
                requestId: handle.invocationId,
                success: ok,
                executionCount,
                executionTime,
                logs: { stdout: stdoutChunks, stderr: stderrChunks },
                results,
                error: errorObj,
                errorMessage: errMsg,
            };
        } catch (e) {
            if (onError && !errorReported) onError(e);
            return {
                requestId: "",
                success: false,
                logs: { stdout: stdoutChunks, stderr: stderrChunks },
                results,
                error: errorObj,
                errorMessage: e instanceof Error ? e.message : String(e),
                executionTime: 0,
            };
        }
    }

    private resolveStreamTarget(): string {
        const mcpTools = this.session.mcpTools ?? [];
        for (const tool of mcpTools) {
            if (tool.name === "run_code" && tool.server) {
                return tool.server;
            }
        }
        return DEFAULT_STREAM_TARGET;
    }

    // ── Response parsing ─────────────────────────────────────────

    private parseRunCodeResult(
        data: unknown,
        requestId: string,
    ): EnhancedCodeExecutionResult {
        if (!data) return emptyResult(requestId, false, "No data returned");

        // Parse data into object format uniformly
        let responseData: unknown;
        if (typeof data === "string") {
            try {
                responseData = JSON.parse(data);
            } catch {
                responseData = data;
            }
        } else {
            responseData = data;
        }

        if (typeof responseData !== "object" || responseData === null) {
            const text = String(data);
            return {
                requestId,
                success: true,
                results: [{ text, isMainResult: true }],
                logs: { stdout: [text], stderr: [] },
                errorMessage: "",
                executionTime: 0,
            };
        }

        let d = responseData as Record<string, unknown>;

        // Check if response is in legacy format where JSON is in content[0].text
        const content = d.content as Record<string, unknown>[] | undefined;
        if (Array.isArray(content) && content.length > 0) {
            const textString = content[0]?.text;
            if (typeof textString === "string") {
                try {
                    const parsed = JSON.parse(textString);
                    if (
                        typeof parsed === "object" && parsed !== null &&
                        ("result" in parsed || "executionError" in parsed)
                    ) {
                        d = parsed as Record<string, unknown>;
                    }
                } catch {
                    // not valid JSON, continue
                }
            }
        }

        // Check for error response
        if (d.isError) {
            const errorContent = (d.content as Record<string, unknown>[]) ?? [];
            const errorMessage = errorContent
                .filter((item) => typeof item === "object" && item !== null)
                .map((item) => (item as Record<string, unknown>).text ?? "Unknown error")
                .join("; ");
            return emptyResult(requestId, false, `Error in response: ${errorMessage}`);
        }

        // Check formats by priority and parse
        if ("result" in d && Array.isArray(d.result)) {
            return this.parseNewFormat(d, requestId);
        }
        if ("logs" in d || "results" in d) {
            return this.parseRichFormat(d, requestId);
        }
        if ("content" in d) {
            return this.parseLegacyFormat(d, requestId);
        }

        // Default fallback
        const text = String(responseData);
        return {
            requestId,
            success: true,
            results: [{ text, isMainResult: true }],
            logs: { stdout: [text], stderr: [] },
            errorMessage: "",
            executionTime: 0,
        };
    }

    private parseNewFormat(
        d: Record<string, unknown>,
        requestId: string,
    ): EnhancedCodeExecutionResult {
        const logs: ExecutionLogs = {
            stdout: (d.stdout as string[]) ?? [],
            stderr: (d.stderr as string[]) ?? [],
        };
        const results: ExecutionResult[] = [];
        for (const item of d.result as unknown[]) {
            const parsed = parseResultItem(item);
            if (parsed) results.push(parsed);
        }

        const execError = d.executionError as string | undefined;
        let error: ExecutionError | undefined;
        if (execError) {
            error = { name: "ExecutionError", value: String(execError), traceback: "" };
        }

        return {
            requestId,
            executionCount: d.execution_count as number | undefined,
            executionTime: (d.execution_time as number) ?? 0,
            logs,
            results,
            error,
            errorMessage: execError ?? "",
            success: !execError && !d.isError,
        };
    }

    private parseRichFormat(
        d: Record<string, unknown>,
        requestId: string,
    ): EnhancedCodeExecutionResult {
        const logsData = (d.logs as Record<string, unknown>) ?? {};
        const logs: ExecutionLogs = {
            stdout: (logsData.stdout as string[]) ?? [],
            stderr: (logsData.stderr as string[]) ?? [],
        };
        const results: ExecutionResult[] = [];
        for (const item of (d.results as Record<string, unknown>[]) ?? []) {
            results.push({
                text: item.text as string | undefined,
                html: item.html as string | undefined,
                markdown: item.markdown as string | undefined,
                png: item.png as string | undefined,
                jpeg: item.jpeg as string | undefined,
                svg: item.svg as string | undefined,
                json: item.json,
                latex: item.latex as string | undefined,
                chart: item.chart,
                isMainResult: (item.is_main_result as boolean) ?? false,
            });
        }

        const errorData = d.error as Record<string, unknown> | undefined;
        let error: ExecutionError | undefined;
        let errorMessage = "";
        if (errorData) {
            error = {
                name: (errorData.name as string) ?? "UnknownError",
                value: (errorData.value as string) ?? "",
                traceback: (errorData.traceback as string) ?? "",
            };
            errorMessage = (errorData.value as string) || (errorData.name as string) || "UnknownError";
        }

        return {
            requestId,
            executionCount: d.execution_count as number | undefined,
            executionTime: (d.execution_time as number) ?? 0,
            logs,
            results,
            error,
            errorMessage,
            success: !(d.isError as boolean),
        };
    }

    private parseLegacyFormat(
        d: Record<string, unknown>,
        requestId: string,
    ): EnhancedCodeExecutionResult {
        const content = d.content as Record<string, unknown>[];
        if (Array.isArray(content) && content.length > 0) {
            const text = content[0].text as string | undefined;
            if (text !== undefined) {
                return {
                    requestId,
                    success: true,
                    logs: { stdout: [text], stderr: [] },
                    results: [{ text, isMainResult: true }],
                    errorMessage: "",
                    executionTime: 0,
                };
            }
        }
        return emptyResult(requestId, false, "No content found in response");
    }
}
