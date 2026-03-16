/**
 * Integration tests for BrowserAgent (act/observe/extract with real API calls).
 * Reference: python/tests/integration/test_agb_browser.py (test_browser_agent)
 * Reference: TypeScript browser-operator tests
 */
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";

jest.setTimeout(300_000);

function sleep(ms: number) {
    return new Promise((r) => setTimeout(r, ms));
}

async function initBrowserWithRetry(
    session: Session,
    maxRetries = 3,
): Promise<boolean> {
    for (let i = 0; i <= maxRetries; i++) {
        const ok = await session.browser.initialize({});
        if (ok) return true;
        await sleep(5000);
    }
    return false;
}

describe("BrowserAgent (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb, "agb-browser-use-1");
        const ok = await initBrowserWithRetry(session);
        expect(ok).toBe(true);
    });

    afterAll(async () => {
        try { await session.browser.destroy(); } catch { /* ignore */ }
        await deleteTestSession(agb, session);
    });

    test("agent is available on browser", () => {
        expect(session.browser.agent).toBeDefined();
    });

    test("navigate to a page", async () => {
        const result = await session.browser.agent.navigate("https://www.example.com");
        expect(result).toBeDefined();
    });

    test("screenshot returns base64 data", async () => {
        await sleep(2000);
        const data = await session.browser.agent.screenshot();
        expect(data).toBeDefined();
        expect(typeof data).toBe("string");
        if (data) {
            expect(data.length).toBeGreaterThan(100);
        }
    });

    test("act performs an action", async () => {
        await session.browser.agent.navigate("https://www.example.com");
        await sleep(2000);

        const result = await session.browser.agent.act({
            action: "Click on the 'More information...' link",
            timeout: 60,
        });

        expect(result).toBeDefined();
        expect(result.success).toBeDefined();
    });

    test("observe returns actionable elements", async () => {
        await session.browser.agent.navigate("https://www.example.com");
        await sleep(2000);

        const result = await session.browser.agent.observe({
            instruction: "Find all clickable links on the page",
        });

        expect(result).toBeDefined();
        expect(Array.isArray(result.results)).toBe(true);
    });

    test("extract returns structured data", async () => {
        await session.browser.agent.navigate("https://www.example.com");
        await sleep(2000);

        const result = await session.browser.agent.extract({
            instruction: "Extract the page title and the first heading text",
            schema: {
                type: "object",
                properties: {
                    title: { type: "string" },
                    heading: { type: "string" },
                },
            },
        });

        expect(result).toBeDefined();
        expect(result.data).toBeDefined();
    });

    test("close agent resources", async () => {
        const result = await session.browser.agent.close();
        expect(result).toBe(true);
    });
});
