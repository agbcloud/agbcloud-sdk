import type { HttpResponse } from "../http-client";

export class GetSessionDetailResponse {
    readonly requestId: string;
    readonly statusCode: number;
    readonly code?: string;
    readonly httpStatusCode?: number;
    private readonly success: boolean;
    private readonly apiSuccess?: boolean;
    private readonly message?: string;
    private readonly data?: Record<string, unknown>;
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
            this.data = json.data as Record<string, unknown> | undefined;
        }
    }

    static fromHttpResponse(resp: HttpResponse): GetSessionDetailResponse {
        return new GetSessionDetailResponse(resp);
    }

    isSuccessful(): boolean {
        return this.success === true && this.apiSuccess === true;
    }

    getErrorMessage(): string {
        if (this.error) return this.error;
        if (this.message) return this.message;
        return "Unknown error";
    }

    getStatus(): string {
        if (!this.data || typeof this.data !== "object") return "";
        return (
            (this.data.status as string) ??
            (this.data.Status as string) ??
            ""
        );
    }
}
