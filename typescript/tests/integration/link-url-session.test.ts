import { logDebug } from "../../src/logger";
import { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import { createAGB, createTestSession } from "./setup";

describe("LinkUrl Session Integration Tests", () => {
    let agb: AGB;
    let session: Session;
    let testDir: string;

    beforeAll( async () => {
        const apiKey = process.env.AGB_API_KEY;
        if (!apiKey) {
            throw new Error("AGB_API_KEY environment variable not set");
        }

        agb = createAGB();
        session = await createTestSession(agb,"agb-browser-use-1");
    });

    test("should use LinkUrl route for MCP tools and call_mcp_tool", async () => {

        try {
            // Check if LinkUrl/token are available
            if (!session.linkUrl || !session.token) {
                console.log("LinkUrl/token not provided, skipping test");
                return;
            }

            // Test command execution through LinkUrl route
            const cmdResult = await session.command.execute(
                "echo link-url-route-ok"
            );
            expect(cmdResult.success).toBe(true);
            expect(cmdResult.output).toContain("link-url-route-ok");

            // Test session restoration with get()
            const restoredResult = await agb.get(session.getSessionId());
            expect(restoredResult.success).toBe(true);
            expect(restoredResult.session).toBeDefined();

            const restoredSession = restoredResult.session!;
            expect(restoredSession.token).not.toBe("");
            expect(restoredSession.linkUrl).not.toBe("");

            // Test direct call_mcp_tool on restored session
            const restoredDirect = await restoredSession.callMcpTool("shell", {
                command: "echo restored-direct-link-url-route-ok",
            });
            expect(restoredDirect.success).toBe(true);
            expect(restoredDirect.data).toContain(
                "restored-direct-link-url-route-ok"
            );

            // Test direct call_mcp_tool on original session
            const direct = await session.callMcpTool("shell", {
                command: "echo direct-link-url-route-ok",
            });
            logDebug("direct", direct.data);
            expect(direct.success).toBe(true);
            expect(direct.data).toContain("direct-link-url-route-ok");
        } finally {
            const deleteResult = await session.delete();
            expect(deleteResult.success).toBe(true);
        }
    });
});
