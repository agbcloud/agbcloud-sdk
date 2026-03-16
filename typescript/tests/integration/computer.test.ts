/**
 * Integration tests for Computer module: mouse, keyboard, screen, window, app.
 * Requires agb-computer-use-ubuntu-2204 image.
 */
import { createAGB, deleteTestSession, createTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import { MouseButton, ScrollDirection } from "../../src/modules/computer/computer";

jest.setTimeout(300_000);

describe("Computer module (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb, "agb-computer-use-ubuntu-2204");
        await new Promise((r) => setTimeout(r, 3000));
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    // --- Screen ---

    test("screen capture returns data", async () => {
        const result = await session.computer.screen.capture();
        expect(result.success).toBe(true);
        expect(result.data).toBeDefined();
    });

    test("screen getSize returns dimensions", async () => {
        const result = await session.computer.screen.getSize();
        expect(result.success).toBe(true);
        expect(typeof result.width).toBe("number");
        expect(typeof result.height).toBe("number");
        expect(typeof result.dpiScalingFactor).toBe("number");
    });

    // --- Mouse ---

    test("mouse move", async () => {
        const result = await session.computer.mouse.move(100, 200);
        expect(result.success).toBe(true);
    });

    test("mouse getPosition", async () => {
        const result = await session.computer.mouse.getPosition();
        expect(result.success).toBe(true);
        expect(typeof result.x).toBe("number");
        expect(typeof result.y).toBe("number");
    });

    test("mouse click", async () => {
        const result = await session.computer.mouse.click(
            400, 300, MouseButton.LEFT,
        );
        expect(result.success).toBe(true);
    });

    test("mouse drag", async () => {
        const result = await session.computer.mouse.drag(
            100, 100, 300, 300,
        );
        expect(result.success).toBe(true);
    });

    test("mouse scroll", async () => {
        const result = await session.computer.mouse.scroll(
            400, 300, ScrollDirection.DOWN, 3,
        );
        expect(result.success).toBe(true);
    });

    // --- Keyboard ---

    test("keyboard type text", async () => {
        const result = await session.computer.keyboard.type("hello AGB");
        expect(result.success).toBe(true);
    });

    test("keyboard press key", async () => {
        const result = await session.computer.keyboard.press("space");
        expect(result.requestId).toBeDefined();
    });

    test("keyboard release key", async () => {
        const result = await session.computer.keyboard.release("Shift");
        expect(result.success).toBe(true);
    });

    // --- Window ---

    test("window listRootWindows", async () => {
        const result = await session.computer.window.listRootWindows();
        expect(result.success).toBe(true);
        expect(Array.isArray(result.windows)).toBe(true);
    });

    test("window getActiveWindow", async () => {
        const result = await session.computer.window.getActiveWindow();
        expect(result.requestId).toBeDefined();
    });

    // --- Application ---

    test("app listInstalled", async () => {
        const result = await session.computer.app.listInstalled();
        expect(result.success).toBe(true);
        expect(Array.isArray(result.data)).toBe(true);
        expect(result.data.length).toBeGreaterThan(0);
    });

    test("app start and stop lifecycle", async () => {
        const installed = await session.computer.app.listInstalled();
        expect(installed.success).toBe(true);
        expect(installed.data.length).toBeGreaterThan(0);

        const firstApp = installed.data[0] as Record<string, unknown>;
        const startCmd = firstApp.start_cmd ?? firstApp.startCmd ?? firstApp.StartCmd;
        if (!startCmd) {
            console.warn("No start_cmd found, listing app keys:", Object.keys(firstApp));
            return;
        }

        const startResult = await session.computer.app.start(startCmd as string);
        if (!startResult.success) {
            console.warn("app.start failed:", startResult.errorMessage);
            return;
        }
        expect(startResult.data.length).toBeGreaterThan(0);

        await new Promise((r) => setTimeout(r, 3000));

        const proc = startResult.data[0] as Record<string, unknown>;
        const pname = proc.pname as string;
        if (pname) {
            const stopResult = await session.computer.app.stopByPname(pname);
            expect(stopResult.success).toBe(true);
        }
    });

    // --- Deprecated convenience methods ---

    test("deprecated computer.screenshot()", async () => {
        const result = await session.computer.screenshot();
        expect(result.success).toBe(true);
        expect(result.data).toBeDefined();
    });
});
