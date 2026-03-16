import type { HttpResponse } from "../../src/api/http-client";
import {
    CreateSessionResponse,
    ListSessionResponse,
    CallMcpToolResponse,
    GetCdpLinkResponse,
    ListContextsResponse,
    GetContextResponse,
    ReleaseSessionResponse,
    GetContextFileUploadUrlResponse,
    GetContextFileDownloadUrlResponse,
    GetLinkResponse,
    GetContextInfoResponse,
    ClearContextResponse,
    ModifyContextResponse,
    SyncContextResponse,
    DescribeContextFilesResponse,
    GetAndLoadInternalContextResponse,
    DeleteContextFileResponse,
    DeleteContextResponse,
    GetLabelResponse,
    ListMcpToolsResponse,
    GetSessionDetailResponse,
    GetMcpResourceResponse,
    GetSessionResponse,
} from "../../src/api/models";

function makeResp(overrides: Partial<HttpResponse> = {}): HttpResponse {
    return {
        statusCode: 200,
        url: "",
        headers: {},
        success: true,
        json: { success: true, requestId: "r1", data: {} },
        requestId: "r1",
        ...overrides,
    };
}

describe("API Response models fromHttpResponse", () => {
    describe("CreateSessionResponse", () => {
        test("fromHttpResponse parses sessionId and data", () => {
            const resp = makeResp({
                json: {
                    success: true,
                    requestId: "r1",
                    data: {
                        sessionId: "sid-1",
                        resourceUrl: "https://r",
                        appInstanceId: "a1",
                        resourceId: "res1",
                    },
                },
            });
            const out = CreateSessionResponse.fromHttpResponse(resp);
            expect(out.requestId).toBe("r1");
            expect(out.isSuccessful()).toBe(true);
            expect(out.getSessionId()).toBe("sid-1");
            expect(out.getResourceUrl()).toBe("https://r");
            expect(out.getData()?.sessionId).toBe("sid-1");
        });
    });

    describe("ListSessionResponse", () => {
        test("fromHttpResponse parses session data and nextToken", () => {
            const resp = makeResp({
                json: {
                    success: true,
                    requestId: "r1",
                    data: [
                        { sessionId: "s1", sessionStatus: "Running" },
                        { sessionId: "s2", sessionStatus: "Stopped" },
                    ],
                    nextToken: "tok",
                    maxResults: 10,
                    count: 2,
                },
            });
            const out = ListSessionResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getSessionData()).toHaveLength(2);
            expect(out.getSessionData()[0].sessionId).toBe("s1");
            expect(out.getNextToken()).toBe("tok");
            expect(out.getMaxResults()).toBe(10);
            expect(out.getCount()).toBe(2);
        });
    });

    describe("CallMcpToolResponse", () => {
        test("fromHttpResponse parses text content", () => {
            const resp = makeResp({
                json: {
                    success: true,
                    requestId: "r1",
                    data: {
                        isError: false,
                        content: [{ type: "text", text: "hello" }],
                    },
                },
            });
            const out = CallMcpToolResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getToolResult()).toBe("hello");
        });

        test("fromHttpResponse parses image data when no text", () => {
            const resp = makeResp({
                json: {
                    success: true,
                    requestId: "r1",
                    data: {
                        isError: false,
                        content: [{ type: "image", data: "base64data" }],
                    },
                },
            });
            const out = CallMcpToolResponse.fromHttpResponse(resp);
            expect(out.getToolResult()).toBe("base64data");
        });
    });

    describe("GetCdpLinkResponse", () => {
        test("fromHttpResponse parses url", () => {
            const resp = makeResp({
                json: {
                    success: true,
                    requestId: "r1",
                    data: { url: "http://cdp.example" },
                },
            });
            const out = GetCdpLinkResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getUrl()).toBe("http://cdp.example");
        });
    });

    describe("ListContextsResponse", () => {
        test("fromHttpResponse parses contexts data", () => {
            const resp = makeResp({
                json: {
                    success: true,
                    requestId: "r1",
                    data: [
                        { id: "c1", name: "ctx1", createTime: "2024-01-01", lastUsedTime: "2024-01-02" },
                    ],
                },
            });
            const out = ListContextsResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getContextsData()).toHaveLength(1);
            expect(out.getContextsData()[0].id).toBe("c1");
            expect(out.getRequestId()).toBe("r1");
        });
    });

    describe("GetContextResponse", () => {
        test("fromHttpResponse parses context data", () => {
            const resp = makeResp({
                json: {
                    success: true,
                    requestId: "r1",
                    data: { id: "c1", name: "my-ctx", createTime: "2024-01-01", lastUsedTime: "2024-01-02" },
                },
            });
            const out = GetContextResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getContextData()?.id).toBe("c1");
            expect(out.getContextData()?.name).toBe("my-ctx");
        });
    });

    describe("ReleaseSessionResponse", () => {
        test("fromHttpResponse isSuccessful when 200 and api success", () => {
            const resp = makeResp({ statusCode: 200, json: { success: true, requestId: "r1" } });
            const out = ReleaseSessionResponse.fromHttpResponse(resp);
            expect(out.requestId).toBe("r1");
            expect(out.statusCode).toBe(200);
        });
    });

    describe("GetContextFileUploadUrlResponse", () => {
        test("fromHttpResponse parses url and expireTime", () => {
            const resp = makeResp({
                json: { success: true, requestId: "r1", data: { url: "https://upload.example", expireTime: "2024-12-31" } },
            });
            const out = GetContextFileUploadUrlResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getUploadUrl()).toBe("https://upload.example");
            expect(out.getExpireTime()).toBe("2024-12-31");
            expect(out.getRequestId()).toBe("r1");
        });
        test("getErrorMessage returns error then message then Unknown error", () => {
            const resp = makeResp({ success: false, text: "network error", json: { success: false, message: "api msg" } });
            const out = GetContextFileUploadUrlResponse.fromHttpResponse(resp);
            expect(out.getErrorMessage()).toBe("network error");
            const resp2 = makeResp({ success: true, json: { success: false, message: "api msg" } });
            const out2 = GetContextFileUploadUrlResponse.fromHttpResponse(resp2);
            expect(out2.getErrorMessage()).toBe("api msg");
        });
    });

    describe("GetContextFileDownloadUrlResponse", () => {
        test("fromHttpResponse parses url", () => {
            const resp = makeResp({
                json: { success: true, requestId: "r1", data: { url: "https://download.example" } },
            });
            const out = GetContextFileDownloadUrlResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getDownloadUrl()).toBe("https://download.example");
        });
    });

    describe("GetLinkResponse", () => {
        test("fromHttpResponse parses url when 200 and api success", () => {
            const resp = makeResp({
                statusCode: 200,
                json: { success: true, requestId: "r1", data: { url: "https://link.example" }, code: "OK" },
            });
            const out = GetLinkResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getUrl()).toBe("https://link.example");
        });
        test("isSuccessful false when statusCode not 200", () => {
            const resp = makeResp({ statusCode: 500, json: { success: true } });
            const out = GetLinkResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(false);
        });
    });

    describe("GetContextInfoResponse", () => {
        test("fromHttpResponse parses contextStatus", () => {
            const resp = makeResp({
                json: { success: true, requestId: "r1", data: { contextStatus: "Ready" } },
            });
            const out = GetContextInfoResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getContextStatus()).toBe("Ready");
        });
    });

    describe("ClearContextResponse", () => {
        test("fromHttpResponse isSuccessful and getRequestId", () => {
            const resp = makeResp({ json: { success: true, requestId: "r1" } });
            const out = ClearContextResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getRequestId()).toBe("r1");
        });
    });

    describe("ModifyContextResponse", () => {
        test("fromHttpResponse getErrorMessage", () => {
            const resp = makeResp({ json: { success: false, message: "modify failed" } });
            const out = ModifyContextResponse.fromHttpResponse(resp);
            expect(out.getErrorMessage()).toBe("modify failed");
        });
    });

    describe("SyncContextResponse", () => {
        test("fromHttpResponse isSuccessful", () => {
            const resp = makeResp({ json: { success: true, requestId: "r1" } });
            const out = SyncContextResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
        });
    });

    describe("DeleteContextFileResponse", () => {
        test("fromHttpResponse isSuccessful", () => {
            const resp = makeResp({ json: { success: true, requestId: "r1" } });
            const out = DeleteContextFileResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
        });
    });

    describe("DeleteContextResponse", () => {
        test("fromHttpResponse isSuccessful", () => {
            const resp = makeResp({ json: { success: true, requestId: "r1" } });
            const out = DeleteContextResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
        });
    });

    describe("DescribeContextFilesResponse", () => {
        test("fromHttpResponse parses files data and nextToken", () => {
            const resp = makeResp({
                statusCode: 200,
                json: {
                    success: true,
                    requestId: "r1",
                    data: [
                        { fileId: "f1", fileName: "a.txt", filePath: "/a.txt", size: 100 },
                    ],
                    nextToken: "tok",
                    count: 1,
                    maxResults: 10,
                },
            });
            const out = DescribeContextFilesResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getFilesData()).toHaveLength(1);
            expect(out.getFilesData()[0].fileId).toBe("f1");
            expect(out.getNextToken()).toBe("tok");
            expect(out.getMaxResults()).toBe(10);
        });
        test("getErrorMessage when not successful", () => {
            const resp = makeResp({ statusCode: 500, json: { success: false, message: "err" } });
            const out = DescribeContextFilesResponse.fromHttpResponse(resp);
            expect(out.getErrorMessage()).toContain("err");
        });
    });

    describe("GetAndLoadInternalContextResponse", () => {
        test("fromHttpResponse parses context list", () => {
            const resp = makeResp({
                json: {
                    success: true,
                    requestId: "r1",
                    data: [
                        { contextId: "c1", contextType: "type1", contextPath: "/p1" },
                    ],
                },
            });
            const out = GetAndLoadInternalContextResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getContextList()).toHaveLength(1);
            expect(out.getContextList()[0].contextId).toBe("c1");
        });
    });

    describe("GetLabelResponse", () => {
        test("fromHttpResponse isSuccessful and getLabelsData", () => {
            const resp = makeResp({ json: { success: true, requestId: "r1", data: { labels: "a,b" } } });
            const out = GetLabelResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getLabelsData()).toEqual({ labels: "a,b" });
        });
        test("getCount/getNextToken/getMaxResults when data is object", () => {
            const resp = makeResp({
                json: { success: true, requestId: "r1", data: { count: 5, nextToken: "tok", maxResults: 10 } },
            });
            const out = GetLabelResponse.fromHttpResponse(resp);
            expect(out.getCount()).toBe(5);
            expect(out.getNextToken()).toBe("tok");
            expect(out.getMaxResults()).toBe(10);
        });
    });

    describe("ListMcpToolsResponse", () => {
        test("fromHttpResponse isSuccessful when 200 and api success", () => {
            const resp = makeResp({ statusCode: 200, json: { success: true, requestId: "r1", data: "tool1,tool2" } });
            const out = ListMcpToolsResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getToolsList()).toBe("tool1,tool2");
        });
        test("isSuccessful false when statusCode not 200", () => {
            const resp = makeResp({ statusCode: 500, json: { success: true } });
            const out = ListMcpToolsResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(false);
        });
        test("getErrorMessage returns error when data.isError", () => {
            const resp = makeResp({
                json: { success: true, requestId: "r1", data: { isError: true, errMsg: "tool error" } },
            });
            const out = ListMcpToolsResponse.fromHttpResponse(resp);
            expect(out.getErrorMessage()).toBe("tool error");
        });
    });

    describe("GetSessionDetailResponse", () => {
        test("fromHttpResponse parses status", () => {
            const resp = makeResp({
                json: { success: true, requestId: "r1", data: { status: "Running" } },
            });
            const out = GetSessionDetailResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getStatus()).toBe("Running");
        });
        test("getStatus returns empty when no data", () => {
            const resp = makeResp({ json: { success: true, requestId: "r1" } });
            const out = GetSessionDetailResponse.fromHttpResponse(resp);
            expect(out.getStatus()).toBe("");
        });
    });

    describe("GetMcpResourceResponse", () => {
        test("fromHttpResponse parses resourceData", () => {
            const resp = makeResp({
                json: {
                    success: true,
                    requestId: "r1",
                    data: { sessionId: "sid", resourceUrl: "https://r", desktopInfo: { appId: "app1" } },
                },
            });
            const out = GetMcpResourceResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getResourceData()?.sessionId).toBe("sid");
            expect(out.getResourceUrl()).toBe("https://r");
        });
    });

    describe("GetSessionResponse", () => {
        test("fromHttpResponse parses session data", () => {
            const resp = makeResp({
                json: {
                    success: true,
                    requestId: "r1",
                    data: { sessionId: "sid", appInstanceId: "app1", resourceUrl: "https://r", status: "Running" },
                },
            });
            const out = GetSessionResponse.fromHttpResponse(resp);
            expect(out.isSuccessful()).toBe(true);
            expect(out.getSessionId()).toBe("sid");
            expect(out.getResourceUrl()).toBe("https://r");
            expect(out.getData()?.status).toBe("Running");
        });
    });
});
