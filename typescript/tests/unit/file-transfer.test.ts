import * as fs from "fs";
import { FileTransfer } from "../../src/modules/file-transfer";

jest.mock("fs");
const mockedFs = fs as jest.Mocked<typeof fs>;

const mockGetAndLoadInternalContext = jest.fn();
const mockGetFileUploadUrl = jest.fn();
const mockGetFileDownloadUrl = jest.fn();
const mockSync = jest.fn();
const mockInfo = jest.fn();

function createMockAgb() {
    return {
        apiKey: "test-key",
        client: { getAndLoadInternalContext: mockGetAndLoadInternalContext },
        context: {
            getFileUploadUrl: mockGetFileUploadUrl,
            getFileDownloadUrl: mockGetFileDownloadUrl,
        },
    };
}

function createMockSession() {
    return {
        getApiKey: () => "test-key",
        getSessionId: () => "session-1",
        context: {
            sync: mockSync,
            info: mockInfo,
        },
    };
}

describe("FileTransfer", () => {
    const originalFetch = globalThis.fetch;

    beforeEach(() => {
        jest.clearAllMocks();
        mockedFs.existsSync.mockReturnValue(false);
        mockedFs.statSync.mockReturnValue({ isFile: () => false } as fs.Stats);
        mockGetAndLoadInternalContext.mockResolvedValue(undefined);
        mockGetFileUploadUrl.mockResolvedValue({ success: false, url: "", errorMessage: "not mocked" });
        mockGetFileDownloadUrl.mockResolvedValue({ success: false, url: "", errorMessage: "not mocked" });
        mockSync.mockResolvedValue({ success: true, requestId: "sync-1" });
        mockInfo.mockResolvedValue({ success: true, items: [] });
    });

    afterAll(() => {
        globalThis.fetch = originalFetch;
    });

    describe("constructor", () => {
        test("stores agb and session", () => {
            const agb = createMockAgb();
            const session = createMockSession();
            const ft = new FileTransfer(agb as any, session as any, 12000);
            expect((ft as { contextId?: string }).contextId).toBeUndefined();
        });
    });

    describe("ensureContextId", () => {
        test("returns success when contextId already set", async () => {
            const agb = createMockAgb();
            const session = createMockSession();
            const ft = new FileTransfer(agb as any, session as any);
            (ft as { contextId?: string }).contextId = "ctx-1";
            (ft as { contextPath?: string }).contextPath = "/path";

            const result = await ft.ensureContextId();

            expect(result.success).toBe(true);
            expect(mockGetAndLoadInternalContext).not.toHaveBeenCalled();
        });

        test("calls getAndLoadInternalContext and sets contextId on success", async () => {
            const agb = createMockAgb();
            const session = createMockSession();
            const mockResponse = {
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getContextList: () => [{ contextId: "ctx-1", contextPath: "/data" }],
            };
            mockGetAndLoadInternalContext.mockResolvedValue(mockResponse);

            const ft = new FileTransfer(agb as any, session as any);
            const result = await ft.ensureContextId();

            expect(result.success).toBe(true);
            expect(mockGetAndLoadInternalContext).toHaveBeenCalled();
            expect((ft as { contextId?: string }).contextId).toBe("ctx-1");
            expect((ft as { contextPath?: string }).contextPath).toBe("/data");
        });

        test("returns error when getAndLoadInternalContext not successful", async () => {
            const agb = createMockAgb();
            const session = createMockSession();
            const mockResponse = {
                isSuccessful: () => false,
                getErrorMessage: () => "api error",
                getContextList: () => [],
            };
            mockGetAndLoadInternalContext.mockResolvedValue(mockResponse);

            const ft = new FileTransfer(agb as any, session as any);
            const result = await ft.ensureContextId();

            expect(result.success).toBe(false);
            expect(result.error).toBe("api error");
        });

        test("returns error when response has no context data", async () => {
            const agb = createMockAgb();
            const session = createMockSession();
            const mockResponse = {
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getContextList: () => [],
            };
            mockGetAndLoadInternalContext.mockResolvedValue(mockResponse);

            const ft = new FileTransfer(agb as any, session as any);
            const result = await ft.ensureContextId();

            expect(result.success).toBe(false);
            expect(result.error).toContain("no data");
        });

        test("returns error when getAndLoadInternalContext throws", async () => {
            const agb = createMockAgb();
            const session = createMockSession();
            mockGetAndLoadInternalContext.mockRejectedValue(new Error("network error"));

            const ft = new FileTransfer(agb as any, session as any);
            const result = await ft.ensureContextId();

            expect(result.success).toBe(false);
            expect(result.error).toContain("network error");
        });
    });

    describe("upload", () => {
        test("returns error when local file does not exist", async () => {
            mockedFs.existsSync.mockReturnValue(false);
            const agb = createMockAgb();
            const session = createMockSession();
            const ft = new FileTransfer(agb as any, session as any);
            (ft as { contextId?: string }).contextId = "ctx-1";

            const result = await ft.upload("/nonexistent.txt", "/remote/file.txt");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("not found");
            expect(result.bytesSent).toBe(0);
        });

        test("returns error when local path is a directory", async () => {
            mockedFs.existsSync.mockReturnValue(true);
            mockedFs.statSync.mockReturnValue({ isFile: () => false } as fs.Stats);
            const agb = createMockAgb();
            const session = createMockSession();
            const ft = new FileTransfer(agb as any, session as any);
            (ft as { contextId?: string }).contextId = "ctx-1";

            const result = await ft.upload("/some/dir", "/remote/");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("not found");
        });

        test("returns error when getFileUploadUrl fails", async () => {
            mockedFs.existsSync.mockReturnValue(true);
            mockedFs.statSync.mockReturnValue({ isFile: () => true } as fs.Stats);
            mockGetFileUploadUrl.mockResolvedValue({
                success: false,
                url: "",
                errorMessage: "quota exceeded",
            });
            const agb = createMockAgb();
            const session = createMockSession();
            const ft = new FileTransfer(agb as any, session as any);
            (ft as { contextId?: string }).contextId = "ctx-1";

            const result = await ft.upload("/local/file.txt", "/remote/file.txt");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("quota exceeded");
        });

        test("returns error when ensureContextId returns no data", async () => {
            mockedFs.existsSync.mockReturnValue(true);
            mockedFs.statSync.mockReturnValue({ isFile: () => true } as fs.Stats);
            const mockResponse = {
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getContextList: () => [],
            };
            mockGetAndLoadInternalContext.mockResolvedValue(mockResponse);
            const agb = createMockAgb();
            const session = createMockSession();
            const ft = new FileTransfer(agb as any, session as any);

            const result = await ft.upload("/local/file.txt", "/remote/file.txt");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("no data");
        });
    });

    describe("download", () => {
        test("returns error when ensureContextId returns no data", async () => {
            const mockResponse = {
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getContextList: () => [],
            };
            mockGetAndLoadInternalContext.mockResolvedValue(mockResponse);
            const agb = createMockAgb();
            const session = createMockSession();
            const ft = new FileTransfer(agb as any, session as any);

            const result = await ft.download("/remote/file.txt", "/local/file.txt");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("no data");
        });

        test("returns error when getFileDownloadUrl fails", async () => {
            mockGetFileDownloadUrl.mockResolvedValue({
                success: false,
                url: "",
                errorMessage: "file not found",
            });
            const agb = createMockAgb();
            const session = createMockSession();
            const ft = new FileTransfer(agb as any, session as any);
            (ft as { contextId?: string }).contextId = "ctx-1";
            mockSync.mockResolvedValue({ success: true, requestId: "sync-1" });

            const result = await ft.download("/remote/file.txt", "/local/out.txt", {
                wait: false,
            });

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("file not found");
        });

        test("returns error when overwrite is false and local file exists", async () => {
            mockedFs.existsSync.mockReturnValue(true);
            mockGetFileDownloadUrl.mockResolvedValue({
                success: true,
                url: "https://download.example/file",
                requestId: "req-1",
            });
            const agb = createMockAgb();
            const session = createMockSession();
            const ft = new FileTransfer(agb as any, session as any);
            (ft as { contextId?: string }).contextId = "ctx-1";
            mockSync.mockResolvedValue({ success: true, requestId: "sync-1" });

            const result = await ft.download("/remote/file.txt", "/local/exists.txt", {
                overwrite: false,
                wait: false,
            });

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("overwrite=false");
        });
    });
});
