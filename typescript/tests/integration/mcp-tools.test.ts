/**
 * Integration tests for MCP tools: listMcpTools, callMcpTool, getMetrics.
 */
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";

jest.setTimeout(300_000);

describe("MCP Tools (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    test("listMcpTools returns tools array", async () => {
        const result = await session.listMcpTools();
        expect(result.success).toBe(true);
        expect(Array.isArray(result.tools)).toBe(true);
        expect(result.tools.length).toBeGreaterThan(0);
    });

    test("listMcpTools includes known tools", async () => {
        const result = await session.listMcpTools();
        expect(result.success).toBe(true);
        const toolNames = result.tools.map((t) => t.name);
        expect(toolNames).toContain("run_code");
        expect(toolNames).toContain("write_file");
        expect(toolNames).toContain("read_file");
    });

    test("callMcpTool read_file", async () => {
        await session.file.write("/tmp/mcp-test.txt", "mcp-read-test");
        const result = await session.callMcpTool("read_file", {
            path: "/tmp/mcp-test.txt",
        });
        expect(result.success).toBe(true);
        expect(result.data).toBeDefined();
    });

    test("callMcpTool run_code", async () => {
        const result = await session.callMcpTool("run_code", {
            code: 'print("mcp-code-test")',
            language: "python",
        });
        expect(result.success).toBe(true);
        expect(result.data).toBeDefined();
    });

    test("getMetrics returns data", async () => {
        const result = await session.getMetrics();
        expect(result.success).toBe(true);
        expect(result.metrics).toBeDefined();
    });

    test("session info returns data", async () => {
        const result = await session.info();
        expect(result.success).toBe(true);
        expect(result.data).toBeDefined();
        const data = result.data as Record<string, unknown>;
        expect(data.sessionId).toBeTruthy();
    });

    test("session getLink", async () => {
        const result = await session.getLink("https", 8080);
        expect(result.requestId).toBeDefined();
    });
});
