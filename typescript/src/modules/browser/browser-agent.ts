import {
    BaseService,
    type SessionLike,
} from "../../api/base-service";
import type { OperationResult } from "../../types/api-response";
import { BrowserError } from "../../exceptions";
import {
    logOperationStart,
    logOperationSuccess,
    logOperationError,
    logInfo,
    logDebug,
    logWarn,
} from "../../logger";

// ─── Option Types ───────────────────────────────────────────

export interface ActOptions {
    action: string;
    timeout?: number;
    variables?: Record<string, string>;
    useVision?: boolean;
    iframes?: boolean;
    domSettleTimeoutMs?: number;
}

export interface ObserveOptions {
    instruction: string;
    useVision?: boolean;
    selector?: string;
    timeout?: number;
    iframes?: boolean;
    domSettleTimeoutMs?: number;
}

export interface ExtractOptions {
    instruction: string;
    schema: Record<string, unknown>;
    useTextExtract?: boolean;
    selector?: string;
    useVision?: boolean;
    timeout?: number;
    maxPage?: number;
    iframe?: boolean;
    domSettleTimeoutMs?: number;
}

// ─── Result Types ───────────────────────────────────────────

export interface ActResult {
    success: boolean;
    message: string;
}

export interface ObserveResult {
    selector: string;
    description: string;
    method: string;
    arguments: Record<string, unknown>;
}

export interface ExtractResult<T = unknown> {
    success: boolean;
    data: T | null;
}

// ─── Helpers ────────────────────────────────────────────────

function stripNulls(obj: Record<string, unknown>): Record<string, unknown> {
    const result: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(obj)) {
        if (v !== undefined && v !== null) {
            result[k] = v;
        }
    }
    return result;
}

function sleep(ms: number): Promise<void> {
    return new Promise((r) => setTimeout(r, ms));
}

// ─── Browser-like interface ─────────────────────────────────

interface BrowserLike {
    isInitialized(): boolean;
}

// ─── BrowserAgent ───────────────────────────────────────────

const DEFAULT_MCP_TIMEOUT = 60000;
const DEFAULT_CLIENT_TIMEOUT_S = 300;
const POLL_INTERVAL_ACT = 5000;
const POLL_INTERVAL_OBSERVE = 5000;
const POLL_INTERVAL_EXTRACT = 8000;

export class BrowserAgent extends BaseService {
    private browser: BrowserLike;

    constructor(session: SessionLike, browser: BrowserLike) {
        super(session);
        this.browser = browser;
    }

    private ensureInitialized(method: string): void {
        if (!this.browser.isInitialized()) {
            throw new BrowserError(
                `Browser must be initialized before calling ${method}.`,
            );
        }
    }

    private async callWithTimeout(
        toolName: string,
        args: Record<string, unknown>,
    ): Promise<OperationResult> {
        return this.callMcpTool(toolName, args, DEFAULT_MCP_TIMEOUT, DEFAULT_MCP_TIMEOUT);
    }

    // ─── navigate ───────────────────────────────────────────

    /**
     * Navigate the browser to the given URL.
     *
     * Args:
     *   url: The URL to navigate to.
     *
     * Returns:
     *   The navigation result string, or an error message.
     */
    async navigate(url: string): Promise<string> {
        this.ensureInitialized("navigate");
        logOperationStart("BrowserAgent.navigate", `URL=${url}`);
        try {
            const result = await this.callWithTimeout("page_use_navigate", { url });
            if (result.success && result.data) {
                logOperationSuccess("BrowserAgent.navigate", `URL=${url}`);
                return typeof result.data === "string"
                    ? result.data
                    : JSON.stringify(result.data);
            }
            return `Navigation failed: ${result.errorMessage ?? "Unknown error"}`;
        } catch (e) {
            const msg = e instanceof Error ? e.message : String(e);
            throw new BrowserError(`Failed to navigate: ${msg}`);
        }
    }

    // ─── screenshot ─────────────────────────────────────────

