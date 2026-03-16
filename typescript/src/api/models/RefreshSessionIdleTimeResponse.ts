import type { HttpResponse } from "../http-client";

export class RefreshSessionIdleTimeResponse {
    readonly requestId: string;
    readonly statusCode: number;
    private readonly success: boolean;
    private readonly apiSuccess?: boolean;
    private readonly code?: string;
    private readonly httpStatusCode?: number;
    private readonly message?: string;
    private readonly data?: unknown;
    private readonly error?: string;

    constructor(resp: HttpResponse) {
        this.statusCode = resp.statusCode;
        this.success = resp.success;
        this.error = resp.text;
        let reqId = resp.requestId ?? "";
        const json = resp.json;
        if (json) {
            const body = (json.body as Record<string, unknown>) ?? json;
            this.apiSuccess =
                (body.Success as boolean | undefined) ??
                (body.success as boolean | undefined);
            this.code =
                (body.Code as string | undefined) ??
                (body.code as string | undefined);
            this.message =
                (body.Message as string | undefined) ??
                (body.message as string | undefined);
            this.httpStatusCode =
                (body.HttpStatusCode as number | undefined) ??
                (body.httpStatusCode as number | undefined);
            this.data =
                (body.Data as unknown | undefined) ??
                (body.data as unknown | undefined);
            if (!reqId) {
                reqId =
                    (body.RequestId as string) ??
                    (body.requestId as string) ??
                    "";
            }
        }
        this.requestId = reqId;
    }

    static fromHttpResponse(resp: HttpResponse): RefreshSessionIdleTimeResponse {
        return new RefreshSessionIdleTimeResponse(resp);
    }

    isSuccessful(): boolean {
        return this.success === true && this.statusCode === 200 && this.apiSuccess === true;
    }

    getErrorMessage(): string {
        if (this.error) return this.error;
        if (this.message) return this.message;
        return "Unknown error";
    }

    getData(): unknown {
        return this.data;
    }
}
