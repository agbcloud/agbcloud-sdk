/**
 * Integration tests for screen.betaTakeScreenshot() functionality.
 * This test requires a Browser Use session (with linkUrl support).
 */

import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import { ScreenError } from "../../src/exceptions";

jest.setTimeout(300_000);

describe("screen.betaTakeScreenshot Integration Tests", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        const apiKey = process.env.AGB_API_KEY;
        if (!apiKey) {
            throw new Error("AGB_API_KEY environment variable not set");
        }

        agb = createAGB();
        // Use browser-use session for linkUrl support
        session = await createTestSession(agb, "agb-browser-use-1");

        // Initialize browser for screenshot capability
        let initOk = false;
        for (let i = 0; i < 3; i++) {
            initOk = await session.browser.initialize({});
            if (initOk) break;
            await new Promise((r) => setTimeout(r, 5000));
        }
        expect(initOk).toBe(true);
    });

    afterAll(async () => {
        try {
            await session.browser.destroy();
        } catch {
            /* ignore */
        }
        await deleteTestSession(agb, session);
    });

    test("betaTakeScreenshot with default format (PNG)", async () => {
        // Check if linkUrl is available
        if (!session.linkUrl) {
            console.log("linkUrl not provided, skipping test");
            return;
        }

        const result = await session.computer.screen.betaTakeScreenshot();

        expect(result.success).toBe(true);
        expect(result.type).toBe("screenshot");
        expect(result.mimeType).toBe("image/png");
        expect(result.data).toBeInstanceOf(Buffer);
        expect(result.data!.length).toBeGreaterThan(100);
        // Verify PNG magic bytes
        expect(result.data!.subarray(0, 8).equals(
            Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])
        )).toBe(true);

        // Verify dimensions are returned
        expect(typeof result.width).toBe("number");
        expect(typeof result.height).toBe("number");
        expect(result.width!).toBeGreaterThan(0);
        expect(result.height!).toBeGreaterThan(0);
    });

    test("betaTakeScreenshot with PNG format", async () => {
        if (!session.linkUrl) {
            console.log("linkUrl not provided, skipping test");
            return;
        }

        const result = await session.computer.screen.betaTakeScreenshot("png");

        expect(result.success).toBe(true);
        expect(result.mimeType).toBe("image/png");
        expect(result.data).toBeInstanceOf(Buffer);
        expect(result.data!.subarray(0, 4).equals(
            Buffer.from([0x89, 0x50, 0x4e, 0x47])
        )).toBe(true);
    });

    test("betaTakeScreenshot with JPEG format", async () => {
        if (!session.linkUrl) {
            console.log("linkUrl not provided, skipping test");
            return;
        }

        const result = await session.computer.screen.betaTakeScreenshot("jpeg");

        expect(result.success).toBe(true);
        expect(result.mimeType).toBe("image/jpeg");
        expect(result.data).toBeInstanceOf(Buffer);
        // Verify JPEG magic bytes
        expect(result.data!.subarray(0, 3).equals(
            Buffer.from([0xff, 0xd8, 0xff])
        )).toBe(true);
    });

    test("betaTakeScreenshot with jpg format alias", async () => {
        if (!session.linkUrl) {
            console.log("linkUrl not provided, skipping test");
            return;
        }

        const result = await session.computer.screen.betaTakeScreenshot("jpg");

        expect(result.success).toBe(true);
        expect(result.mimeType).toBe("image/jpeg");
        expect(result.data).toBeInstanceOf(Buffer);
        expect(result.data!.subarray(0, 3).equals(
            Buffer.from([0xff, 0xd8, 0xff])
        )).toBe(true);
    });

    test("betaTakeScreenshot invalid format throws Error", async () => {
        if (!session.linkUrl) {
            console.log("linkUrl not provided, skipping test");
            return;
        }

        await expect(
            session.computer.screen.betaTakeScreenshot("gif")
        ).rejects.toThrow("Invalid format");
    });

    test("consecutive betaTakeScreenshot calls succeed", async () => {
        if (!session.linkUrl) {
            console.log("linkUrl not provided, skipping test");
            return;
        }

        const start = Date.now();

        const result1 = await session.computer.screen.betaTakeScreenshot("png");
        const result2 = await session.computer.screen.betaTakeScreenshot("jpeg");

        const elapsed = Date.now() - start;

        expect(result1.success).toBe(true);
        expect(result2.success).toBe(true);
        expect(result1.data!.length).toBeGreaterThan(0);
        expect(result2.data!.length).toBeGreaterThan(0);
        expect(elapsed).toBeLessThan(60_000);
    });
});

describe("screen.betaTakeScreenshot without linkUrl", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        const apiKey = process.env.AGB_API_KEY;
        if (!apiKey) {
            throw new Error("AGB_API_KEY environment variable not set");
        }

        agb = createAGB();
        // Use regular session without linkUrl (computer-use)
        session = await createTestSession(agb, "agb-computer-use-1");
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    test("betaTakeScreenshot throws ScreenError in Computer Use environment", async () => {
        // Computer Use session should not have linkUrl
        if (session.linkUrl) {
            console.log("linkUrl unexpectedly available, skipping test");
            return;
        }

        await expect(
            session.computer.screen.betaTakeScreenshot()
        ).rejects.toThrow(ScreenError);

        await expect(
            session.computer.screen.betaTakeScreenshot()
        ).rejects.toThrow("does not support");
    });
});
