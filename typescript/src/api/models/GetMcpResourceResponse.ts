import type { HttpResponse } from "../http-client";
import type { McpResourceData } from "./GetMcpResourceRequest";

export class GetMcpResourceResponse {
    readonly requestId: string;
    readonly statusCode: number;
    private readonly success: boolean;
    private readonly apiSuccess?: boolean;
    private readonly message?: string;
    private readonly data?: McpResourceData;
    private readonly error?: string;

    constructor(resp: HttpResponse) {
        this.requestId = resp.requestId ?? "";
        this.statusCode = resp.statusCode;
        this.success = resp.success;
        this.error = resp.text;
        const json = resp.json;
        if (json) {
            this.apiSuccess = json.success as boolean | undefined;
            this.message = json.message as string | undefined;
            const dataObj = json.data as Record<string, unknown> | undefined;
            this.data = dataObj
                ? {
                    desktopInfo: dataObj.desktopInfo,
                    resourceUrl: dataObj.resourceUrl as string | undefined,
                    sessionId: dataObj.sessionId as string | undefined,
                }
                : undefined;
        }
    }

    static fromHttpResponse(resp: HttpResponse): GetMcpResourceResponse {
        return new GetMcpResourceResponse(resp);
    }

    isSuccessful(): boolean {
        return this.success === true && this.apiSuccess === true;
    }

    getErrorMessage(): string {
        if (this.error) return this.error;
        if (this.message) return this.message;
        return "Unknown error";
    }

    getResourceData(): McpResourceData | undefined {
        return this.data;
    }

    getResourceUrl(): string | undefined {
        return this.data?.resourceUrl;
    }
}
