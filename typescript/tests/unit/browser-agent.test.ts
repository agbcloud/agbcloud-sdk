import { BrowserAgent } from "../../src/modules/browser/browser-agent";
import type {
    ActOptions,
    ObserveOptions,
    ExtractOptions,
    ObserveResult,
} from "../../src/modules/browser/browser-agent";
import { BrowserError } from "../../src/exceptions";

function createMockSession() {
    return {
        getApiKey: () => "test-key",
        getSessionId: () => "test-session",
        getClient: () => ({}),
    };
}

function createMockBrowser(initialized = true) {
    return { isInitialized: () => initialized };
}

describe("BrowserAgent", () => {
    let agent: BrowserAgent;
    let spy: jest.SpyInstance;

    beforeEach(() => {
        const session = createMockSession();
        const browser = createMockBrowser(true);
        agent = new BrowserAgent(session, browser);
        spy = jest.spyOn(agent as any, "callMcpTool");
    });
    afterEach(() => spy.mockRestore());

    // ─── ensureInitialized ──────────────────────────────────

    describe("initialization check", () => {
        test("throws BrowserError when browser not initialized", async () => {
            const session = createMockSession();
            const browser = createMockBrowser(false);
            const uninitAgent = new BrowserAgent(session, browser);

            await expect(uninitAgent.navigate("https://example.com")).rejects.toThrow(BrowserError);
            await expect(uninitAgent.act({ action: "click" })).rejects.toThrow(BrowserError);
            await expect(uninitAgent.observe({ instruction: "find button" })).rejects.toThrow(BrowserError);
            await expect(uninitAgent.observeAsync({ instruction: "find button" })).rejects.toThrow(BrowserError);
            await expect(uninitAgent.extract({ instruction: "get data", schema: {} })).rejects.toThrow(BrowserError);
            await expect(uninitAgent.extractAsync({ instruction: "get data", schema: {} })).rejects.toThrow(BrowserError);
        });
    });

    // ─── navigate ───────────────────────────────────────────

    describe("navigate", () => {
        test("success", async () => {
            spy.mockResolvedValue({
                requestId: "req-nav", success: true,
                data: "Navigation successful",
            });
            const result = await agent.navigate("https://example.com");
            expect(result).toBe("Navigation successful");
            expect(spy).toHaveBeenCalledWith(
                "page_use_navigate",
                { url: "https://example.com" },
                60000, 60000,
            );
        });

        test("success with object data", async () => {
            spy.mockResolvedValue({
                requestId: "req-nav2", success: true,
                data: { status: "ok" },
            });
            const result = await agent.navigate("https://example.com");
            expect(result).toBe('{"status":"ok"}');
        });

        test("failure returns error message", async () => {
            spy.mockResolvedValue({
                requestId: "req-navf", success: false,
                errorMessage: "Page not found",
            });
            const result = await agent.navigate("https://404.example.com");
            expect(result).toBe("Navigation failed: Page not found");
        });

        test("exception throws BrowserError", async () => {
            spy.mockRejectedValue(new Error("Network error"));
            await expect(agent.navigate("https://fail.com")).rejects.toThrow(BrowserError);
        });
    });

    // ─── screenshot ────────────────────────────────────

    describe("screenshot", () => {
        test("success with defaults", async () => {
            spy.mockResolvedValue({
                requestId: "req-ss", success: true,
                data: "data:image/png;base64,...",
            });
            const result = await agent.screenshot();
            expect(result).toContain("data:image/png");
            expect(spy).toHaveBeenCalledWith(
                "page_use_screenshot",
                expect.objectContaining({ context_id: 0, full_page: true, quality: 80 }),
                60000, 60000,
            );
        });

        test("success with custom options", async () => {
            spy.mockResolvedValue({
                requestId: "req-ss2", success: true,
                data: "base64data",
            });
            await agent.screenshot({
                fullPage: false,
                quality: 50,
                contextId: 1,
                pageId: "page-1",
            });
            expect(spy).toHaveBeenCalledWith(
                "page_use_screenshot",
                expect.objectContaining({
                    context_id: 1, page_id: "page-1",
                    full_page: false, quality: 50,
                }),
                60000, 60000,
            );
        });

        test("failure returns error string", async () => {
            spy.mockResolvedValue({
                requestId: "req-ssf", success: false,
                errorMessage: "Screenshot error",
            });
            const result = await agent.screenshot();
            expect(result).toContain("Screenshot failed");
        });

        test("exception throws BrowserError", async () => {
            spy.mockRejectedValue(new Error("Timeout"));
            await expect(agent.screenshot()).rejects.toThrow(BrowserError);
        });
    });

    // ─── close ──────────────────────────────────────────────

    describe("close", () => {
        test("success", async () => {
            spy.mockResolvedValue({
                requestId: "req-close", success: true, data: "closed",
            });
            const result = await agent.close();
            expect(result).toBe(true);
        });

        test("failure returns false", async () => {
            spy.mockResolvedValue({
                requestId: "req-closef", success: false,
                errorMessage: "Close failed",
            });
            const result = await agent.close();
            expect(result).toBe(false);
        });

        test("exception throws BrowserError", async () => {
            spy.mockRejectedValue(new Error("Connection lost"));
            await expect(agent.close()).rejects.toThrow(BrowserError);
        });
    });

    // ─── act ────────────────────────────────────────────────

    describe("act", () => {
        test("success with ActOptions", async () => {
            spy.mockResolvedValue({
                requestId: "req-act", success: true,
                data: "Action completed",
            });
            const options: ActOptions = {
                action: "click button",
                useVision: true,
            };
            const result = await agent.act(options);
            expect(result.success).toBe(true);
            expect(result.message).toBe("Action completed");
            expect(spy).toHaveBeenCalledWith(
                "page_use_act",
                expect.objectContaining({
                    context_id: 0,
                    action: "click button",
                    use_vision: true,
                }),
                60000, 60000,
            );
        });

        test("success with all ActOptions fields", async () => {
            spy.mockResolvedValue({
                requestId: "req-act2", success: true,
                data: '{"done": true}',
            });
            const options: ActOptions = {
                action: "fill form",
                variables: { name: "John" },
                timeout: 5000,
                iframes: true,
                domSettleTimeoutMs: 1000,
            };
            const result = await agent.act(options, 1, "page-1");
            expect(result.success).toBe(true);
            expect(spy).toHaveBeenCalledWith(
                "page_use_act",
                expect.objectContaining({
                    context_id: 1,
                    page_id: "page-1",
                    action: "fill form",
                    variables: { name: "John" },
                    timeout: 5000,
                    iframes: true,
                    dom_settle_timeout_ms: 1000,
                }),
                60000, 60000,
            );
        });

        test("success with ObserveResult input", async () => {
            spy.mockResolvedValue({
                requestId: "req-act3", success: true,
                data: "Clicked",
            });
            const observeResult: ObserveResult = {
                selector: "#btn",
                description: "Submit button",
                method: "click",
                arguments: { x: 100, y: 200 },
            };
            const result = await agent.act(observeResult);
            expect(result.success).toBe(true);
            expect(spy).toHaveBeenCalledWith(
                "page_use_act",
                expect.objectContaining({
                    context_id: 0,
                    action: JSON.stringify({ method: "click", arguments: { x: 100, y: 200 } }),
                }),
                60000, 60000,
            );
        });

        test("failure", async () => {
            spy.mockResolvedValue({
                requestId: "req-actf", success: false,
                errorMessage: "Element not found",
            });
            const result = await agent.act({ action: "click missing" });
            expect(result.success).toBe(false);
            expect(result.message).toBe("Element not found");
        });
    });

    // ─── actAsync ───────────────────────────────────────────

    describe("actAsync", () => {
        test("success after polling", async () => {
            spy
                .mockResolvedValueOnce({
                    requestId: "req-start", success: true,
                    data: JSON.stringify({ task_id: "task-1" }),
                })
                .mockResolvedValueOnce({
                    requestId: "req-poll1", success: true,
                    data: JSON.stringify({ steps: ["step1"], is_done: false, success: false }),
                })
                .mockResolvedValueOnce({
                    requestId: "req-poll2", success: true,
                    data: JSON.stringify({ steps: ["step1", "step2"], is_done: true, success: true }),
                });

            jest.useFakeTimers();
            const promise = agent.actAsync({ action: "fill form" });
            await jest.advanceTimersByTimeAsync(5000);
            await jest.advanceTimersByTimeAsync(5000);
            const result = await promise;
            jest.useRealTimers();

            expect(result.success).toBe(true);
            expect(result.message).toContain("step1");
        });

        test("failure to start throws", async () => {
            spy.mockResolvedValue({
                requestId: "req-startf", success: false,
                errorMessage: "Cannot start",
            });
            await expect(agent.actAsync({ action: "click" })).rejects.toThrow(
                "Failed to start act task",
            );
        });

        test("done with no steps", async () => {
            spy
                .mockResolvedValueOnce({
                    requestId: "req-start", success: true,
                    data: JSON.stringify({ task_id: "task-2" }),
                })
                .mockResolvedValueOnce({
                    requestId: "req-poll", success: true,
                    data: JSON.stringify({ steps: [], is_done: true, success: true }),
                });

            jest.useFakeTimers();
            const promise = agent.actAsync({ action: "noop" });
            await jest.advanceTimersByTimeAsync(5000);
            const result = await promise;
            jest.useRealTimers();

            expect(result.success).toBe(true);
            expect(result.message).toBe("No actions have been executed.");
        });

        test("timeout based on time (default 300s)", async () => {
            spy
                .mockResolvedValueOnce({
                    requestId: "req-start", success: true,
                    data: JSON.stringify({ task_id: "task-timeout" }),
                })
                .mockResolvedValue({
                    requestId: "req-poll", success: true,
                    data: JSON.stringify({ steps: [], is_done: false, success: false }),
                });

            jest.useFakeTimers();
            const promise = agent.actAsync({ action: "slow task" });
            let error: Error | undefined;
            promise.catch((e) => { error = e; });

            for (let i = 0; i < 62; i++) {
                await jest.advanceTimersByTimeAsync(5000);
            }
            await jest.advanceTimersByTimeAsync(0);

            expect(error).toBeDefined();
            expect(error!.message).toMatch(/timeout after 300s/);
            jest.useRealTimers();
        });

        test("timeout with custom timeout value", async () => {
            spy
                .mockResolvedValueOnce({
                    requestId: "req-start", success: true,
                    data: JSON.stringify({ task_id: "task-ct" }),
                })
                .mockResolvedValue({
                    requestId: "req-poll", success: true,
                    data: JSON.stringify({ steps: [], is_done: false, success: false }),
                });

            jest.useFakeTimers();
            const promise = agent.actAsync({ action: "quick task", timeout: 10 });
            let error: Error | undefined;
            promise.catch((e) => { error = e; });

            for (let i = 0; i < 4; i++) {
                await jest.advanceTimersByTimeAsync(5000);
            }
            await jest.advanceTimersByTimeAsync(0);

            expect(error).toBeDefined();
            expect(error!.message).toMatch(/timeout after 10s/);
            jest.useRealTimers();
        });

        test("timeout on poll failure", async () => {
            spy
                .mockResolvedValueOnce({
                    requestId: "req-start", success: true,
                    data: JSON.stringify({ task_id: "task-pf" }),
                })
                .mockResolvedValue({
                    requestId: "req-poll", success: false,
                    errorMessage: "Poll error",
                });

            jest.useFakeTimers();
            const promise = agent.actAsync({ action: "failing", timeout: 8 });
            let error: Error | undefined;
            promise.catch((e) => { error = e; });

            for (let i = 0; i < 3; i++) {
                await jest.advanceTimersByTimeAsync(5000);
            }
            await jest.advanceTimersByTimeAsync(0);

            expect(error).toBeDefined();
            expect(error!.message).toMatch(/timeout after 8s/);
            jest.useRealTimers();
        });
    });

    // ─── observe ────────────────────────────────────────────

    describe("observe", () => {
        test("success with results", async () => {
            spy.mockResolvedValue({
                requestId: "req-obs", success: true,
                data: JSON.stringify([
                    { selector: "#login", description: "Login button", method: "click", arguments: '{"x": 10}' },
                    { selector: "#input", description: "Email field", method: "fill", arguments: { value: "test@test.com" } },
                ]),
            });
            const result = await agent.observe({ instruction: "Find login elements" });
            expect(result.success).toBe(true);
            expect(result.results).toHaveLength(2);
            expect(result.results[0].arguments).toEqual({ x: 10 });
            expect(result.results[1].arguments).toEqual({ value: "test@test.com" });
        });

        test("with selector option", async () => {
            spy.mockResolvedValue({
                requestId: "req-obs2", success: true,
                data: "[]",
            });
            await agent.observe({
                instruction: "find all",
                selector: "#main-content",
                useVision: true,
                iframes: true,
                domSettleTimeoutMs: 2000,
            }, 1, "page-2");
            expect(spy).toHaveBeenCalledWith(
                "page_use_observe",
                expect.objectContaining({
                    context_id: 1,
                    page_id: "page-2",
                    instruction: "find all",
                    selector: "#main-content",
                    use_vision: true,
                    iframes: true,
                    dom_settle_timeout_ms: 2000,
                }),
                60000, 60000,
            );
        });

        test("failure returns empty results", async () => {
            spy.mockResolvedValue({
                requestId: "req-obsf", success: false,
                errorMessage: "Observe failed",
            });
            const result = await agent.observe({ instruction: "observe" });
            expect(result.success).toBe(false);
            expect(result.results).toEqual([]);
        });

        test("handles invalid JSON arguments gracefully", async () => {
            spy.mockResolvedValue({
                requestId: "req-obs4", success: true,
                data: JSON.stringify([
                    { selector: "#x", description: "X", method: "click", arguments: "not-valid-json" },
                ]),
            });
            const result = await agent.observe({ instruction: "test" });
            expect(result.success).toBe(true);
            expect(result.results[0].arguments).toEqual({});
        });
    });

    // ─── observeAsync ───────────────────────────────────────

    describe("observeAsync", () => {
        test("success after polling", async () => {
            spy
                .mockResolvedValueOnce({
                    requestId: "req-obs-start", success: true,
                    data: JSON.stringify({ task_id: "obs-task-1" }),
                })
                .mockResolvedValueOnce({
                    requestId: "req-obs-poll", success: true,
                    data: JSON.stringify([
                        { selector: "#btn", description: "Button", method: "click", arguments: {} },
                    ]),
                });

            jest.useFakeTimers();
            const promise = agent.observeAsync({ instruction: "find buttons" });
            await jest.advanceTimersByTimeAsync(5000);
            const result = await promise;
            jest.useRealTimers();

            expect(result.success).toBe(true);
            expect(result.results).toHaveLength(1);
            expect(result.results[0].selector).toBe("#btn");
        });

        test("failure to start throws", async () => {
            spy.mockResolvedValue({
                requestId: "req-obs-sf", success: false,
                errorMessage: "Cannot start",
            });
            await expect(
                agent.observeAsync({ instruction: "find" }),
            ).rejects.toThrow("Failed to start observe task");
        });

        test("timeout with default 300s", async () => {
            spy
                .mockResolvedValueOnce({
                    requestId: "req-obs-start", success: true,
                    data: JSON.stringify({ task_id: "obs-timeout" }),
                })
                .mockResolvedValue({
                    requestId: "req-obs-poll", success: false,
                    errorMessage: "not ready",
                });

            jest.useFakeTimers();
            const promise = agent.observeAsync({ instruction: "slow" });
            let error: Error | undefined;
            promise.catch((e) => { error = e; });

            for (let i = 0; i < 62; i++) {
                await jest.advanceTimersByTimeAsync(5000);
            }
            await jest.advanceTimersByTimeAsync(0);

            expect(error).toBeDefined();
            expect(error!.message).toMatch(/Observe timeout after 300s/);
            jest.useRealTimers();
        });

        test("timeout with custom value", async () => {
            spy
                .mockResolvedValueOnce({
                    requestId: "req-obs-start", success: true,
                    data: JSON.stringify({ task_id: "obs-ct" }),
                })
                .mockResolvedValue({
                    requestId: "req-obs-poll", success: false,
                    errorMessage: "not ready",
                });

            jest.useFakeTimers();
            const promise = agent.observeAsync({ instruction: "quick", timeout: 8 });
            let error: Error | undefined;
            promise.catch((e) => { error = e; });

            for (let i = 0; i < 3; i++) {
                await jest.advanceTimersByTimeAsync(5000);
            }
            await jest.advanceTimersByTimeAsync(0);

            expect(error).toBeDefined();
            expect(error!.message).toMatch(/Observe timeout after 8s/);
            jest.useRealTimers();
        });

        test("with selector and options", async () => {
            spy
                .mockResolvedValueOnce({
                    requestId: "req-obs-start", success: true,
                    data: JSON.stringify({ task_id: "obs-sel" }),
                })
                .mockResolvedValueOnce({
                    requestId: "req-obs-poll", success: true,
                    data: "[]",
                });

            jest.useFakeTimers();
            const promise = agent.observeAsync({
                instruction: "find",
                selector: "#app",
                useVision: false,
            }, 2, "page-5");
            await jest.advanceTimersByTimeAsync(5000);
            await promise;
            jest.useRealTimers();

            expect(spy).toHaveBeenNthCalledWith(
                1,
                "page_use_observe_async",
                expect.objectContaining({
                    context_id: 2,
                    page_id: "page-5",
                    selector: "#app",
                    use_vision: false,
                }),
                60000, 60000,
            );
        });
    });

    // ─── extract ────────────────────────────────────────────

    describe("extract", () => {
        test("success", async () => {
            spy.mockResolvedValue({
                requestId: "req-ext", success: true,
                data: JSON.stringify({ title: "Hello", price: 9.99 }),
            });
            const result = await agent.extract({
                instruction: "Get product info",
                schema: { type: "object" },
            });
            expect(result.success).toBe(true);
            expect(result.data).toEqual({ title: "Hello", price: 9.99 });
        });

        test("with maxPage and all options", async () => {
            spy.mockResolvedValue({
                requestId: "req-ext2", success: true,
                data: '{"name": "test"}',
            });
            await agent.extract({
                instruction: "extract name",
                schema: { type: "object" },
                useTextExtract: true,
                useVision: false,
                selector: "#content",
                iframe: true,
                domSettleTimeoutMs: 3000,
                maxPage: 5,
            }, 1, "page-3");
            expect(spy).toHaveBeenCalledWith(
                "page_use_extract",
                expect.objectContaining({
                    context_id: 1,
                    page_id: "page-3",
                    use_text_extract: true,
                    use_vision: false,
                    selector: "#content",
                    iframe: true,
                    dom_settle_timeout_ms: 3000,
                    max_page: 5,
                }),
                60000, 60000,
            );
        });

        test("failure returns null data", async () => {
            spy.mockResolvedValue({
                requestId: "req-extf", success: false,
                errorMessage: "Extract failed",
            });
            const result = await agent.extract({ instruction: "get data", schema: {} });
            expect(result.success).toBe(false);
            expect(result.data).toBeNull();
        });
    });

    // ─── extractAsync ───────────────────────────────────────

    describe("extractAsync", () => {
        test("success after polling", async () => {
            spy
                .mockResolvedValueOnce({
                    requestId: "req-exts", success: true,
                    data: JSON.stringify({ task_id: "ext-task-1" }),
                })
                .mockResolvedValueOnce({
                    requestId: "req-extpoll", success: true,
                    data: JSON.stringify({ name: "Product", price: 29.99 }),
                });

            jest.useFakeTimers();
            const promise = agent.extractAsync({ instruction: "get product", schema: { type: "object" } });
            await jest.advanceTimersByTimeAsync(8000);
            const result = await promise;
            jest.useRealTimers();

            expect(result.success).toBe(true);
            expect(result.data).toEqual({ name: "Product", price: 29.99 });
        });

        test("failure to start throws", async () => {
            spy.mockResolvedValue({
                requestId: "req-extsf", success: false,
                errorMessage: "Cannot start",
            });
            await expect(
                agent.extractAsync({ instruction: "get", schema: {} }),
            ).rejects.toThrow("Failed to start extract task");
        });

        test("timeout with default 300s", async () => {
            spy
                .mockResolvedValueOnce({
                    requestId: "req-ext-start", success: true,
                    data: JSON.stringify({ task_id: "ext-timeout" }),
                })
                .mockResolvedValue({
                    requestId: "req-ext-poll", success: false,
                    errorMessage: "not ready",
                });

            jest.useFakeTimers();
            const promise = agent.extractAsync({ instruction: "slow", schema: {} });
            let error: Error | undefined;
            promise.catch((e) => { error = e; });

            for (let i = 0; i < 39; i++) {
                await jest.advanceTimersByTimeAsync(8000);
            }
            await jest.advanceTimersByTimeAsync(0);

            expect(error).toBeDefined();
            expect(error!.message).toMatch(/Extract timeout after 300s/);
            jest.useRealTimers();
        });

        test("timeout with custom value", async () => {
            spy
                .mockResolvedValueOnce({
                    requestId: "req-ext-start", success: true,
                    data: JSON.stringify({ task_id: "ext-ct" }),
                })
                .mockResolvedValue({
                    requestId: "req-ext-poll", success: false,
                    errorMessage: "not ready",
                });

            jest.useFakeTimers();
            const promise = agent.extractAsync({
                instruction: "quick",
                schema: {},
                timeout: 12,
            });
            let error: Error | undefined;
            promise.catch((e) => { error = e; });

            for (let i = 0; i < 3; i++) {
                await jest.advanceTimersByTimeAsync(8000);
            }
            await jest.advanceTimersByTimeAsync(0);

            expect(error).toBeDefined();
            expect(error!.message).toMatch(/Extract timeout after 12s/);
            jest.useRealTimers();
        });

        test("with maxPage option", async () => {
            spy
                .mockResolvedValueOnce({
                    requestId: "req-ext-start", success: true,
                    data: JSON.stringify({ task_id: "ext-mp" }),
                })
                .mockResolvedValueOnce({
                    requestId: "req-ext-poll", success: true,
                    data: '{"result": "ok"}',
                });

            jest.useFakeTimers();
            const promise = agent.extractAsync({
                instruction: "get all",
                schema: { type: "object" },
                maxPage: 10,
            });
            await jest.advanceTimersByTimeAsync(8000);
            await promise;
            jest.useRealTimers();

            expect(spy).toHaveBeenNthCalledWith(
                1,
                "page_use_extract_async",
                expect.objectContaining({ max_page: 10 }),
                60000, 60000,
            );
        });
    });

    // ─── toJSON ─────────────────────────────────────────────

    describe("toJSON", () => {
        test("returns type BrowserAgent", () => {
            expect(agent.toJSON()).toEqual({ type: "BrowserAgent" });
        });
    });
});

// ─── Browser.agent integration ──────────────────────────────

describe("Browser has agent property", () => {
    test("Browser exposes agent as BrowserAgent", async () => {
        const { Browser } = await import("../../src/modules/browser/browser");
        const session = {
            getApiKey: () => "key",
            getSessionId: () => "sid",
            getClient: () => ({}),
        };
        const browser = new Browser(session);
        expect(browser.agent).toBeInstanceOf(BrowserAgent);
    });
});
