import { Extension, ExtensionOption, ExtensionsService } from "../../src/extension";

describe("Extension", () => {
    test("constructor sets fields", () => {
        const ext = new Extension("ext-1", "my-extension", "2024-01-01");
        expect(ext.id).toBe("ext-1");
        expect(ext.name).toBe("my-extension");
        expect(ext.createdAt).toBe("2024-01-01");
    });

    test("constructor without createdAt", () => {
        const ext = new Extension("ext-2", "another");
        expect(ext.createdAt).toBeUndefined();
    });
});

describe("ExtensionOption", () => {
    test("valid construction", () => {
        const opt = new ExtensionOption("ctx-1", ["ext-1", "ext-2"]);
        expect(opt.contextId).toBe("ctx-1");
        expect(opt.extensionIds).toEqual(["ext-1", "ext-2"]);
    });

    test("empty contextId throws", () => {
        expect(() => new ExtensionOption("", ["ext-1"])).toThrow("contextId cannot be empty");
    });

    test("whitespace contextId throws", () => {
        expect(() => new ExtensionOption("  ", ["ext-1"])).toThrow("contextId cannot be empty");
    });

    test("empty extensionIds throws", () => {
        expect(() => new ExtensionOption("ctx-1", [])).toThrow("extensionIds cannot be empty");
    });

    test("validate returns true for valid", () => {
        const opt = new ExtensionOption("ctx-1", ["ext-1"]);
        expect(opt.validate()).toBe(true);
    });

    test("validate returns false for empty id in array", () => {
        const opt = new ExtensionOption("ctx-1", ["ext-1"]);
        opt.extensionIds = ["ext-1", ""];
        expect(opt.validate()).toBe(false);
    });

    test("validate returns false for whitespace-only id", () => {
        const opt = new ExtensionOption("ctx-1", ["ext-1"]);
        opt.extensionIds = ["  "];
        expect(opt.validate()).toBe(false);
    });

    test("toString returns formatted string", () => {
        const opt = new ExtensionOption("ctx-1", ["ext-1", "ext-2"]);
        expect(opt.toString()).toBe(
            `ExtensionOption(contextId='ctx-1', extensionIds=["ext-1","ext-2"])`,
        );
    });

    test("toDisplayString returns human-readable string", () => {
        const opt = new ExtensionOption("ctx-1", ["ext-1", "ext-2"]);
        expect(opt.toDisplayString()).toBe(
            "Extension Config: 2 extension(s) in context 'ctx-1'",
        );
    });
});

