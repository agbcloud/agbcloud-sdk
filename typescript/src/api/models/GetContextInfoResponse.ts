import type { HttpResponse } from "../http-client";

export class GetContextInfoResponse {
    private readonly success: boolean;
    private readonly apiSuccess?: boolean;
    private readonly message?: string;
    private readonly data?: Record<string, unknown>;
    private readonly error?: string;
    private readonly requestId: string;

    constructor(resp: HttpResponse) {
        this.success = resp.success;
        this.requestId = resp.requestId ?? "";
        this.error = resp.text;
        const json = resp.json;
        if (json) {
            this.apiSuccess = json.success as boolean | undefined;
            this.message = json.message as string | undefined;
            this.data = json.data as Record<string, unknown> | undefined;
        }
    }

    static fromHttpResponse(resp: HttpResponse): GetContextInfoResponse {
        return new GetContextInfoResponse(resp);
    }

    isSuccessful(): boolean {
        return this.success === true && this.apiSuccess === true;
    }

    getErrorMessage(): string {
        if (this.error) return this.error;
        if (this.message) return this.message;
        return "Unknown error";
    }

    getContextStatus(): unknown {
        return this.data?.contextStatus;
    }

    getRequestId(): string {
        return this.requestId;
    }
}
