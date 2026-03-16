/**
 * Integration tests for browser.screenshot(page, fullPage, options).
 * Reference: source project Browser.screenshot() which accepts a Playwright page.
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

describeOrSkip("Browser screenshot (integration)", () => {
    let agb: AGB;
    let session: Session;
    let cdpBrowser: any;
    let page: any;

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

        const endpointUrl = await session.browser.getEndpointUrl();
        cdpBrowser = await chromium.connectOverCDP(endpointUrl);
        const context = cdpBrowser.contexts[0] ?? await cdpBrowser.newContext();
        page = await context.newPage();
        await page.goto("https://www.example.com", { timeout: 30000 });
        await sleep(2000);
    });

    afterAll(async () => {
        try { await page?.close(); } catch { /* ignore */ }
        try { await cdpBrowser?.close(); } catch { /* ignore */ }
        try { await session.browser.destroy(); } catch { /* ignore */ }
        await deleteTestSession(agb, session);
    });

    test("screenshot with default options", async () => {
        const result = await session.browser.screenshot(page);
        expect(result).toBeInstanceOf(Uint8Array);
        expect(result.length).toBeGreaterThan(100);
    });

    test("screenshot fullPage=true", async () => {
        const result = await session.browser.screenshot(page, true);
        expect(result).toBeInstanceOf(Uint8Array);
        expect(result.length).toBeGreaterThan(100);
    });

    test("screenshot with custom options", async () => {
        const result = await session.browser.screenshot(page, false, {
            type: "png",
            timeout: 30000,
        });
        expect(result).toBeInstanceOf(Uint8Array);
        expect(result.length).toBeGreaterThan(100);
    });

    test("consecutive screenshots succeed", async () => {
        const start = Date.now();
        const r1 = await session.browser.screenshot(page);
        const r2 = await session.browser.screenshot(page);
        const elapsed = Date.now() - start;

        expect(r1).toBeInstanceOf(Uint8Array);
        expect(r2).toBeInstanceOf(Uint8Array);
        expect(r1.length).toBeGreaterThan(0);
        expect(r2.length).toBeGreaterThan(0);
        expect(elapsed).toBeLessThan(60_000);
    });
});
