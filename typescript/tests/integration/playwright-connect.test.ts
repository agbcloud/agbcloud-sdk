/**
 * Integration tests for Playwright CDP connection to browser sessions.
 * Reference: python/tests/integration/test_browser_playwright_connect.py
 *
 * Requires playwright as a dev dependency.
 */
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";

jest.setTimeout(300_000);

function sleep(ms: number) {
    return new Promise((r) => setTimeout(r, ms));
}

let playwrightAvailable = false;
let chromium: any;

try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const pw = require("playwright");
    chromium = pw.chromium;
    playwrightAvailable = true;
} catch {
    playwrightAvailable = false;
}

const describeOrSkip = playwrightAvailable ? describe : describe.skip;

describeOrSkip("Playwright CDP connect (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb, "agb-browser-use-1");

        let initOk = false;
        for (let i = 0; i < 3; i++) {
            initOk = await session.browser.initialize({});
            if (initOk) break;
            await sleep(5000);
        }
        expect(initOk).toBe(true);
    });

    afterAll(async () => {
        try { await session.browser.destroy(); } catch { /* ignore */ }
        await deleteTestSession(agb, session);
    });

    test("connect via CDP and navigate", async () => {
        const endpointUrl = await session.browser.getEndpointUrl();
        expect(endpointUrl).toBeDefined();
        expect(typeof endpointUrl).toBe("string");

        const browser = await chromium.connectOverCDP(endpointUrl);
        const context = browser.contexts[0] ?? await browser.newContext();
        const page = await context.newPage();

        try {
            await page.goto("https://www.example.com", { timeout: 30000 });
            const title = await page.title();
            expect(title).toBeDefined();
            expect(title.length).toBeGreaterThan(0);
        } finally {
            await page.close();
            await browser.close();
        }
    });

    test("evaluate JavaScript in CDP page", async () => {
        const endpointUrl = await session.browser.getEndpointUrl();
        const browser = await chromium.connectOverCDP(endpointUrl);
        const context = browser.contexts[0] ?? await browser.newContext();
        const page = await context.newPage();

        try {
            await page.goto("about:blank");
            const result = await page.evaluate(() => 1 + 1);
            expect(result).toBe(2);
        } finally {
            await page.close();
            await browser.close();
        }
    });

    test("take screenshot via CDP page", async () => {
        const endpointUrl = await session.browser.getEndpointUrl();
        const browser = await chromium.connectOverCDP(endpointUrl);
        const context = browser.contexts[0] ?? await browser.newContext();
        const page = await context.newPage();

        try {
            await page.goto("https://www.example.com", { timeout: 30000 });
            await sleep(2000);

            const screenshotBuffer = await page.screenshot();
            expect(screenshotBuffer).toBeInstanceOf(Buffer);
            expect(screenshotBuffer.length).toBeGreaterThan(1000);
        } finally {
            await page.close();
            await browser.close();
        }
    });
});
