import {
    GetCdpLinkRequest,
    SetLabelRequest,
    GetContextRequest,
    ListContextsRequest,
    GetContextFileUploadUrlRequest,
    GetContextFileDownloadUrlRequest,
    DeleteContextFileRequest,
    GetLinkRequest,
    DescribeContextFilesRequest,
    ClearContextRequest,
    GetContextInfoRequest,
    SyncContextRequest,
    GetAndLoadInternalContextRequest,
} from "../../src/api/models";

describe("API Request models getParams/getBody", () => {
    describe("GetCdpLinkRequest", () => {
        test("getParams includes sessionId when set", () => {
            const req = new GetCdpLinkRequest("auth", "sid-1");
            expect(req.getParams()).toEqual({ sessionId: "sid-1" });
        });
        test("getParams omits sessionId when not set", () => {
            const req = new GetCdpLinkRequest();
            expect(req.getParams()).toEqual({});
        });
        test("getBody returns empty object", () => {
            const req = new GetCdpLinkRequest("auth", "sid-1");
            expect(req.getBody()).toEqual({});
        });
    });

    describe("SetLabelRequest", () => {
        test("getParams includes sessionId and Labels when set", () => {
            const req = new SetLabelRequest("auth", "sid-1", "a,b");
            expect(req.getParams()).toEqual({ sessionId: "sid-1", Labels: "a,b" });
        });
        test("getParams omits optional when not set", () => {
            const req = new SetLabelRequest();
            expect(req.getParams()).toEqual({});
        });
        test("getBody returns empty object", () => {
            expect(new SetLabelRequest("a").getBody()).toEqual({});
        });
    });

    describe("GetContextRequest", () => {
        test("getParams includes id, name, allowCreate, loginRegionId", () => {
            const req = new GetContextRequest("auth", "id1", "n1", true, "region1");
            expect(req.getParams()).toEqual({
                id: "id1",
                name: "n1",
                allowCreate: "true",
                loginRegionId: "region1",
            });
        });
        test("getParams allowCreate is string", () => {
            const req = new GetContextRequest("", undefined, undefined, false);
            expect(req.getParams().allowCreate).toBe("false");
        });
        test("getBody returns empty object", () => {
            expect(new GetContextRequest().getBody()).toEqual({});
        });
    });

    describe("ListContextsRequest", () => {
        test("getParams includes maxResults and nextToken when set", () => {
            const req = new ListContextsRequest("auth", 20, "tok");
            expect(req.getParams()).toEqual({ maxResults: 20, nextToken: "tok" });
        });
        test("getParams empty when not set", () => {
            expect(new ListContextsRequest().getParams()).toEqual({});
        });
        test("getBody returns empty object", () => {
            expect(new ListContextsRequest().getBody()).toEqual({});
        });
    });

    describe("GetContextFileUploadUrlRequest", () => {
        test("getParams returns contextId and filePath", () => {
            const req = new GetContextFileUploadUrlRequest("auth", "ctx1", "/p/file.txt");
            expect(req.getParams()).toEqual({ contextId: "ctx1", filePath: "/p/file.txt" });
        });
        test("getBody returns empty object", () => {
            expect(new GetContextFileUploadUrlRequest().getBody()).toEqual({});
        });
    });

    describe("GetContextFileDownloadUrlRequest", () => {
        test("getParams returns contextId and filePath", () => {
            const req = new GetContextFileDownloadUrlRequest("auth", "ctx1", "/p/file.txt");
            expect(req.getParams()).toEqual({ contextId: "ctx1", filePath: "/p/file.txt" });
        });
    });

    describe("DeleteContextFileRequest", () => {
        test("getParams returns contextId and filePath", () => {
            const req = new DeleteContextFileRequest("auth", "ctx1", "/p/file.txt");
            expect(req.getParams()).toEqual({ contextId: "ctx1", filePath: "/p/file.txt" });
        });
        test("getBody returns empty object", () => {
            expect(new DeleteContextFileRequest("a", "c", "p").getBody()).toEqual({});
        });
    });

    describe("GetLinkRequest", () => {
        test("getParams includes sessionId, protocolType, port when set", () => {
            const req = new GetLinkRequest("auth", 9222, "cdp", "sid-1");
            expect(req.getParams()).toEqual({ sessionId: "sid-1", protocolType: "cdp", port: 9222 });
        });
        test("getParams empty when optional not set", () => {
            expect(new GetLinkRequest().getParams()).toEqual({});
        });
    });

    describe("DescribeContextFilesRequest", () => {
        test("getParams returns contextId, parentFolderPath, pageNumber, pageSize", () => {
            const req = new DescribeContextFilesRequest("auth", "ctx1", "/folder", 2, 20);
            expect(req.getParams()).toEqual({
                contextId: "ctx1",
                parentFolderPath: "/folder",
                pageNumber: "2",
                pageSize: "20",
            });
        });
    });

    describe("ClearContextRequest", () => {
        test("getParams returns id", () => {
            const req = new ClearContextRequest("auth", "ctx-id");
            expect(req.getParams()).toEqual({ id: "ctx-id" });
        });
    });

    describe("GetContextInfoRequest", () => {
        test("getParams includes sessionId and optional contextId, path, taskType", () => {
            const req = new GetContextInfoRequest("auth", "sid", "ctx1", "/p", "sync");
            expect(req.getParams()).toEqual({ sessionId: "sid", contextId: "ctx1", path: "/p", taskType: "sync" });
        });
    });

    describe("SyncContextRequest", () => {
        test("getParams includes sessionId and optional contextId, path, mode", () => {
            const req = new SyncContextRequest("auth", "sid", "ctx1", "/p", "full");
            expect(req.getParams()).toEqual({ sessionId: "sid", contextId: "ctx1", path: "/p", mode: "full" });
        });
    });

    describe("GetAndLoadInternalContextRequest", () => {
        test("getParams includes sessionId and contextTypes as JSON string", () => {
            const req = new GetAndLoadInternalContextRequest("auth", "sid", ["type1", "type2"]);
            expect(req.getParams()).toEqual({ sessionId: "sid", contextTypes: '["type1","type2"]' });
        });
        test("getParams omits contextTypes when empty", () => {
            const req = new GetAndLoadInternalContextRequest("auth", "sid", []);
            expect(req.getParams()).toEqual({ sessionId: "sid" });
        });
    });
});
