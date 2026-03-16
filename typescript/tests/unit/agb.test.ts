import { AGB } from "../../src/agb";
import { Session } from "../../src/session";

const mockCreateMcpSession = jest.fn();
const mockListSessions = jest.fn();
const mockGetMcpSession = jest.fn();

jest.mock("../../src/api/client", () => ({
    Client: jest.fn().mockImplementation(() => ({
        createMcpSession: mockCreateMcpSession,
        listSessions: mockListSessions,
        getMcpSession: mockGetMcpSession,
    })),
}));

describe("AGB", () => {
    const originalEnv = process.env;

    beforeEach(() => {
        process.env = { ...originalEnv };
        delete process.env.AGB_API_KEY;
        jest.clearAllMocks();
    });

    afterAll(() => {
        process.env = originalEnv;
    });

    describe("constructor", () => {
        test("throws without API key", () => {
            expect(() => new AGB()).toThrow("API key is required");
        });

        test("accepts string API key", () => {
            const agb = new AGB("test-api-key-12345");
            expect(agb.apiKey).toBe("test-api-key-12345");
        });

        test("reads API key from env", () => {
            process.env.AGB_API_KEY = "env-api-key-12345";
            const agb = new AGB();
            expect(agb.apiKey).toBe("env-api-key-12345");
        });

        test("with options", () => {
            const agb = new AGB({
                apiKey: "test-api-key-12345",
                config: { endpoint: "custom.endpoint.com", timeoutMs: 30000 },
            });
            expect(agb.apiKey).toBe("test-api-key-12345");
            expect(agb.config.endpoint).toBe("custom.endpoint.com");
            expect(agb.config.timeoutMs).toBe(30000);
        });
    });

    test("toJSON returns config snapshot", () => {
        const agb = new AGB("key");
        const json = agb.toJSON();
        expect(json).toHaveProperty("endpoint");
        expect(json).toHaveProperty("timeoutMs");
    });

    test("context service is initialized", () => {
        const agb = new AGB("test-api-key-12345");
        expect(agb.context).toBeDefined();
    });

    describe("create", () => {
        test("returns error without params", async () => {
            const agb = new AGB("test-api-key-12345");
            const result = await agb.create(null);
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("params is required");
        });

        test("returns error when imageId empty", async () => {
            const agb = new AGB("key");
            const result = await agb.create({ imageId: "", contextSync: [] });
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("imageId is required");
        });

        test("returns error when imageId only whitespace", async () => {
            const agb = new AGB("key");
            const result = await agb.create({ imageId: "   ", contextSync: [] });
            expect(result.success).toBe(false);
        });

        test("success returns session when createMcpSession succeeds", async () => {
            const agb = new AGB("key");
            mockCreateMcpSession.mockResolvedValue({
                requestId: "req-1",
                getData: () => ({
                    success: true,
                    sessionId: "sid-1",
                    resourceUrl: "https://resource.example",
                    appInstanceId: "app-1",
                    resourceId: "res-1",
                }),
                getSessionId: () => "sid-1",
                getResourceUrl: () => "https://resource.example",
                getErrorMessage: () => "",
            });

            const result = await agb.create({ imageId: "img-1", contextSync: [] });

            expect(result.success).toBe(true);
            expect(result.session).toBeInstanceOf(Session);
            expect(result.session?.getSessionId()).toBe("sid-1");
            expect(result.requestId).toBe("req-1");
        });

        test("returns error when getData().success is false", async () => {
            const agb = new AGB("key");
            mockCreateMcpSession.mockResolvedValue({
                requestId: "req-1",
                getData: () => ({ success: false, errMsg: "quota exceeded" }),
                getSessionId: () => undefined,
                getResourceUrl: () => "",
                getErrorMessage: () => "quota exceeded",
            });

            const result = await agb.create({ imageId: "img-1", contextSync: [] });

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("quota exceeded");
        });

        test("returns error when sessionId missing in response", async () => {
            const agb = new AGB("key");
            mockCreateMcpSession.mockResolvedValue({
                requestId: "req-1",
                getData: () => ({ success: true }),
                getSessionId: () => undefined,
                getResourceUrl: () => "",
                getErrorMessage: () => "no session id",
            });

            const result = await agb.create({ imageId: "img-1", contextSync: [] });

            expect(result.success).toBe(false);
        });

        test("catches and returns error when createMcpSession throws", async () => {
            const agb = new AGB("key");
            mockCreateMcpSession.mockRejectedValue(new Error("network error"));

            const result = await agb.create({ imageId: "img-1", contextSync: [] });

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("network error");
        });
    });

    describe("list", () => {
        test("returns error when page < 1", async () => {
            const agb = new AGB("key");
            const result = await agb.list({}, 0, 10);
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("Page number must be >= 1");
        });

        test("success returns sessionIds when listSessions succeeds", async () => {
            const agb = new AGB("key");
            mockListSessions.mockResolvedValue({
                requestId: "req-1",
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getSessionData: () => [{ sessionId: "sid-1" }, { sessionId: "sid-2" }],
                getNextToken: () => "",
                getMaxResults: () => 10,
                getCount: () => 2,
            });

            const result = await agb.list({}, 1, 10);

            expect(result.success).toBe(true);
            expect(result.sessionIds).toEqual(["sid-1", "sid-2"]);
        });

        test("returns error when listSessions not successful", async () => {
            const agb = new AGB("key");
            mockListSessions.mockResolvedValue({
                requestId: "req-1",
                isSuccessful: () => false,
                getErrorMessage: () => "api error",
            });

            const result = await agb.list({});

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("api error");
        });
    });

    describe("getSession", () => {
        test("success returns data when getMcpSession succeeds", async () => {
            const agb = new AGB("key");
            mockGetMcpSession.mockResolvedValue({
                requestId: "req-1",
                statusCode: 200,
                code: "",
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getData: () => ({
                    sessionId: "sid-1",
                    resourceUrl: "https://r",
                    appInstanceId: "a1",
                    resourceId: "r1",
                    status: "Running",
                }),
            });

            const result = await agb.getSession("sid-1");

            expect(result.success).toBe(true);
            expect(result.data?.sessionId).toBe("sid-1");
        });

        test("returns error when getMcpSession not successful", async () => {
            const agb = new AGB("key");
            mockGetMcpSession.mockResolvedValue({
                requestId: "req-1",
                statusCode: 404,
                code: "NotFound",
                isSuccessful: () => false,
                getErrorMessage: () => "session not found",
            });

            const result = await agb.getSession("sid-missing");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("session not found");
        });
    });

    describe("get", () => {
        test("returns error when sessionId empty", async () => {
            const agb = new AGB("key");
            const result = await agb.get("");
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("sessionId is required");
        });

        test("success returns session when getSession succeeds", async () => {
            const agb = new AGB("key");
            mockGetMcpSession.mockResolvedValue({
                requestId: "req-1",
                statusCode: 200,
                code: "",
                isSuccessful: () => true,
                getErrorMessage: () => "",
                getData: () => ({
                    sessionId: "sid-1",
                    resourceUrl: "https://r",
                    appInstanceId: "a1",
                    resourceId: "r1",
                    status: "Running",
                }),
            });

            const result = await agb.get("sid-1");

            expect(result.success).toBe(true);
            expect(result.session).toBeInstanceOf(Session);
            expect(result.session?.getSessionId()).toBe("sid-1");
        });
    });

    describe("delete", () => {
        test("returns result from session.delete", async () => {
            const agb = new AGB("key");
            const session = new Session(agb, "sid-1");
            const mockDelete = jest.fn().mockResolvedValue({ success: true, requestId: "req-1" });
            (session as any).delete = mockDelete;

            const result = await agb.delete(session);

            expect(result.success).toBe(true);
            expect(mockDelete).toHaveBeenCalledWith(false);
        });

        test("returns error when session.delete throws", async () => {
            const agb = new AGB("key");
            const session = new Session(agb, "sid-1");
            (session as any).delete = jest.fn().mockRejectedValue(new Error("delete failed"));

            const result = await agb.delete(session);

            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("delete failed");
        });
    });
});
