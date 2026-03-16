import { BaseService } from "../api/base-service";
import type {
    EnhancedCodeExecutionResult,
    ExecutionResult,
    ExecutionLogs,
} from "../types/api-response";
import {
    logOperationStart,
    logOperationSuccess,
    logOperationError,
} from "../logger";

const LANGUAGE_ALIASES: Record<string, string> = {
    python3: "python",
    py: "python",
    js: "javascript",
    node: "javascript",
    nodejs: "javascript",
};

const SUPPORTED_LANGUAGES = new Set(["python", "javascript", "java", "r"]);

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
            const parsed = JSON.parse(item);
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
     * Run code in the session.
     *
     * @param code - Source code to execute
     * @param language - Language identifier (e.g. "python", "javascript", "java", "r")
     * @param timeoutS - Timeout in seconds (default 60)
     * @returns Promise resolving to EnhancedCodeExecutionResult with results and logs
     */
    async run(
        code: string,
        language: string,
        timeoutS = 60,
    ): Promise<EnhancedCodeExecutionResult> {
        try {
            const lang = language.toLowerCase();
            const canonical = LANGUAGE_ALIASES[lang] ?? lang;

            if (!SUPPORTED_LANGUAGES.has(canonical)) {
                const errorMessage = `Unsupported language: ${language}. Supported: ${[...SUPPORTED_LANGUAGES].join(", ")}`;
                logOperationError("Code.run", errorMessage);
                return emptyResult("", false, errorMessage);
            }

            logOperationStart("Code.run", `Language=${canonical}, TimeoutS=${timeoutS}`);

            const result = await this.callMcpTool("run_code", {
                code,
                language: canonical,
                timeout_s: timeoutS,
            });

            if (result.success) {
                logOperationSuccess("Code.run", `RequestId=${result.requestId}`);
                return this.parseRunCodeResult(result.data, result.requestId ?? "");
            }

            const errorMessage = result.errorMessage || "Failed to run code";
            logOperationError("Code.run", errorMessage);
            return emptyResult(result.requestId ?? "", false, errorMessage);
        } catch (e: unknown) {
            const errMsg = e instanceof Error ? e.message : String(e);
            logOperationError("Code.run", errMsg);
            return emptyResult("", false, `Failed to run code: ${errMsg}`);
        }
    }

    /** Alias for run */
    execute = this.run.bind(this);

    private parseRunCodeResult(
        data: unknown,
        requestId: string,
    ): EnhancedCodeExecutionResult {
        if (!data) return emptyResult(requestId, false, "No data returned");

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
            return {
                requestId,
                success: true,
                results: [{ text: String(data), isMainResult: true }],
                logs: { stdout: [String(data)], stderr: [] },
                errorMessage: "",
                executionTime: 0,
            };
        }

        const d = responseData as Record<string, unknown>;

        if ("result" in d && Array.isArray(d.result)) {
            return this.parseNewFormat(d, requestId);
        }
        if ("logs" in d || "results" in d) {
            return this.parseRichFormat(d, requestId);
        }
        if ("content" in d) {
            return this.parseLegacyFormat(d, requestId);
        }

        return {
            requestId,
            success: true,
            results: [{ text: String(responseData), isMainResult: true }],
            logs: { stdout: [String(responseData)], stderr: [] },
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
        return {
            requestId,
            executionCount: d.execution_count as number | undefined,
            executionTime: (d.execution_time as number) ?? 0,
            logs,
            results,
            errorMessage: execError ?? "",
            success: !execError,
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
        const errorObj = d.error as Record<string, unknown> | undefined;
        const errorMessage = errorObj
            ? (errorObj.value as string) ?? (errorObj.name as string) ?? ""
            : "";
        return {
            requestId,
            executionCount: d.execution_count as number | undefined,
            executionTime: (d.execution_time as number) ?? 0,
            logs,
            results,
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
