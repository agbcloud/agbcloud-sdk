import type { HttpResponse } from "../../src/api/http-client";
import { Client } from "../../src/api/client";
import {
    CreateSessionRequest,
    ReleaseSessionRequest,
    GetSessionRequest,
    ListSessionRequest,
    SetLabelRequest,
    GetLabelRequest,
    GetCdpLinkRequest,
    CallMcpToolRequest,
    ListMcpToolsRequest,
    GetMcpResourceRequest,
    InitBrowserRequest,
    GetSessionDetailRequest,
    DeleteSessionAsyncRequest,
} from "../../src/api/models";

const mockMakeRequest = jest.fn();
const mockClose = jest.fn();

jest.mock("../../src/api/http-client", () => ({
    HTTPClient: jest.fn().mockImplementation(() => ({
        makeRequest: mockMakeRequest,
        close: mockClose,
    })),
}));

function makeHttpResponse(overrides: Partial<HttpResponse> = {}): HttpResponse {
    return {
        statusCode: 200,
        url: "https://api.test/",
        headers: {},
        success: true,
        json: { success: true, requestId: "req-1", data: {} },
        requestId: "req-1",
        ...overrides,
    };
}

describe("Client", () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe("createMcpSession", () => {
        test("calls POST /mcp/createSession and returns CreateSessionResponse", async () => {
            const client = new Client();
            mockMakeRequest.mockResolvedValue(
                makeHttpResponse({
                    json: {
                        success: true,
                        requestId: "r1",
                        data: { sessionId: "sid-1" },
                    },
                    requestId: "r1",
                }),
            );

            const req = new CreateSessionRequest("api-key-123", undefined, "img-1");
            const res = await client.createMcpSession(req);

            expect(mockMakeRequest).toHaveBeenCalledWith({
                method: "POST",
                endpoint: "/mcp/createSession",
                params: expect.any(Object),
                jsonData: expect.any(Object),
            });
            expect(mockClose).toHaveBeenCalled();
            expect(res.isSuccessful()).toBe(true);
            expect(res.requestId).toBe("r1");
        });

        test("throws when authorization missing", async () => {
            const client = new Client();
            const req = new CreateSessionRequest("", undefined, "img-1");

            await expect(client.createMcpSession(req)).rejects.toThrow(
                "authorization is required",
            );
            expect(mockMakeRequest).not.toHaveBeenCalled();
        });
    });

    describe("releaseMcpSession", () => {
        test("calls POST /mcp/releaseSession and returns ReleaseSessionResponse", async () => {
            const client = new Client();
            mockMakeRequest.mockResolvedValue(makeHttpResponse());

            const req = new ReleaseSessionRequest("sid-1", "key");
            const res = await client.releaseMcpSession(req);

            expect(mockMakeRequest).toHaveBeenCalledWith({
                method: "POST",
                endpoint: "/mcp/releaseSession",
                params: expect.any(Object),
                jsonData: { sessionId: "sid-1" },
            });
            expect(res).toBeDefined();
            expect(res.statusCode).toBe(200);
        });

        test("throws when sessionId missing", async () => {
            const client = new Client();
            const req = new ReleaseSessionRequest("", "key");

            await expect(client.releaseMcpSession(req)).rejects.toThrow(
                "session_id is required",
            );
        });

        test("throws when authorization missing", async () => {
            const client = new Client();
            const req = new ReleaseSessionRequest("sid", "");

            await expect(client.releaseMcpSession(req)).rejects.toThrow(
                "authorization is required",
            );
        });
    });

    describe("getMcpSession", () => {
        test("calls POST /mcp/getSession", async () => {
            const client = new Client();
            mockMakeRequest.mockResolvedValue(
                makeHttpResponse({
                    json: {
                        success: true,
                        requestId: "r1",
                        data: { sessionId: "sid-1" },
                    },
                }),
            );

            const req = new GetSessionRequest("key", "sid-1");
            const res = await client.getMcpSession(req);

            expect(mockMakeRequest).toHaveBeenCalledWith({
                method: "POST",
                endpoint: "/mcp/getSession",
                params: expect.any(Object),
                jsonData: expect.any(Object),
            });
            expect(res).toBeDefined();
        });
    });

    describe("listSessions", () => {
        test("calls GET /sdk/ListSession", async () => {
            const client = new Client();
            mockMakeRequest.mockResolvedValue(
                makeHttpResponse({
                    json: {
                        success: true,
                        requestId: "r1",
                        data: { sessions: [], nextToken: undefined },
                    },
                }),
            );

            const req = new ListSessionRequest("key");
            const res = await client.listSessions(req);

            expect(mockMakeRequest).toHaveBeenCalledWith({
                method: "GET",
                endpoint: "/sdk/ListSession",
                params: expect.any(Object),
            });
            expect(res).toBeDefined();
        });

        test("throws when authorization missing", async () => {
            const client = new Client();
            const req = new ListSessionRequest("");

            await expect(client.listSessions(req)).rejects.toThrow(
                "authorization is required",
            );
        });
    });

    describe("getSessionDetail", () => {
        test("calls POST /mcp/getSessionInfo", async () => {
            const client = new Client();
            mockMakeRequest.mockResolvedValue(
                makeHttpResponse({
                    json: {
                        success: true,
                        requestId: "r1",
                        data: { sessionId: "sid-1", status: "Running" },
                    },
                }),
            );

            const req = new GetSessionDetailRequest("key", "sid-1");
            const res = await client.getSessionDetail(req);

            expect(mockMakeRequest).toHaveBeenCalledWith({
                method: "POST",
                endpoint: "/mcp/getSessionInfo",
                params: expect.any(Object),
                jsonData: expect.any(Object),
            });
            expect(res).toBeDefined();
        });
    });

    describe("setLabel", () => {
        test("calls POST /sdk/SetLabel", async () => {
            const client = new Client();
            mockMakeRequest.mockResolvedValue(makeHttpResponse());

            const req = new SetLabelRequest("key", "sid-1", "env=test");
            const res = await client.setLabel(req);

            expect(mockMakeRequest).toHaveBeenCalledWith({
                method: "POST",
                endpoint: "/sdk/SetLabel",
                params: expect.any(Object),
            });
            expect(res).toBeDefined();
        });
    });

    describe("getLabel", () => {
        test("calls GET /sdk/GetLabel", async () => {
            const client = new Client();
            mockMakeRequest.mockResolvedValue(
                makeHttpResponse({
                    json: { success: true, requestId: "r1", data: { labels: {} } },
                }),
            );

            const req = new GetLabelRequest("key", "sid-1");
            const res = await client.getLabel(req);

            expect(mockMakeRequest).toHaveBeenCalledWith({
                method: "GET",
                endpoint: "/sdk/GetLabel",
                params: expect.any(Object),
            });
            expect(res).toBeDefined();
        });
    });

    describe("getCdpLink", () => {
        test("calls POST /internet/getCdpLink", async () => {
            const client = new Client();
            mockMakeRequest.mockResolvedValue(
                makeHttpResponse({
                    json: {
                        success: true,
                        requestId: "r1",
                        data: { url: "http://cdp-link.example" },
                    },
                }),
            );

            const req = new GetCdpLinkRequest("key", "sid-1");
            const res = await client.getCdpLink(req);

            expect(mockMakeRequest).toHaveBeenCalledWith({
                method: "POST",
                endpoint: "/internet/getCdpLink",
                params: expect.any(Object),
                jsonData: expect.any(Object),
            });
            expect(res).toBeDefined();
        });

        test("throws when sessionId missing", async () => {
            const client = new Client();
            const req = new GetCdpLinkRequest("key", "");

            await expect(client.getCdpLink(req)).rejects.toThrow(
                "session_id is required",
            );
        });
    });

    describe("callMcpTool", () => {
        test("calls POST /mcp with readTimeout", async () => {
            const client = new Client();
            mockMakeRequest.mockResolvedValue(
                makeHttpResponse({
                    json: {
                        success: true,
                        requestId: "r1",
                        data: { content: [] },
                    },
                }),
            );

            const req = new CallMcpToolRequest(
                {},
                "key",
                undefined,
                "toolName",
                undefined,
                "sid-1",
            );
            const res = await client.callMcpTool(req, 120000);

            expect(mockMakeRequest).toHaveBeenCalledWith(
                expect.objectContaining({
                    method: "POST",
                    endpoint: "/mcp",
                    readTimeout: 120000,
                }),
            );
            expect(res).toBeDefined();
        });
    });

    describe("listMcpTools", () => {
        test("calls POST /mcp/listTools", async () => {
            const client = new Client();
            mockMakeRequest.mockResolvedValue(
                makeHttpResponse({
                    json: {
                        success: true,
                        requestId: "r1",
                        data: { tools: [] },
                    },
                }),
            );

            const req = new ListMcpToolsRequest("img-1", "key");
            const res = await client.listMcpTools(req);

            expect(mockMakeRequest).toHaveBeenCalledWith({
                method: "POST",
                endpoint: "/mcp/listTools",
                params: expect.any(Object),
                jsonData: expect.any(Object),
            });
            expect(res).toBeDefined();
        });
    });

    describe("getMcpResource", () => {
        test("calls POST /mcp/getMcpResource", async () => {
            const client = new Client();
            mockMakeRequest.mockResolvedValue(
                makeHttpResponse({
                    json: { success: true, requestId: "r1", data: {} },
                }),
            );

            const req = new GetMcpResourceRequest("sid-1", "key");
            const res = await client.getMcpResource(req);

            expect(mockMakeRequest).toHaveBeenCalledWith({
                method: "POST",
                endpoint: "/mcp/getMcpResource",
                params: expect.any(Object),
                jsonData: expect.any(Object),
            });
            expect(res).toBeDefined();
        });

        test("throws when sessionId missing", async () => {
            const client = new Client();
            const req = new GetMcpResourceRequest("", "key");

            await expect(client.getMcpResource(req)).rejects.toThrow(
                "session_id is required",
            );
        });
    });

    describe("initBrowser", () => {
        test("calls POST /browser/init", async () => {
            const client = new Client();
            mockMakeRequest.mockResolvedValue(
                makeHttpResponse({
                    json: {
                        success: true,
                        requestId: "r1",
                        data: { browserSessionId: "b1" },
                    },
                }),
            );

            const req = new InitBrowserRequest("key", "sid-1", "/persistent");
            const res = await client.initBrowser(req);

            expect(mockMakeRequest).toHaveBeenCalledWith({
                method: "POST",
                endpoint: "/browser/init",
                params: expect.any(Object),
                jsonData: expect.any(Object),
            });
            expect(res).toBeDefined();
        });
    });

    describe("deleteSessionAsync", () => {
        test("calls POST /mcp/releaseSessionAsync", async () => {
            const client = new Client();
            mockMakeRequest.mockResolvedValue(makeHttpResponse());

            const req = new DeleteSessionAsyncRequest("key", "sid-1");
            const res = await client.deleteSessionAsync(req);

            expect(mockMakeRequest).toHaveBeenCalledWith({
                method: "POST",
                endpoint: "/mcp/releaseSessionAsync",
                params: expect.any(Object),
                jsonData: expect.any(Object),
            });
            expect(res).toBeDefined();
        });
    });
});
