import type { HttpResponse } from "../http-client";

export class SyncContextResponse {
    private readonly success: boolean;
    private readonly apiSuccess?: boolean;
    private readonly message?: string;
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
        }
    }

    static fromHttpResponse(resp: HttpResponse): SyncContextResponse {
        return new SyncContextResponse(resp);
    }

    isSuccessful(): boolean {
        return this.success === true && this.apiSuccess === true;
    }

    getErrorMessage(): string {
        if (this.error) return this.error;
        if (this.message) return this.message;
        return "Unknown error";
    }

    getRequestId(): string {
        return this.requestId;
    }
}
