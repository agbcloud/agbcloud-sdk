/**
 * Unit tests for screen.betaTakeScreenshot functionality.
 */

import type { SessionLike } from "../../src/api/base-service";
import { ScreenController } from "../../src/modules/computer/computer";
import { ScreenError } from "../../src/exceptions";

// Helper to create valid PNG response
function createValidPngResponse(): string {
    // PNG magic bytes + padding
    const pngMagic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
    const pngData = Buffer.concat([pngMagic, Buffer.alloc(100)]);
    const b64Data = pngData.toString("base64");
    return JSON.stringify({
        type: "screenshot",
        mime_type: "image/png",
        data: b64Data,
        width: 1920,
        height: 1080,
    });
}

// Helper to create valid JPEG response
function createValidJpegResponse(): string {
    // JPEG magic bytes + padding
    const jpegMagic = Buffer.from([0xff, 0xd8, 0xff]);
    const jpegData = Buffer.concat([jpegMagic, Buffer.alloc(100)]);
    const b64Data = jpegData.toString("base64");
    return JSON.stringify({
        type: "screenshot",
        mime_type: "image/jpeg",
        data: b64Data,
        width: 1920,
        height: 1080,
    });
}

// Helper to create mock session
function createMockSession(hasLinkUrl: boolean = true): SessionLike {
    return {
        getApiKey: () => "test-key",
        getSessionId: () => "test-session",
        getClient: () => ({}),
        linkUrl: hasLinkUrl ? "https://example.com/link" : "",
    };
}

describe("ScreenController.betaTakeScreenshot - Basic", () => {
    let screen: ScreenController;
    let spy: jest.SpyInstance;

    beforeEach(() => {
        screen = new ScreenController(createMockSession(true));
        spy = jest.spyOn(screen as any, "callMcpTool");
    });
    afterEach(() => spy.mockRestore());

    test("PNG screenshot success", async () => {
        spy.mockResolvedValue({
            requestId: "req-123",
            success: true,
            data: createValidPngResponse(),
        });

        const result = await screen.betaTakeScreenshot("png");

        expect(result.success).toBe(true);
        expect(result.requestId).toBe("req-123");
        expect(result.mimeType).toBe("image/png");
        expect(result.type).toBe("screenshot");
        expect(result.width).toBe(1920);
        expect(result.height).toBe(1080);
        expect(result.data).toBeInstanceOf(Buffer);
        expect(result.data?.subarray(0, 8).equals(
            Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])
        )).toBe(true);

        expect(spy).toHaveBeenCalledWith("screenshot", { format: "png" });
    });

    test("JPEG screenshot success", async () => {
        spy.mockResolvedValue({
            requestId: "req-456",
            success: true,
            data: createValidJpegResponse(),
        });

        const result = await screen.betaTakeScreenshot("jpeg");

        expect(result.success).toBe(true);
        expect(result.mimeType).toBe("image/jpeg");
        expect(result.data?.subarray(0, 3).equals(
            Buffer.from([0xff, 0xd8, 0xff])
        )).toBe(true);

        expect(spy).toHaveBeenCalledWith("screenshot", { format: "jpeg" });
    });

    test("jpg alias is converted to jpeg", async () => {
        spy.mockResolvedValue({
            requestId: "req-789",
            success: true,
            data: createValidJpegResponse(),
        });

        const result = await screen.betaTakeScreenshot("jpg");

        expect(result.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("screenshot", { format: "jpeg" });
    });

    test("default format is png", async () => {
        spy.mockResolvedValue({
            requestId: "req-default",
            success: true,
            data: createValidPngResponse(),
        });

        const result = await screen.betaTakeScreenshot();

        expect(result.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("screenshot", { format: "png" });
    });
});

