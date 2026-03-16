import type { HttpResponse } from "../http-client";
import type { SessionData } from "./CreateSessionRequest";

export class CreateSessionResponse {
    readonly requestId: string;
    readonly statusCode: number;
    readonly code?: string;
    readonly httpStatusCode?: number;
    private readonly success: boolean;
    private readonly apiSuccess?: boolean;
    private readonly message?: string;
    private readonly accessDeniedDetail?: unknown;
    private readonly data?: SessionData;
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
                    appInstanceId: dataObj.appInstanceId as string | undefined,
                    resourceId: dataObj.resourceId as string | undefined,
                    resourceUrl: dataObj.resourceUrl as string | undefined,
                    success: dataObj.success as boolean | undefined,
                    errMsg: dataObj.errMsg as string | undefined,
                    sessionId: dataObj.sessionId as string | undefined,
                    taskId: dataObj.taskId as string | undefined,
                    networkInterfaceIp: dataObj.networkInterfaceIp as string | undefined,
                }
                : undefined;
        }
    }

    static fromHttpResponse(resp: HttpResponse): CreateSessionResponse {
        return new CreateSessionResponse(resp);
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

    getErrorMessage(): string {
        if (this.error) return this.error;
        if (this.data?.errMsg) return this.data.errMsg;
        if (this.message) return this.message;
        return "Unknown error";
    }

    getData(): SessionData | undefined {
        return this.data;
    }
}
