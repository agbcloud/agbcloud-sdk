import type { Config } from "../config";
import { HTTPClient } from "./http-client";
import {
    CreateSessionRequest,
    CreateSessionResponse,
    ReleaseSessionRequest,
    ReleaseSessionResponse,
    GetSessionRequest,
    GetSessionResponse,
    GetSessionDetailRequest,
    GetSessionDetailResponse,
    ListSessionRequest,
    ListSessionResponse,
    DeleteSessionAsyncRequest,
    DeleteSessionAsyncResponse,
    RefreshSessionIdleTimeRequest,
    RefreshSessionIdleTimeResponse,
    CallMcpToolRequest,
    CallMcpToolResponse,
    ListMcpToolsRequest,
    ListMcpToolsResponse,
    GetMcpResourceRequest,
    GetMcpResourceResponse,
    SetLabelRequest,
    SetLabelResponse,
    GetLabelRequest,
    GetLabelResponse,
    GetLinkRequest,
    GetLinkResponse,
    GetCdpLinkRequest,
    GetCdpLinkResponse,
    InitBrowserRequest,
    InitBrowserResponse,
    ListContextsRequest,
    ListContextsResponse,
    GetContextRequest,
    GetContextResponse,
    ModifyContextRequest,
    ModifyContextResponse,
    DeleteContextRequest,
    DeleteContextResponse,
    ClearContextRequest,
    ClearContextResponse,
    SyncContextRequest,
    SyncContextResponse,
    GetContextInfoRequest,
    GetContextInfoResponse,
    GetContextFileDownloadUrlRequest,
    GetContextFileDownloadUrlResponse,
    GetContextFileUploadUrlRequest,
    GetContextFileUploadUrlResponse,
    DeleteContextFileRequest,
    DeleteContextFileResponse,
    DescribeContextFilesRequest,
    DescribeContextFilesResponse,
    GetAndLoadInternalContextRequest,
    GetAndLoadInternalContextResponse,
} from "./models";

function requireAuth(authorization: string | undefined): void {
    if (!authorization) {
        throw new Error("authorization is required");
    }
}

function requireSessionId(sessionId: string | undefined): void {
    if (!sessionId) {
        throw new Error("session_id is required");
    }
}

export class Client {
    private config?: Config;

    constructor(config?: Config) {
        this.config = config;
    }

    private getHttpClient(apiKey: string): HTTPClient {
        return new HTTPClient(apiKey, this.config);
    }

