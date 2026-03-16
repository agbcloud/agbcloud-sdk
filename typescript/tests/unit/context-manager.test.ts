import { ContextManager } from "../../src/context-manager";

const mockGetContextInfo = jest.fn();
const mockSyncContext = jest.fn();

function createMockSession() {
    return {
        getApiKey: () => "test-key",
        getSessionId: () => "session-1",
        getClient: () => ({
            getContextInfo: mockGetContextInfo,
            syncContext: mockSyncContext,
        }),
    };
}

describe("ContextManager", () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    test("constructor stores session", () => {
        const session = createMockSession();
        const mgr = new ContextManager(session as any);
        expect((mgr as any).session).toBe(session);
    });

    test("toJSON returns sessionId", () => {
        const session = createMockSession();
        const mgr = new ContextManager(session as any);
        expect(mgr.toJSON()).toEqual({ sessionId: "session-1" });
    });

    describe("info", () => {
        test("success returns items when getContextStatus has valid data", async () => {
            const session = createMockSession();
            mockGetContextInfo.mockResolvedValue({
                getRequestId: () => "req-1",
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getContextStatus: () =>
                    JSON.stringify([
                        {
                            type: "data",
                            data: JSON.stringify([
                                {
                                    contextId: "c1",
                                    path: "/p",
                                    status: "Success",
                                    errorMessage: "",
                                    startTime: 0,
                                    finishTime: 0,
                                    taskType: "upload",
                                },
                            ]),
                        },
                    ]),
            });

            const mgr = new ContextManager(session as any);
            const result = await mgr.info();

            expect(result.success).toBe(true);
            expect(result.requestId).toBe("req-1");
            expect(result.items).toHaveLength(1);
            expect(result.items![0].contextId).toBe("c1");
            expect(result.items![0].status).toBe("Success");
        });

        test("returns error when getContextInfo not successful", async () => {
            const session = createMockSession();
            mockGetContextInfo.mockResolvedValue({
                getRequestId: () => "req-1",
                isSuccessful: () => false,
                getErrorMessage: () => "api error",
            });

            const mgr = new ContextManager(session as any);
            const result = await mgr.info();

            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("api error");
            expect(result.items).toEqual([]);
        });

        test("rejects when getContextInfo throws", async () => {
            const session = createMockSession();
            mockGetContextInfo.mockRejectedValue(new Error("network error"));

            const mgr = new ContextManager(session as any);
            await expect(mgr.info()).rejects.toThrow("network error");
        });

        test("success with empty getContextStatus returns empty items", async () => {
            const session = createMockSession();
            mockGetContextInfo.mockResolvedValue({
                getRequestId: () => "req-1",
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getContextStatus: () => null,
            });

            const mgr = new ContextManager(session as any);
            const result = await mgr.info();

            expect(result.success).toBe(true);
            expect(result.items).toEqual([]);
        });
    });

    describe("sync", () => {
        test("returns error when contextId provided but path omitted", async () => {
            const session = createMockSession();
            const mgr = new ContextManager(session as any);
            const result = await mgr.sync("ctx-1", undefined, "upload");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("context_id and path must be provided together");
            expect(mockSyncContext).not.toHaveBeenCalled();
        });

        test("returns error when path provided but contextId omitted", async () => {
            const session = createMockSession();
            const mgr = new ContextManager(session as any);
            const result = await mgr.sync(undefined, "/path", "upload");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("context_id and path must be provided together");
        });

        test("success when syncContext succeeds and no callback", async () => {
            const session = createMockSession();
            mockGetContextInfo.mockResolvedValue({
                getRequestId: () => "req-1",
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getContextStatus: () => null,
            });
            mockSyncContext.mockResolvedValue({
                getRequestId: () => "req-sync",
                isSuccessful: () => true,
                getErrorMessage: () => "",
            });

            const mgr = new ContextManager(session as any);
            const result = await mgr.sync("ctx-1", "/path", "upload", 2, 10);

            expect(result.success).toBe(true);
            expect(result.requestId).toBe("req-sync");
            expect(mockSyncContext).toHaveBeenCalled();
        });

        test("returns error when syncContext not successful", async () => {
            const session = createMockSession();
            mockSyncContext.mockResolvedValue({
                getRequestId: () => "req-1",
                isSuccessful: () => false,
                getErrorMessage: () => "sync failed",
            });

            const mgr = new ContextManager(session as any);
            const result = await mgr.sync(undefined, undefined, "upload");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("sync failed");
        });
    });
});
