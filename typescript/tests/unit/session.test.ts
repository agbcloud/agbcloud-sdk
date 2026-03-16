import type { AGB } from "../../src/session";
import { Session } from "../../src/session";

describe("Session", () => {
    const createMockClient = () => ({
        setLabel: jest.fn(),
        getLabel: jest.fn(),
        getMcpResource: jest.fn(),
        getLink: jest.fn(),
        deleteSessionAsync: jest.fn(),
        getSessionDetail: jest.fn(),
        callMcpTool: jest.fn(),
        listMcpTools: jest.fn(),
    });

    const createMockAGB = (client: ReturnType<typeof createMockClient>): AGB =>
        ({
            apiKey: "test-api-key",
            client,
        }) as unknown as AGB;

    describe("constructor initialization", () => {
        test("initializes with AGB and sessionId", () => {
            const mockClient = createMockClient();
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "test-session-id");

            expect(session.getSessionId()).toBe("test-session-id");
            expect(session.getApiKey()).toBe("test-api-key");
            expect(session.getClient()).toBe(mockClient);
        });

        test("initializes all modules", () => {
            const mockClient = createMockClient();
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "test-session-id");

            expect(session.command).toBeDefined();
            expect(session.file).toBeDefined();
            expect(session.code).toBeDefined();
            expect(session.browser).toBeDefined();
            expect(session.computer).toBeDefined();
            expect(session.context).toBeDefined();
        });

        test("stores session ID correctly", () => {
            const mockClient = createMockClient();
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "my-custom-session-123");

            expect(session.getSessionId()).toBe("my-custom-session-123");
        });
    });

    describe("getApiKey, getSessionId, getClient accessors", () => {
        test("getApiKey returns apiKey from AGB", () => {
            const mockClient = createMockClient();
            const mockAGB = createMockAGB(mockClient);
            mockAGB.apiKey = "custom-key-456";
            const session = new Session(mockAGB, "sid");

            expect(session.getApiKey()).toBe("custom-key-456");
        });

        test("getSessionId returns sessionId", () => {
            const mockClient = createMockClient();
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "session-xyz");

            expect(session.getSessionId()).toBe("session-xyz");
        });

        test("getClient returns client from AGB", () => {
            const mockClient = createMockClient();
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            expect(session.getClient()).toBe(mockClient);
        });
    });

    describe("_validateLabels (via setLabels)", () => {
        test("rejects null labels", async () => {
            const mockClient = createMockClient();
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.setLabels(null as unknown as Record<string, string>);

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("Labels cannot be null");
            expect(mockClient.setLabel).not.toHaveBeenCalled();
        });

        test("rejects undefined labels", async () => {
            const mockClient = createMockClient();
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.setLabels(undefined as unknown as Record<string, string>);

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("Labels cannot be null");
            expect(mockClient.setLabel).not.toHaveBeenCalled();
        });

        test("rejects array as labels", async () => {
            const mockClient = createMockClient();
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.setLabels(["a", "b"] as unknown as Record<string, string>);

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("Labels cannot be an array");
            expect(mockClient.setLabel).not.toHaveBeenCalled();
        });

        test("rejects empty object", async () => {
            const mockClient = createMockClient();
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.setLabels({});

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("Labels cannot be empty");
            expect(mockClient.setLabel).not.toHaveBeenCalled();
        });

        test("rejects empty key", async () => {
            const mockClient = createMockClient();
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.setLabels({ "": "value" });

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("Label keys cannot be empty");
            expect(mockClient.setLabel).not.toHaveBeenCalled();
        });

        test("rejects empty value", async () => {
            const mockClient = createMockClient();
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.setLabels({ key: "" });

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("Label values cannot be empty");
            expect(mockClient.setLabel).not.toHaveBeenCalled();
        });

        test("rejects whitespace-only value", async () => {
            const mockClient = createMockClient();
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.setLabels({ key: "   " });

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("Label values cannot be empty");
            expect(mockClient.setLabel).not.toHaveBeenCalled();
        });

        test("accepts valid labels object", async () => {
            const mockClient = createMockClient();
            mockClient.setLabel.mockResolvedValue({
                isSuccessful: () => true,
                getErrorMessage: () => "",
                requestId: "req-123",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.setLabels({ env: "prod", team: "backend" });

            expect(result.success).toBe(true);
            expect(mockClient.setLabel).toHaveBeenCalled();
        });
    });

    describe("setLabels", () => {
        test("returns success when client succeeds", async () => {
            const mockClient = createMockClient();
            mockClient.setLabel.mockResolvedValue({
                isSuccessful: () => true,
                getErrorMessage: () => "",
                requestId: "req-set-1",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.setLabels({ env: "test" });

            expect(result.success).toBe(true);
            expect(result.requestId).toBe("req-set-1");
        });

        test("returns failure when client fails", async () => {
            const mockClient = createMockClient();
            mockClient.setLabel.mockResolvedValue({
                isSuccessful: () => false,
                getErrorMessage: () => "API error",
                requestId: "req-set-2",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.setLabels({ env: "test" });

            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("API error");
        });
    });

    describe("getLabels", () => {
        test("returns success with labels data", async () => {
            const mockClient = createMockClient();
            mockClient.getLabel.mockResolvedValue({
                isSuccessful: () => true,
                getLabelsData: () => ({ labels: '{"env":"prod","team":"sdk"}' }),
                getErrorMessage: () => "",
                requestId: "req-get-1",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.getLabels();

            expect(result.success).toBe(true);
            expect(result.data).toEqual({ env: "prod", team: "sdk" });
        });

        test("returns success with empty labels when no labels in response", async () => {
            const mockClient = createMockClient();
            mockClient.getLabel.mockResolvedValue({
                isSuccessful: () => true,
                getLabelsData: () => ({}),
                getErrorMessage: () => "",
                requestId: "req-get-2",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.getLabels();

            expect(result.success).toBe(true);
            expect(result.data).toEqual({});
        });

        test("returns success with empty labels when labels string is invalid JSON", async () => {
            const mockClient = createMockClient();
            mockClient.getLabel.mockResolvedValue({
                isSuccessful: () => true,
                getLabelsData: () => ({ labels: "not valid json {" }),
                getErrorMessage: () => "",
                requestId: "req-get-2",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.getLabels();

            expect(result.success).toBe(true);
            expect(result.data).toEqual({});
        });

        test("returns failure when client fails", async () => {
            const mockClient = createMockClient();
            mockClient.getLabel.mockResolvedValue({
                isSuccessful: () => false,
                getLabelsData: () => undefined,
                getErrorMessage: () => "Not found",
                requestId: "req-get-3",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.getLabels();

            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("Not found");
        });
    });

    describe("info", () => {
        test("returns success with resource data", async () => {
            const mockClient = createMockClient();
            mockClient.getMcpResource.mockResolvedValue({
                isSuccessful: () => true,
                getResourceData: () => ({
                    sessionId: "sid-1",
                    resourceUrl: "https://example.com",
                    desktopInfo: { appId: "app1", resourceId: "res1" },
                }),
                getErrorMessage: () => "",
                requestId: "req-info-1",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.info();

            expect(result.success).toBe(true);
            expect(result.data).toBeDefined();
            expect((result.data as Record<string, unknown>).sessionId).toBe("sid-1");
            expect((result.data as Record<string, unknown>).resourceUrl).toBe("https://example.com");
        });

        test("returns success with desktopInfo fields when present", async () => {
            const mockClient = createMockClient();
            mockClient.getMcpResource.mockResolvedValue({
                isSuccessful: () => true,
                getResourceData: () => ({
                    sessionId: "sid-1",
                    resourceUrl: "https://example.com",
                    desktopInfo: {
                        appId: "app1",
                        authCode: "auth123",
                        connectionProperties: { prop: "val" },
                        resourceId: "res1",
                        resourceType: "desktop",
                        ticket: "ticket123",
                    },
                }),
                getErrorMessage: () => "",
                requestId: "req-info-1",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.info();

            expect(result.success).toBe(true);
            const data = result.data as Record<string, unknown>;
            expect(data.appId).toBe("app1");
            expect(data.authCode).toBe("auth123");
            expect(data.resourceId).toBe("res1");
            expect(data.resourceType).toBe("desktop");
            expect(data.ticket).toBe("ticket123");
        });

        test("returns failure when response is null", async () => {
            const mockClient = createMockClient();
            mockClient.getMcpResource.mockResolvedValue(null);
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.info();

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("None response");
        });

        test("returns failure when successful but no resource data", async () => {
            const mockClient = createMockClient();
            mockClient.getMcpResource.mockResolvedValue({
                isSuccessful: () => true,
                getResourceData: () => undefined,
                getErrorMessage: () => "",
                requestId: "req-info-2",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.info();

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("No resource data found");
        });
    });

    describe("delete", () => {
        test("returns success when session is deleted and getStatus returns FINISH", async () => {
            const mockClient = createMockClient();
            mockClient.deleteSessionAsync.mockResolvedValue({
                isSuccessful: () => true,
                body: {},
                requestId: "req-del-1",
            });
            mockClient.getSessionDetail.mockResolvedValue({
                isSuccessful: () => true,
                getStatus: () => "FINISH",
                getErrorMessage: () => "",
                requestId: "req-status-1",
                httpStatusCode: 200,
                code: "",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.delete(false);

            expect(result.success).toBe(true);
            expect(mockClient.deleteSessionAsync).toHaveBeenCalled();
            expect(mockClient.getSessionDetail).toHaveBeenCalled();
        });

        test("returns success when getStatus returns not found (session already deleted)", async () => {
            const mockClient = createMockClient();
            mockClient.deleteSessionAsync.mockResolvedValue({
                isSuccessful: () => true,
                body: {},
                requestId: "req-del-2",
            });
            mockClient.getSessionDetail.mockResolvedValue({
                isSuccessful: () => false,
                getStatus: () => "",
                getErrorMessage: () => "session not found",
                requestId: "req-status-2",
                httpStatusCode: 400,
                code: "InvalidMcpSession.NotFound",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.delete(false);

            expect(result.success).toBe(true);
        });
    });

    describe("callMcpTool", () => {
        test("returns success with tool result", async () => {
            const mockClient = createMockClient();
            mockClient.callMcpTool.mockResolvedValue({
                isSuccessful: () => true,
                getToolResult: () => '{"output":"hello"}',
                getErrorMessage: () => undefined,
                requestId: "req-call-1",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.callMcpTool("run_command", { cmd: "echo hi" });

            expect(result.success).toBe(true);
            expect(result.data).toBe('{"output":"hello"}');
        });

        test("returns failure when client fails", async () => {
            const mockClient = createMockClient();
            mockClient.callMcpTool.mockResolvedValue({
                isSuccessful: () => false,
                getToolResult: () => undefined,
                getErrorMessage: () => "Tool execution failed",
                requestId: "req-call-2",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.callMcpTool("run_command", {});

            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("Tool execution failed");
        });

        test("returns failure when response is null", async () => {
            const mockClient = createMockClient();
            mockClient.callMcpTool.mockResolvedValue(null);
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.callMcpTool("run_command", {});

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("null response");
        });
    });

    describe("listMcpTools", () => {
        test("returns success with tools list", async () => {
            const toolsJson = JSON.stringify([
                {
                    name: "run_command",
                    description: "Run a command",
                    inputSchema: {},
                    server: "command",
                    tool: "run_command",
                },
            ]);
            const mockClient = createMockClient();
            mockClient.listMcpTools.mockResolvedValue({
                isSuccessful: () => true,
                getToolsList: () => toolsJson,
                getErrorMessage: () => undefined,
                requestId: "req-list-1",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");
            session.imageId = "agb-code-space-1";

            const result = await session.listMcpTools();

            expect(result.success).toBe(true);
            expect(result.tools).toHaveLength(1);
            expect(result.tools[0].name).toBe("run_command");
            expect(result.tools[0].description).toBe("Run a command");
        });

        test("returns failure when client fails", async () => {
            const mockClient = createMockClient();
            mockClient.listMcpTools.mockResolvedValue({
                isSuccessful: () => false,
                getToolsList: () => undefined,
                getErrorMessage: () => "API error",
                requestId: "req-list-2",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");
            session.imageId = "agb-code-space-1";

            const result = await session.listMcpTools();

            expect(result.success).toBe(false);
            expect(result.tools).toEqual([]);
            expect(result.errorMessage).toBe("API error");
        });

        test("returns failure when tools list is invalid JSON", async () => {
            const mockClient = createMockClient();
            mockClient.listMcpTools.mockResolvedValue({
                isSuccessful: () => true,
                getToolsList: () => "not valid json {{{",
                getErrorMessage: () => undefined,
                requestId: "req-list-3",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");
            session.imageId = "agb-code-space-1";

            const result = await session.listMcpTools();

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("Failed to parse tools list");
        });

        test("throws error when imageId is not set", async () => {
            const mockClient = createMockClient();
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            await expect(session.listMcpTools()).rejects.toThrow(
                "imageId is required",
            );
        });
    });

    describe("getMetrics", () => {
        test("returns success with parsed metrics", async () => {
            const metricsData = {
                cpu_count: 4,
                cpu_used_pct: 25.5,
                disk_total: 1000000,
                disk_used: 500000,
                mem_total: 8000,
                mem_used: 2000,
                rx_rate_kbyte_per_s: 100,
                tx_rate_kbyte_per_s: 50,
                rx_used_kbyte: 1000,
                tx_used_kbyte: 500,
                timestamp: "2025-01-01T00:00:00Z",
            };
            const mockClient = createMockClient();
            mockClient.callMcpTool.mockResolvedValue({
                isSuccessful: () => true,
                getToolResult: () => JSON.stringify(metricsData),
                getErrorMessage: () => undefined,
                requestId: "req-metrics-1",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.getMetrics();

            expect(result.success).toBe(true);
            expect(result.metrics).toBeDefined();
            expect(result.metrics?.cpuCount).toBe(4);
            expect(result.metrics?.cpuUsedPct).toBe(25.5);
            expect(result.metrics?.diskTotal).toBe(1000000);
            expect(result.metrics?.memTotal).toBe(8000);
        });

        test("returns failure when callMcpTool fails", async () => {
            const mockClient = createMockClient();
            mockClient.callMcpTool.mockResolvedValue({
                isSuccessful: () => false,
                getToolResult: () => undefined,
                getErrorMessage: () => "Tool failed",
                requestId: "req-metrics-2",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.getMetrics();

            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("Tool failed");
        });

        test("returns failure when get_metrics returns invalid JSON", async () => {
            const mockClient = createMockClient();
            mockClient.callMcpTool.mockResolvedValue({
                isSuccessful: () => true,
                getToolResult: () => "not json {{{",
                getErrorMessage: () => undefined,
                requestId: "req-metrics-3",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.getMetrics();

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("Failed to parse get_metrics");
        });
    });

    describe("getStatus", () => {
        test("returns success with status", async () => {
            const mockClient = createMockClient();
            mockClient.getSessionDetail.mockResolvedValue({
                isSuccessful: () => true,
                getStatus: () => "RUNNING",
                getErrorMessage: () => "",
                requestId: "req-status-1",
                httpStatusCode: 200,
                code: "",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.getStatus();

            expect(result.success).toBe(true);
            expect(result.status).toBe("RUNNING");
        });

        test("returns failure when client fails", async () => {
            const mockClient = createMockClient();
            mockClient.getSessionDetail.mockResolvedValue({
                isSuccessful: () => false,
                getStatus: () => "",
                getErrorMessage: () => "Session not found",
                requestId: "req-status-2",
                httpStatusCode: 404,
                code: "NotFound",
            });
            const mockAGB = createMockAGB(mockClient);
            const session = new Session(mockAGB, "sid");

            const result = await session.getStatus();

            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("Session not found");
        });
    });
});