    async createMcpSession(
        request: CreateSessionRequest,
    ): Promise<CreateSessionResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/mcp/createSession",
                params: request.getParams(),
                jsonData: request.getBody(),
            });
            return CreateSessionResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async releaseMcpSession(
        request: ReleaseSessionRequest,
    ): Promise<ReleaseSessionResponse> {
        requireSessionId(request.sessionId);
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization!);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/mcp/releaseSession",
                params: request.getParams(),
                jsonData: request.getBody(),
            });
            return ReleaseSessionResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async getMcpSession(
        request: GetSessionRequest,
    ): Promise<GetSessionResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/mcp/getSession",
                params: request.getParams(),
                jsonData: request.getBody(),
            });
            return GetSessionResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async getSessionDetail(
        request: GetSessionDetailRequest,
    ): Promise<GetSessionDetailResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/mcp/getSessionInfo",
                params: request.getParams(),
                jsonData: request.getBody(),
            });
            return GetSessionDetailResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async listSessions(
        request: ListSessionRequest,
    ): Promise<ListSessionResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "GET",
                endpoint: "/sdk/ListSession",
                params: request.getParams(),
            });
            return ListSessionResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async callMcpTool(
        request: CallMcpToolRequest,
        readTimeout?: number,
        connectTimeout?: number,
    ): Promise<CallMcpToolResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization!);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/mcp",
                params: request.getParams(),
                jsonData: request.getBody(),
                readTimeout,
                connectTimeout,
            });
            return CallMcpToolResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async listMcpTools(
        request: ListMcpToolsRequest,
    ): Promise<ListMcpToolsResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization!);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/mcp/listTools",
                params: request.getParams(),
                jsonData: request.getBody(),
            });
            return ListMcpToolsResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async getMcpResource(
        request: GetMcpResourceRequest,
    ): Promise<GetMcpResourceResponse> {
        requireSessionId(request.sessionId);
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization!);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/mcp/getMcpResource",
                params: request.getParams(),
                jsonData: request.getBody(),
            });
            return GetMcpResourceResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async initBrowser(
        request: InitBrowserRequest,
    ): Promise<InitBrowserResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/browser/init",
                params: request.getParams(),
                jsonData: request.getBody(),
            });
            return InitBrowserResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async getLink(request: GetLinkRequest): Promise<GetLinkResponse> {
        requireAuth(request.authorization);
        requireSessionId(request.sessionId);
        const http = this.getHttpClient(request.authorization!);
        try {
            const resp = await http.makeRequest({
                method: "GET",
                endpoint: "/internet/getLink",
                params: request.getParams(),
            });
            return GetLinkResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async getCdpLink(
        request: GetCdpLinkRequest,
    ): Promise<GetCdpLinkResponse> {
        requireAuth(request.authorization);
        requireSessionId(request.sessionId);
        const http = this.getHttpClient(request.authorization!);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/internet/getCdpLink",
                params: request.getParams(),
                jsonData: request.getBody(),
            });
            return GetCdpLinkResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async setLabel(request: SetLabelRequest): Promise<SetLabelResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/sdk/SetLabel",
                params: request.getParams(),
            });
            return SetLabelResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async getLabel(request: GetLabelRequest): Promise<GetLabelResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "GET",
                endpoint: "/sdk/GetLabel",
                params: request.getParams(),
            });
            return GetLabelResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async deleteSessionAsync(
        request: DeleteSessionAsyncRequest,
    ): Promise<DeleteSessionAsyncResponse> {
        requireAuth(request.authorization);
        requireSessionId(request.sessionId);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/mcp/releaseSessionAsync",
                params: request.getParams(),
                jsonData: request.getBody(),
            });
            return DeleteSessionAsyncResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async refreshSessionIdleTime(
        request: RefreshSessionIdleTimeRequest,
    ): Promise<RefreshSessionIdleTimeResponse> {
        requireAuth(request.authorization);
        requireSessionId(request.sessionId);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/mcp/refreshSessionIdleTime",
                params: request.getParams(),
                jsonData: request.getBody(),
            });
            return RefreshSessionIdleTimeResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    // ---- Context methods ----

    async listContexts(
        request: ListContextsRequest,
    ): Promise<ListContextsResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "GET",
                endpoint: "/sdk/ListContexts",
                params: request.getParams(),
            });
            return ListContextsResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async getContext(
        request: GetContextRequest,
    ): Promise<GetContextResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "GET",
                endpoint: "/sdk/GetContext",
                params: request.getParams(),
            });
            return GetContextResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async modifyContext(
        request: ModifyContextRequest,
    ): Promise<ModifyContextResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/sdk/ModifyContext",
                params: request.getParams(),
            });
            return ModifyContextResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async deleteContext(
        request: DeleteContextRequest,
    ): Promise<DeleteContextResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/sdk/DeleteContext",
                params: request.getParams(),
            });
            return DeleteContextResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async clearContext(
        request: ClearContextRequest,
    ): Promise<ClearContextResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/sdk/ClearContext",
                params: request.getParams(),
            });
            return ClearContextResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async syncContext(
        request: SyncContextRequest,
    ): Promise<SyncContextResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/sdk/SyncContext",
                params: request.getParams(),
            });
            return SyncContextResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async getContextInfo(
        request: GetContextInfoRequest,
    ): Promise<GetContextInfoResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "GET",
                endpoint: "/sdk/GetContextInfo",
                params: request.getParams(),
            });
            return GetContextInfoResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async getContextFileDownloadUrl(
        request: GetContextFileDownloadUrlRequest,
    ): Promise<GetContextFileDownloadUrlResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/sdk/GetContextFileDownloadUrl",
                params: request.getParams(),
            });
            return GetContextFileDownloadUrlResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async getContextFileUploadUrl(
        request: GetContextFileUploadUrlRequest,
    ): Promise<GetContextFileUploadUrlResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/sdk/GetContextFileUploadUrl",
                params: request.getParams(),
            });
            return GetContextFileUploadUrlResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async deleteContextFile(
        request: DeleteContextFileRequest,
    ): Promise<DeleteContextFileResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/sdk/DeleteContextFile",
                params: request.getParams(),
            });
            return DeleteContextFileResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async describeContextFiles(
        request: DescribeContextFilesRequest,
    ): Promise<DescribeContextFilesResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/sdk/DescribeContextFiles",
                params: request.getParams(),
            });
            return DescribeContextFilesResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    async getAndLoadInternalContext(
        request: GetAndLoadInternalContextRequest,
    ): Promise<GetAndLoadInternalContextResponse> {
        requireAuth(request.authorization);
        const http = this.getHttpClient(request.authorization);
        try {
            const resp = await http.makeRequest({
                method: "POST",
                endpoint: "/sdk/GetAndLoadInternalContext",
                params: request.getParams(),
            });
            return GetAndLoadInternalContextResponse.fromHttpResponse(resp);
        } finally {
            http.close();
        }
    }

    close(): void {
        // No long-lived HTTP client to clean up
    }
}
