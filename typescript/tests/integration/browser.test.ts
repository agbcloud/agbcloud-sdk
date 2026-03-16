/**
 * Integration tests for Browser module: initialize, screenshot, endpoint URL, destroy.
 * Requires agb-browser-use-1 image.
 */
import { createAGB, deleteTestSession, createTestSession, getApiKey } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import { GetCdpLinkRequest } from "../../src/api/models/GetCdpLinkRequest";

jest.setTimeout(300_000);

async function initBrowserWithRetry(
    session: Session,
    options?: Record<string, unknown>,
    maxRetries = 2,
): Promise<boolean> {
    for (let i = 0; i <= maxRetries; i++) {
        const ok = await session.browser.initialize(options ?? {});
        if (ok) return true;
        await new Promise((r) => setTimeout(r, 5000));
    }
    return false;
}

describe("Browser module (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb, "agb-browser-use-1");
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    test("initialize browser", async () => {
        const ok = await initBrowserWithRetry(session);
        expect(ok).toBe(true);
        expect(session.browser.isInitialized()).toBe(true);
    });

    test("initialize browser again is idempotent", async () => {
        const ok = await session.browser.initialize({});
        expect(ok).toBe(true);
    });

    test("getEndpointUrl returns URL via getCdpLink", async () => {
        const url = await session.browser.getEndpointUrl();
        expect(url).toBeDefined();
        expect(typeof url).toBe("string");
        expect(url.length).toBeGreaterThan(0);
    });

    test("getCdpLink API returns WebSocket URL directly", async () => {
        const client = session.getClient();
        const request = new GetCdpLinkRequest(
            `Bearer ${getApiKey()}`,
            session.getSessionId(),
        );
        const response = await client.getCdpLink(request);
        expect(response.statusCode).not.toBe(404);
        expect(response.isSuccessful()).toBe(true);
        const url = response.getUrl();
        expect(url).toBeDefined();
        expect(typeof url).toBe("string");
        expect(url!.length).toBeGreaterThan(0);
    });

    test("destroy browser", async () => {
        const result = await session.browser.destroy();
        expect(result.success).toBe(true);
    });

    test("destroy without init throws BrowserError", async () => {
        await expect(session.browser.destroy()).rejects.toThrow(
            "Browser is not initialized",
        );
    });

    test("re-initialize with options", async () => {
        const ok = await initBrowserWithRetry(session, {
            headless: true,
            fingerprint: {
                userAgent: "Mozilla/5.0 IntegrationTest",
                locale: "en-US",
            },
        });
        expect(ok).toBe(true);
    });

    test("final destroy", async () => {
        const result = await session.browser.destroy();
        expect(result.success).toBe(true);
    });
});