    /**
     * Take a screenshot of the current page.
     */
    async screenshot(options?: {
        fullPage?: boolean;
        quality?: number;
        clip?: { x: number; y: number; width: number; height: number };
        timeout?: number;
        contextId?: number;
        pageId?: string;
    }): Promise<string> {
        this.ensureInitialized("screenshot");
        logOperationStart("BrowserAgent.screenshot", "");
        try {
            const args = stripNulls({
                context_id: options?.contextId ?? 0,
                page_id: options?.pageId,
                full_page: options?.fullPage ?? true,
                quality: options?.quality ?? 80,
                clip: options?.clip,
                timeout: options?.timeout,
            });
            const result = await this.callWithTimeout("page_use_screenshot", args);
            if (result.success && result.data) {
                logOperationSuccess("BrowserAgent.screenshot", "");
                return typeof result.data === "string"
                    ? result.data
                    : JSON.stringify(result.data);
            }
            return `Screenshot failed: ${result.errorMessage ?? "Unknown error"}`;
        } catch (e) {
            const msg = e instanceof Error ? e.message : String(e);
            throw new BrowserError(`Failed to take screenshot: ${msg}`);
        }
    }

    // ─── close ──────────────────────────────────────────────

    /**
     * Close the remote browser agent session.
     */
    async close(): Promise<boolean> {
        logOperationStart("BrowserAgent.close", "");
        try {
            const result = await this.callWithTimeout("page_use_close_session", {});
            if (result.success && result.data) {
                logInfo(`Session close status: ${result.data}`);
                logOperationSuccess("BrowserAgent.close", "");
                return true;
            }
            logWarn(`Failed to close session: ${result.errorMessage ?? "Unknown error"}`);
            return false;
        } catch (e) {
            const msg = e instanceof Error ? e.message : String(e);
            throw new BrowserError(`Failed to close session: ${msg}`);
        }
    }

    // ─── act (sync) ─────────────────────────────────────────

    /**
     * Perform an action on the web page (synchronous MCP call).
     */
    async act(
        actionInput: ActOptions | ObserveResult,
        contextId = 0,
        pageId?: string,
    ): Promise<ActResult> {
        this.ensureInitialized("act");
        const { args, taskName } = this.buildActArgs(actionInput, contextId, pageId);
        logOperationStart("BrowserAgent.act", taskName);

        const result = await this.callWithTimeout("page_use_act", args);
        if (result.success && result.data) {
            const data = typeof result.data === "string"
                ? result.data
                : JSON.stringify(result.data);
            logOperationSuccess("BrowserAgent.act", `${taskName}: ${data}`);
            return { success: true, message: data };
        }
        return { success: false, message: result.errorMessage ?? "" };
    }

    // ─── actAsync (polling with time-based timeout) ─────────

    /**
     * Perform an action asynchronously with polling until completion.
     * Timeout defaults to 300s and can be configured via ActOptions.timeout.
     */
    async actAsync(
        actionInput: ActOptions | ObserveResult,
        contextId = 0,
        pageId?: string,
    ): Promise<ActResult> {
        this.ensureInitialized("actAsync");
        const { args, taskName } = this.buildActArgs(actionInput, contextId, pageId);
        logOperationStart("BrowserAgent.actAsync", taskName);

        const startResult = await this.callWithTimeout("page_use_act_async", args);
        if (!startResult.success) {
            throw new BrowserError("Failed to start act task");
        }

        const parsed = typeof startResult.data === "string"
            ? JSON.parse(startResult.data)
            : startResult.data;
        const taskId = parsed.task_id as string;

        const clientTimeout = "action" in actionInput
            ? (actionInput as ActOptions).timeout
            : undefined;
        const timeoutS = clientTimeout ?? DEFAULT_CLIENT_TIMEOUT_S;
        const startTs = Date.now();
        const noActionMsg = "No actions have been executed.";

        while (true) {
            await sleep(POLL_INTERVAL_ACT);

            const pollResult = await this.callWithTimeout(
                "page_use_get_act_result",
                { task_id: taskId },
            );

            if (pollResult.success && pollResult.data) {
                const data = typeof pollResult.data === "string"
                    ? JSON.parse(pollResult.data)
                    : pollResult.data;
                const steps = data.steps ?? [];
                const isDone = Boolean(data.is_done);
                const success = Boolean(data.success);

                if (isDone) {
                    const msg = steps.length > 0 ? JSON.stringify(steps) : noActionMsg;
                    logInfo(`Task ${taskId}:${taskName} is done. Success: ${success}. ${msg}`);
                    return { success, message: msg };
                }

                const elapsed = (Date.now() - startTs) / 1000;
                const statusMsg = steps.length > 0
                    ? `${steps.length} steps done. Details: ${JSON.stringify(steps)}`
                    : noActionMsg;
                logInfo(`Task ${taskId}:${taskName} in progress. ${statusMsg}`);

                if (elapsed >= timeoutS) {
                    throw new BrowserError(
                        `Task ${taskId}:${taskName} timeout after ${timeoutS}s`,
                    );
                }
            } else {
                const elapsed = (Date.now() - startTs) / 1000;
                if (elapsed >= timeoutS) {
                    throw new BrowserError(
                        `Task ${taskId}:${taskName} timeout after ${timeoutS}s`,
                    );
                }
            }
        }
    }

