/**
 * Integration tests for session features: labels, info, getLink, MCP tools, metrics.
 */
import { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import { createAGB, createTestSession, deleteTestSession } from "./setup";

jest.setTimeout(300_000);

describe("Session features (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    // --- Labels ---

    test("set and get labels", async () => {
        const labels = {
            environment: `test-${Date.now()}`,
            owner: "ts-integration",
        };

        const setResult = await session.setLabels(labels);
        expect(setResult.success).toBe(true);

        const getResult = await session.getLabels();
        expect(getResult.success).toBe(true);
        expect(getResult.data).toBeDefined();

        const retrieved = getResult.data as Record<string, string>;
        expect(retrieved.environment).toBe(labels.environment);
        expect(retrieved.owner).toBe(labels.owner);
    });

    test("set labels with empty object fails", async () => {
        const result = await session.setLabels({} as Record<string, string>);
        expect(result.success).toBe(false);
        expect(result.errorMessage).toBeTruthy();
    });

    test("update labels replaces old values", async () => {
        const initial = { key1: "val1", key2: "val2" };
        await session.setLabels(initial);

        const updated = { key1: "updated", key3: "new" };
        const setResult = await session.setLabels(updated);
        expect(setResult.success).toBe(true);

        const getResult = await session.getLabels();
        expect(getResult.success).toBe(true);
        const data = getResult.data as Record<string, string>;
        expect(data.key1).toBe("updated");
        expect(data.key3).toBe("new");
    });

    // --- Info ---

    test("session info", async () => {
        const result = await session.info();
        expect(result.success).toBe(true);
        expect(result.data).toBeDefined();

        const data = result.data as Record<string, unknown>;
        expect(data.sessionId).toBe(session.getSessionId());
    });

    // --- getLink ---

    test("session getLink", async () => {
        const result = await session.getLink();
        expect(result).toBeDefined();
        expect(result.requestId).toBeDefined();
    });

    // --- MCP Tools ---

    test("list MCP tools", async () => {
        const result = await session.listMcpTools();
        expect(result.success).toBe(true);
        expect(Array.isArray(result.tools)).toBe(true);
        expect(result.tools.length).toBeGreaterThan(0);

        const toolNames = result.tools.map((t) => t.name);
        expect(toolNames).toContain("shell");
        expect(toolNames).toContain("run_code");
    });

    test("list MCP tools with custom image ID", async () => {
        const result = await session.listMcpTools("agb-code-space-2");
        expect(result.success).toBe(true);
        expect(result.tools.length).toBeGreaterThan(0);
    });

    test("call MCP tool basic", async () => {
        const result = await session.callMcpTool("shell", {
            command: "echo mcp_test",
            timeout_ms: 5000,
        });
        expect(result.success).toBe(true);
        expect(result.data).toBeTruthy();
    });

    test("call MCP tool with timeouts", async () => {
        const result = await session.callMcpTool(
            "shell",
            { command: "echo timeout_test", timeout_ms: 5000 },
            60000,
            10000,
        );
        expect(result.success).toBe(true);
    });



    // --- Metrics ---

    test("get session metrics", async () => {
        const result = await session.getMetrics();
        expect(result.success).toBe(true);
        expect(result.metrics).toBeDefined();

        const m = result.metrics!;
        expect(typeof m.cpuCount).toBe("number");
        expect(typeof m.memTotal).toBe("number");
        expect(typeof m.diskTotal).toBe("number");
    });

    test("get session metrics with timeouts", async () => {
        const result = await session.getMetrics(60000, 10000);
        expect(result.success).toBe(true);
        expect(result.metrics).toBeDefined();
    });

    // --- getStatus ---

    test("get session status", async () => {
        const result = await session.getStatus();
        expect(result.success).toBe(true);
        expect(result.status).toBeTruthy();
    });
});