describe("ExtensionsService", () => {
    const mockContextService = {
        get: jest.fn(),
        delete: jest.fn(),
        getFileUploadUrl: jest.fn(),
        listFiles: jest.fn(),
        deleteFile: jest.fn(),
    };

    const mockAgb = {
        apiKey: "test-key",
        context: mockContextService as any,
    };

    /** Helper: create a service with lazy init resolved */
    async function createService(contextId = "ctx-123", contextName?: string): Promise<ExtensionsService> {
        mockContextService.get.mockResolvedValue({
            success: true,
            context: { id: contextId, name: contextName ?? "test" },
        });
        const svc = new ExtensionsService(mockAgb, contextName);
        // Trigger lazy initialization by calling list (a lightweight public method)
        // We need listFiles mock for list() to not throw
        mockContextService.listFiles.mockResolvedValue({ success: true, files: [] });
        await svc.list();
        return svc;
    }

    beforeEach(() => {
        jest.clearAllMocks();
    });

    // ─── constructor + lazy initialization ──────────────────

    test("constructor with default name triggers get", async () => {
        mockContextService.get.mockResolvedValue({
            success: true,
            context: { id: "ctx-auto", name: "extensions-auto" },
        });
        const svc = new ExtensionsService(mockAgb);
        mockContextService.listFiles.mockResolvedValue({ success: true, files: [] });
        await svc.list();
        expect(svc.contextId).toBe("ctx-auto");
        expect(mockContextService.get).toHaveBeenCalledWith(
            expect.stringMatching(/^extensions-\d+$/),
            true,
        );
    });

    test("constructor with custom name", async () => {
        mockContextService.get.mockResolvedValue({
            success: true,
            context: { id: "ctx-456", name: "my-exts" },
        });
        const svc = new ExtensionsService(mockAgb, "my-exts");
        mockContextService.listFiles.mockResolvedValue({ success: true, files: [] });
        await svc.list();
        expect(svc.contextId).toBe("ctx-456");
        expect(mockContextService.get).toHaveBeenCalledWith("my-exts", true);
    });

    test("initialization failure throws on first use", async () => {
        mockContextService.get.mockResolvedValue({
            success: false,
            context: null,
        });
        const svc = new ExtensionsService(mockAgb, "bad-ctx");
        await expect(svc.list()).rejects.toThrow(
            "Failed to create extension repository context",
        );
    });

    test("constructor throws if agb is null", () => {
        expect(() => new ExtensionsService(null as any)).toThrow(
            "AGB instance is required",
        );
    });

    test("constructor throws if agb.context is missing", () => {
        expect(() => new ExtensionsService({ apiKey: "k" } as any)).toThrow(
            "AGB instance must have a context service",
        );
    });

    // ─── list ───────────────────────────────────────────────

    test("list returns extensions", async () => {
        const svc = await createService("ctx-list");

        mockContextService.listFiles.mockResolvedValue({
            success: true,
            files: [
                { name: "ext_abc.zip", path: "/tmp/extensions/ext_abc.zip", type: "file", createdTime: "2024-01-01" },
                { name: "ext_def.zip", path: "/tmp/extensions/ext_def.zip", type: "file" },
            ],
        });
        const exts = await svc.list();
        expect(exts).toHaveLength(2);
        expect(exts[0].id).toBe("ext_abc.zip");
        expect(exts[0].createdAt).toBe("2024-01-01");
        expect(exts[1].createdAt).toBeUndefined();
    });

    test("list failure throws", async () => {
        const svc = await createService("ctx-lf");
        mockContextService.listFiles.mockResolvedValue({ success: false, files: [] });
        await expect(svc.list()).rejects.toThrow("Failed to list extensions");
    });

    // ─── createExtensionOption ──────────────────────────────

    test("createExtensionOption", async () => {
        const svc = await createService("ctx-opt");
        const opt = svc.createExtensionOption(["ext-1", "ext-2"]);
        expect(opt).toBeInstanceOf(ExtensionOption);
        expect(opt.contextId).toBe("ctx-opt");
        expect(opt.extensionIds).toEqual(["ext-1", "ext-2"]);
    });

    // ─── cleanup ────────────────────────────────────────────

    test("cleanup success", async () => {
        const svc = await createService("ctx-clean");
        mockContextService.delete.mockResolvedValue({ success: true });
        const result = await svc.cleanup();
        expect(result).toBe(true);
    });

    test("cleanup failure returns false", async () => {
        const svc = await createService("ctx-cleanf");
        mockContextService.delete.mockResolvedValue({ success: false });
        const result = await svc.cleanup();
        expect(result).toBe(false);
    });

    test("cleanup exception returns false", async () => {
        const svc = await createService("ctx-cleane");
        mockContextService.delete.mockRejectedValue(new Error("Delete error"));
        const result = await svc.cleanup();
        expect(result).toBe(false);
    });

    // ─── delete ─────────────────────────────────────────────

    test("delete success returns true", async () => {
        const svc = await createService("ctx-rm");
        mockContextService.deleteFile.mockResolvedValue({ success: true });
        const result = await svc.delete("ext-1");
        expect(result).toBe(true);
        expect(mockContextService.deleteFile).toHaveBeenCalledWith(
            "ctx-rm",
            "/tmp/extensions/ext-1",
        );
    });

    test("delete failure returns false", async () => {
        const svc = await createService("ctx-rmf");
        mockContextService.deleteFile.mockResolvedValue({
            success: false,
            errorMessage: "Not found",
        });
        const result = await svc.delete("ext-1");
        expect(result).toBe(false);
    });

    test("delete exception returns false", async () => {
        const svc = await createService("ctx-rme");
        mockContextService.deleteFile.mockRejectedValue(new Error("Network error"));
        const result = await svc.delete("ext-1");
        expect(result).toBe(false);
    });
});
