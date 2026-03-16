import { Context, ContextService } from "../../src/context";

const mockListContexts = jest.fn();
const mockGetContext = jest.fn();
const mockModifyContext = jest.fn();
const mockDeleteContext = jest.fn();
const mockGetContextFileUploadUrl = jest.fn();
const mockGetContextFileDownloadUrl = jest.fn();
const mockDeleteContextFile = jest.fn();

function createMockAgb() {
    return {
        apiKey: "test-key",
        client: {
            listContexts: mockListContexts,
            getContext: mockGetContext,
            modifyContext: mockModifyContext,
            deleteContext: mockDeleteContext,
            getContextFileUploadUrl: mockGetContextFileUploadUrl,
            getContextFileDownloadUrl: mockGetContextFileDownloadUrl,
            deleteContextFile: mockDeleteContextFile,
        },
    };
}

describe("Context", () => {
    test("constructor sets id and name", () => {
        const ctx = new Context("ctx-1", "my-context", "2024-01-01", "2024-01-02");
        expect(ctx.id).toBe("ctx-1");
        expect(ctx.name).toBe("my-context");
        expect(ctx.createdAt).toBe("2024-01-01");
        expect(ctx.lastUsedAt).toBe("2024-01-02");
    });
});

describe("ContextService", () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    test("toJSON returns type", () => {
        const agb = createMockAgb();
        const svc = new ContextService(agb as any);
        expect(svc.toJSON()).toEqual({ type: "ContextService" });
    });

    describe("list", () => {
        test("success returns contexts", async () => {
            const agb = createMockAgb();
            mockListContexts.mockResolvedValue({
                getRequestId: () => "req-1",
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getContextsData: () => [
                    { id: "c1", name: "ctx1", createTime: "2024-01-01", lastUsedTime: "2024-01-02" },
                ],
                getNextToken: () => undefined,
                getMaxResults: () => 10,
            });

            const svc = new ContextService(agb as any);
            const result = await svc.list({ maxResults: 10 });

            expect(result.success).toBe(true);
            expect(result.contexts).toHaveLength(1);
            expect(result.contexts![0].id).toBe("c1");
            expect(result.contexts![0].name).toBe("ctx1");
        });

        test("returns error when listContexts not successful", async () => {
            const agb = createMockAgb();
            mockListContexts.mockResolvedValue({
                getRequestId: () => "req-1",
                isSuccessful: () => false,
                getErrorMessage: () => "api error",
            });

            const svc = new ContextService(agb as any);
            const result = await svc.list();

            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("api error");
        });

        test("returns error when listContexts throws", async () => {
            const agb = createMockAgb();
            mockListContexts.mockRejectedValue(new Error("network error"));

            const svc = new ContextService(agb as any);
            const result = await svc.list();

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("network error");
        });
    });

    describe("get", () => {
        test("returns error when both contextId and name empty", async () => {
            const agb = createMockAgb();
            const svc = new ContextService(agb as any);
            const result = await svc.get(undefined, false);
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("context_id or name");
        });

        test("returns error when create=true and contextId provided", async () => {
            const agb = createMockAgb();
            const svc = new ContextService(agb as any);
            const result = await svc.get("name", true, undefined, "ctx-1");
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("create=True");
        });

        test("success returns context when getContext succeeds", async () => {
            const agb = createMockAgb();
            mockGetContext.mockResolvedValue({
                getRequestId: () => "req-1",
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getContextData: () => ({ id: "c1", name: "my-ctx", createTime: "2024-01-01", lastUsedTime: "2024-01-02" }),
            });

            const svc = new ContextService(agb as any);
            const result = await svc.get("my-ctx");

            expect(result.success).toBe(true);
            expect(result.context?.id).toBe("c1");
            expect(result.context?.name).toBe("my-ctx");
        });

        test("returns error when getContext returns no data", async () => {
            const agb = createMockAgb();
            mockGetContext.mockResolvedValue({
                getRequestId: () => "req-1",
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getContextData: () => undefined,
            });

            const svc = new ContextService(agb as any);
            const result = await svc.get("my-ctx");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("No context data");
        });
    });

    describe("create", () => {
        test("returns error when name empty", async () => {
            const agb = createMockAgb();
            const svc = new ContextService(agb as any);
            const result = await svc.create("");
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("name cannot be empty");
        });

        test("calls get with create=true when name provided", async () => {
            const agb = createMockAgb();
            mockGetContext.mockResolvedValue({
                getRequestId: () => "req-1",
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getContextData: () => ({ id: "new-id", name: "new-ctx" }),
            });

            const svc = new ContextService(agb as any);
            const result = await svc.create("new-ctx");

            expect(result.success).toBe(true);
            expect(mockGetContext).toHaveBeenCalled();
        });
    });

    describe("update", () => {
        test("returns error when context is null/undefined", async () => {
            const agb = createMockAgb();
            const svc = new ContextService(agb as any);
            const result = await svc.update(null as any);
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("cannot be None");
        });

        test("returns error when context.id empty", async () => {
            const agb = createMockAgb();
            const svc = new ContextService(agb as any);
            const result = await svc.update(new Context("", "name"));
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("context.id");
        });

        test("returns error when context.name empty", async () => {
            const agb = createMockAgb();
            const svc = new ContextService(agb as any);
            const result = await svc.update(new Context("id", ""));
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("context.name");
        });

        test("success when modifyContext succeeds", async () => {
            const agb = createMockAgb();
            mockModifyContext.mockResolvedValue({
                getRequestId: () => "req-1",
                isSuccessful: () => true,
                getErrorMessage: () => "",
            });

            const svc = new ContextService(agb as any);
            const result = await svc.update(new Context("ctx-1", "new-name"));

            expect(result.success).toBe(true);
            expect(result.data).toEqual({ context_id: "ctx-1" });
        });
    });

    describe("delete", () => {
        test("returns error when context is null", async () => {
            const agb = createMockAgb();
            const svc = new ContextService(agb as any);
            const result = await svc.delete(null as any);
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("cannot be None");
        });

        test("returns error when context.id empty", async () => {
            const agb = createMockAgb();
            const svc = new ContextService(agb as any);
            const result = await svc.delete(new Context("", "name"));
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("context.id");
        });

        test("success when deleteContext succeeds", async () => {
            const agb = createMockAgb();
            mockDeleteContext.mockResolvedValue({
                getRequestId: () => "req-1",
                isSuccessful: () => true,
                getErrorMessage: () => "",
            });

            const svc = new ContextService(agb as any);
            const result = await svc.delete(new Context("ctx-1", "name"));

            expect(result.success).toBe(true);
        });
    });

    describe("getFileUploadUrl", () => {
        test("returns error when contextId empty", async () => {
            const agb = createMockAgb();
            const svc = new ContextService(agb as any);
            const result = await svc.getFileUploadUrl("", "/path");
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("context_id");
        });

        test("returns error when filePath empty", async () => {
            const agb = createMockAgb();
            const svc = new ContextService(agb as any);
            const result = await svc.getFileUploadUrl("ctx-1", "");
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("file_path");
        });

        test("success returns url when API succeeds", async () => {
            const agb = createMockAgb();
            mockGetContextFileUploadUrl.mockResolvedValue({
                getRequestId: () => "req-1",
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getUploadUrl: () => "https://upload.example/url",
            });
            const svc = new ContextService(agb as any);
            const result = await svc.getFileUploadUrl("ctx-1", "/remote/file.txt");
            expect(result.success).toBe(true);
            expect(result.url).toBe("https://upload.example/url");
        });
    });

    describe("getFileDownloadUrl", () => {
        test("returns error when contextId empty", async () => {
            const agb = createMockAgb();
            const svc = new ContextService(agb as any);
            const result = await svc.getFileDownloadUrl("", "/path");
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("context_id");
        });

        test("success returns url when API succeeds", async () => {
            const agb = createMockAgb();
            mockGetContextFileDownloadUrl.mockResolvedValue({
                getRequestId: () => "req-1",
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getDownloadUrl: () => "https://download.example/url",
            });
            const svc = new ContextService(agb as any);
            const result = await svc.getFileDownloadUrl("ctx-1", "/remote/file.txt");
            expect(result.success).toBe(true);
            expect(result.url).toBe("https://download.example/url");
        });
    });

    describe("deleteFile", () => {
        test("returns error when contextId empty", async () => {
            const agb = createMockAgb();
            const svc = new ContextService(agb as any);
            const result = await svc.deleteFile("", "/path");
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("context_id");
        });

        test("success when deleteContextFile succeeds", async () => {
            const agb = createMockAgb();
            mockDeleteContextFile.mockResolvedValue({
                getRequestId: () => "req-1",
                isSuccessful: () => true,
                getErrorMessage: () => "",
            });
            const svc = new ContextService(agb as any);
            const result = await svc.deleteFile("ctx-1", "/remote/file.txt");
            expect(result.success).toBe(true);
        });
    });
});