describe("ScreenController.betaTakeScreenshot - Environment Check", () => {
    test("throws ScreenError without linkUrl", async () => {
        const screen = new ScreenController(createMockSession(false));

        await expect(screen.betaTakeScreenshot()).rejects.toThrow(ScreenError);
        await expect(screen.betaTakeScreenshot()).rejects.toThrow("does not support");
        await expect(screen.betaTakeScreenshot()).rejects.toThrow("capture()");
    });

    test("throws ScreenError when linkUrl is empty string", async () => {
        const mockSession: SessionLike = {
            getApiKey: () => "test-key",
            getSessionId: () => "test-session",
            getClient: () => ({}),
            linkUrl: "",
        };
        const screen = new ScreenController(mockSession);

        await expect(screen.betaTakeScreenshot()).rejects.toThrow(ScreenError);
    });
});

describe("ScreenController.betaTakeScreenshot - Format Validation", () => {
    let screen: ScreenController;
    let spy: jest.SpyInstance;

    beforeEach(() => {
        screen = new ScreenController(createMockSession(true));
        spy = jest.spyOn(screen as any, "callMcpTool");
    });
    afterEach(() => spy.mockRestore());

    test("invalid format gif throws Error", async () => {
        await expect(screen.betaTakeScreenshot("gif")).rejects.toThrow("Invalid format");
    });

    test("invalid format bmp throws Error", async () => {
        await expect(screen.betaTakeScreenshot("bmp")).rejects.toThrow("Invalid format");
    });

    test("format is case insensitive", async () => {
        spy.mockResolvedValue({
            requestId: "req-case",
            success: true,
            data: createValidPngResponse(),
        });

        const result = await screen.betaTakeScreenshot("PNG");

        expect(result.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("screenshot", { format: "png" });
    });
});

describe("ScreenController.betaTakeScreenshot - Error Handling", () => {
    let screen: ScreenController;
    let spy: jest.SpyInstance;

    beforeEach(() => {
        screen = new ScreenController(createMockSession(true));
        spy = jest.spyOn(screen as any, "callMcpTool");
    });
    afterEach(() => spy.mockRestore());

    test("MCP tool failure throws ScreenError", async () => {
        spy.mockResolvedValue({
            requestId: "req-fail",
            success: false,
            errorMessage: "Tool execution failed",
        });

        await expect(screen.betaTakeScreenshot()).rejects.toThrow(ScreenError);
        await expect(screen.betaTakeScreenshot()).rejects.toThrow("Tool execution failed");
    });

    test("empty response data throws ScreenError", async () => {
        spy.mockResolvedValue({
            requestId: "req-empty",
            success: true,
            data: "",
        });

        await expect(screen.betaTakeScreenshot()).rejects.toThrow(ScreenError);
        await expect(screen.betaTakeScreenshot()).rejects.toThrow("empty data");
    });

    test("non-JSON response throws ScreenError", async () => {
        spy.mockResolvedValue({
            requestId: "req-nonjson",
            success: true,
            data: "not json data",
        });

        await expect(screen.betaTakeScreenshot()).rejects.toThrow(ScreenError);
        await expect(screen.betaTakeScreenshot()).rejects.toThrow("non-JSON");
    });

    test("invalid JSON response throws ScreenError", async () => {
        spy.mockResolvedValue({
            requestId: "req-invalid",
            success: true,
            data: "{invalid json}",
        });

        await expect(screen.betaTakeScreenshot()).rejects.toThrow(ScreenError);
        await expect(screen.betaTakeScreenshot()).rejects.toThrow("Invalid screenshot JSON");
    });

    test("missing base64 field throws ScreenError", async () => {
        spy.mockResolvedValue({
            requestId: "req-nodata",
            success: true,
            data: JSON.stringify({
                type: "screenshot",
                mime_type: "image/png",
                width: 100,
                height: 100,
            }),
        });

        await expect(screen.betaTakeScreenshot()).rejects.toThrow(ScreenError);
        await expect(screen.betaTakeScreenshot()).rejects.toThrow("missing base64");
    });

    test("missing type field throws ScreenError", async () => {
        const pngData = Buffer.concat([
            Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
            Buffer.alloc(100),
        ]);
        spy.mockResolvedValue({
            requestId: "req-notype",
            success: true,
            data: JSON.stringify({
                mime_type: "image/png",
                data: pngData.toString("base64"),
            }),
        });

        await expect(screen.betaTakeScreenshot()).rejects.toThrow(ScreenError);
        await expect(screen.betaTakeScreenshot()).rejects.toThrow("non-empty string 'type'");
    });

    test("missing mime_type field throws ScreenError", async () => {
        const pngData = Buffer.concat([
            Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
            Buffer.alloc(100),
        ]);
        spy.mockResolvedValue({
            requestId: "req-nomime",
            success: true,
            data: JSON.stringify({
                type: "screenshot",
                data: pngData.toString("base64"),
            }),
        });

        await expect(screen.betaTakeScreenshot()).rejects.toThrow(ScreenError);
        await expect(screen.betaTakeScreenshot()).rejects.toThrow("non-empty string 'mime_type'");
    });

    test("wrong magic bytes throws ScreenError", async () => {
        // Send JPEG data but claim it's PNG
        const jpegData = Buffer.concat([
            Buffer.from([0xff, 0xd8, 0xff]),
            Buffer.alloc(100),
        ]);
        spy.mockResolvedValue({
            requestId: "req-wrongmagic",
            success: true,
            data: JSON.stringify({
                type: "screenshot",
                mime_type: "image/png",
                data: jpegData.toString("base64"),
            }),
        });

        await expect(screen.betaTakeScreenshot("png")).rejects.toThrow(ScreenError);
        await expect(screen.betaTakeScreenshot("png")).rejects.toThrow("does not match expected format");
    });

    test("wrong mime type throws ScreenError", async () => {
        const pngData = Buffer.concat([
            Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
            Buffer.alloc(100),
        ]);
        spy.mockResolvedValue({
            requestId: "req-wrongmime",
            success: true,
            data: JSON.stringify({
                type: "screenshot",
                mime_type: "image/jpeg", // Wrong for PNG
                data: pngData.toString("base64"),
            }),
        });

        await expect(screen.betaTakeScreenshot("png")).rejects.toThrow(ScreenError);
        await expect(screen.betaTakeScreenshot("png")).rejects.toThrow("mime_type does not match");
    });
});

describe("ScreenController.betaTakeScreenshot - Optional Fields", () => {
    let screen: ScreenController;
    let spy: jest.SpyInstance;

    beforeEach(() => {
        screen = new ScreenController(createMockSession(true));
        spy = jest.spyOn(screen as any, "callMcpTool");
    });
    afterEach(() => spy.mockRestore());

    test("width and height are optional", async () => {
        const pngData = Buffer.concat([
            Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
            Buffer.alloc(100),
        ]);
        spy.mockResolvedValue({
            requestId: "req-nosize",
            success: true,
            data: JSON.stringify({
                type: "screenshot",
                mime_type: "image/png",
                data: pngData.toString("base64"),
                // No width/height
            }),
        });

        const result = await screen.betaTakeScreenshot();

        expect(result.success).toBe(true);
        expect(result.width).toBeUndefined();
        expect(result.height).toBeUndefined();
    });

    test("invalid width type throws ScreenError", async () => {
        const pngData = Buffer.concat([
            Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
            Buffer.alloc(100),
        ]);
        spy.mockResolvedValue({
            requestId: "req-badwidth",
            success: true,
            data: JSON.stringify({
                type: "screenshot",
                mime_type: "image/png",
                data: pngData.toString("base64"),
                width: "not an int",
            }),
        });

        await expect(screen.betaTakeScreenshot()).rejects.toThrow(ScreenError);
        await expect(screen.betaTakeScreenshot()).rejects.toThrow("expected integer 'width'");
    });

    test("invalid height type throws ScreenError", async () => {
        const pngData = Buffer.concat([
            Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
            Buffer.alloc(100),
        ]);
        spy.mockResolvedValue({
            requestId: "req-badheight",
            success: true,
            data: JSON.stringify({
                type: "screenshot",
                mime_type: "image/png",
                data: pngData.toString("base64"),
                width: 100,
                height: "not an int",
            }),
        });

        await expect(screen.betaTakeScreenshot()).rejects.toThrow(ScreenError);
        await expect(screen.betaTakeScreenshot()).rejects.toThrow("expected integer 'height'");
    });
});
