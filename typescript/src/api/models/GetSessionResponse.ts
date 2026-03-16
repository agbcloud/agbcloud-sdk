import type { HttpResponse } from "../http-client";

export interface GetSessionSessionData {
    sessionId?: string;
    appInstanceId?: string;
    resourceId?: string;
    resourceUrl?: string;
    status?: string;
}

export class GetSessionResponse {
    readonly requestId: string;
    readonly statusCode: number;
    readonly code?: string;
    readonly httpStatusCode?: number;
    private readonly success: boolean;
    private readonly apiSuccess?: boolean;
    private readonly message?: string;
    private readonly accessDeniedDetail?: unknown;
    private readonly data?: GetSessionSessionData;
    private readonly error?: string;

    constructor(resp: HttpResponse) {
        this.requestId = resp.requestId ?? "";
        this.statusCode = resp.statusCode;
        this.success = resp.success;
        this.error = resp.text;
        const json = resp.json;
        if (json) {
            this.apiSuccess = json.success as boolean | undefined;
            this.code = json.code as string | undefined;
            this.message = json.message as string | undefined;
            this.httpStatusCode = json.httpStatusCode as number | undefined;
            this.accessDeniedDetail = json.accessDeniedDetail;
            const dataObj = json.data as Record<string, unknown> | undefined;
            this.data = dataObj
                ? {
                    sessionId: dataObj.sessionId as string | undefined,
                    appInstanceId: dataObj.appInstanceId as string | undefined,
                    resourceId: dataObj.resourceId as string | undefined,
                    resourceUrl: dataObj.resourceUrl as string | undefined,
                    status: dataObj.status as string | undefined,
                }
                : undefined;
        }
    }

    static fromHttpResponse(resp: HttpResponse): GetSessionResponse {
        return new GetSessionResponse(resp);
    }

    isSuccessful(): boolean {
        return this.success === true && this.apiSuccess === true;
    }

    getSessionId(): string | undefined {
        return this.data?.sessionId;
    }

    getResourceUrl(): string | undefined {
        return this.data?.resourceUrl;
    }

    getData(): GetSessionSessionData | undefined {
        return this.data;
    }

    getErrorMessage(): string {
        if (this.error) return this.error;
        if (this.message) return this.message;
        return "Unknown error";
    }
}