    // ─── observe (sync) ─────────────────────────────────────

    /**
     * Observe elements or state on a web page.
     */
    async observe(
        options: ObserveOptions,
        contextId = 0,
        pageId?: string,
    ): Promise<{ success: boolean; results: ObserveResult[] }> {
        this.ensureInitialized("observe");
        logOperationStart("BrowserAgent.observe", options.instruction);

        const args = stripNulls({
            context_id: contextId,
            page_id: pageId,
            instruction: options.instruction,
            use_vision: options.useVision,
            selector: options.selector,
            iframes: options.iframes,
            dom_settle_timeout_ms: options.domSettleTimeoutMs,
        });

        const response = await this.callWithTimeout("page_use_observe", args);
        if (!response.success || !response.data) {
            logWarn(`Failed to execute observe: ${response.errorMessage}`);
            return { success: false, results: [] };
        }

        return {
            success: true,
            results: this.parseObserveData(response.data),
        };
    }

    // ─── observeAsync (polling with time-based timeout) ─────

    /**
     * Asynchronously observe elements on a web page with polling.
     * Timeout defaults to 300s and can be configured via ObserveOptions.timeout.
     */
    async observeAsync(
        options: ObserveOptions,
        contextId = 0,
        pageId?: string,
    ): Promise<{ success: boolean; results: ObserveResult[] }> {
        this.ensureInitialized("observeAsync");
        logOperationStart("BrowserAgent.observeAsync", options.instruction);

        const args = stripNulls({
            context_id: contextId,
            page_id: pageId,
            instruction: options.instruction,
            use_vision: options.useVision,
            selector: options.selector,
            iframes: options.iframes,
            dom_settle_timeout_ms: options.domSettleTimeoutMs,
        });

        const startResult = await this.callWithTimeout("page_use_observe_async", args);
        if (!startResult.success || !startResult.data) {
            throw new BrowserError("Failed to start observe task");
        }

        const parsed = typeof startResult.data === "string"
            ? JSON.parse(startResult.data)
            : startResult.data;
        const taskId = parsed.task_id as string;

        const timeoutS = options.timeout ?? DEFAULT_CLIENT_TIMEOUT_S;
        const startTs = Date.now();

        while (true) {
            await sleep(POLL_INTERVAL_OBSERVE);

            const pollResult = await this.callWithTimeout(
                "page_use_get_observe_result",
                { task_id: taskId },
            );

            if (pollResult.success && pollResult.data) {
                const results = this.parseObserveData(pollResult.data);
                logInfo(`observe results: ${JSON.stringify(results)}`);
                return { success: true, results };
            }

            const elapsed = (Date.now() - startTs) / 1000;
            logDebug(`Task ${taskId}: No observe result yet (elapsed=${elapsed.toFixed(0)}s)`);
            if (elapsed >= timeoutS) {
                throw new BrowserError(
                    `Task ${taskId}: Observe timeout after ${timeoutS}s`,
                );
            }
        }
    }

    // ─── extract (sync) ─────────────────────────────────────

    /**
     * Extract structured data from a web page (synchronous MCP call).
     */
    async extract<T = unknown>(
        options: ExtractOptions,
        contextId = 0,
        pageId?: string,
    ): Promise<ExtractResult<T>> {
        this.ensureInitialized("extract");
        logOperationStart("BrowserAgent.extract", options.instruction);

        const args = this.buildExtractArgs(options, contextId, pageId);
        const response = await this.callWithTimeout("page_use_extract", args);

        if (response.success && response.data) {
            const extractResult = typeof response.data === "string"
                ? JSON.parse(response.data)
                : response.data;
            logOperationSuccess("BrowserAgent.extract", JSON.stringify(extractResult));
            return { success: true, data: extractResult as T };
        }
        logWarn(`Failed to execute extract: ${response.errorMessage}`);
        return { success: false, data: null };
    }

    // ─── extractAsync (polling with time-based timeout) ─────

    /**
     * Extract structured data asynchronously with polling.
     * Timeout defaults to 300s and can be configured via ExtractOptions.timeout.
     */
    async extractAsync<T = unknown>(
        options: ExtractOptions,
        contextId = 0,
        pageId?: string,
    ): Promise<ExtractResult<T>> {
        this.ensureInitialized("extractAsync");
        logOperationStart("BrowserAgent.extractAsync", options.instruction);

        const args = this.buildExtractArgs(options, contextId, pageId);
        const startResult = await this.callWithTimeout("page_use_extract_async", args);

        if (!startResult.success || !startResult.data) {
            throw new BrowserError("Failed to start extract task");
        }

        const parsed = typeof startResult.data === "string"
            ? JSON.parse(startResult.data)
            : startResult.data;
        const taskId = parsed.task_id as string;

        const timeoutS = options.timeout ?? DEFAULT_CLIENT_TIMEOUT_S;
        const startTs = Date.now();

        while (true) {
            await sleep(POLL_INTERVAL_EXTRACT);

            const pollResult = await this.callWithTimeout(
                "page_use_get_extract_result",
                { task_id: taskId },
            );

            if (pollResult.success && pollResult.data) {
                const extractResult = typeof pollResult.data === "string"
                    ? JSON.parse(pollResult.data)
                    : pollResult.data;
                logOperationSuccess("BrowserAgent.extractAsync", JSON.stringify(extractResult));
                return { success: true, data: extractResult as T };
            }

            const elapsed = (Date.now() - startTs) / 1000;
            logDebug(`Task ${taskId}: No extract result yet (elapsed=${elapsed.toFixed(0)}s)`);
            if (elapsed >= timeoutS) {
                throw new BrowserError(
                    `Task ${taskId}: Extract timeout after ${timeoutS}s`,
                );
            }
        }
    }

    // ─── Private helpers ────────────────────────────────────

    private buildActArgs(
        actionInput: ActOptions | ObserveResult,
        contextId: number,
        pageId?: string,
    ): { args: Record<string, unknown>; taskName: string } {
        const base: Record<string, unknown> = {
            context_id: contextId,
            page_id: pageId,
        };
        let taskName: string;

        if ("action" in actionInput) {
            const opts = actionInput as ActOptions;
            Object.assign(base, {
                action: opts.action,
                variables: opts.variables,
                timeout: opts.timeout,
                use_vision: opts.useVision,
                iframes: opts.iframes,
                dom_settle_timeout_ms: opts.domSettleTimeoutMs,
            });
            taskName = opts.action;
        } else {
            const obs = actionInput as ObserveResult;
            const actionDict = {
                method: obs.method,
                arguments: obs.arguments,
            };
            base.action = JSON.stringify(actionDict);
            taskName = obs.method;
        }

        return { args: stripNulls(base), taskName };
    }

    private buildExtractArgs(
        options: ExtractOptions,
        contextId: number,
        pageId?: string,
    ): Record<string, unknown> {
        return stripNulls({
            context_id: contextId,
            page_id: pageId,
            instruction: options.instruction,
            field_schema: "schema: " + JSON.stringify(options.schema),
            use_text_extract: options.useTextExtract,
            use_vision: options.useVision,
            selector: options.selector,
            iframe: options.iframe,
            dom_settle_timeout_ms: options.domSettleTimeoutMs,
            max_page: options.maxPage,
        });
    }

    private parseObserveData(rawData: unknown): ObserveResult[] {
        const data = typeof rawData === "string"
            ? JSON.parse(rawData)
            : rawData;
        logDebug(`observe results: ${JSON.stringify(data)}`);

        const results: ObserveResult[] = [];
        if (Array.isArray(data)) {
            for (const item of data) {
                let parsedArgs: Record<string, unknown>;
                const rawArgs = item.arguments ?? "{}";
                if (typeof rawArgs === "string") {
                    try {
                        parsedArgs = JSON.parse(rawArgs);
                    } catch {
                        logWarn(`Could not parse arguments as JSON: ${rawArgs}`);
                        parsedArgs = {};
                    }
                } else {
                    parsedArgs = rawArgs;
                }
                results.push({
                    selector: item.selector ?? "",
                    description: item.description ?? "",
                    method: item.method ?? "",
                    arguments: parsedArgs,
                });
            }
        }

        logOperationSuccess("BrowserAgent.observe", `Found ${results.length} elements`);
        return results;
    }

    toJSON(): Record<string, unknown> {
        return { type: "BrowserAgent" };
    }
}
