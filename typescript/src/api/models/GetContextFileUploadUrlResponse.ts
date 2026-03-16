import type { HttpResponse } from "../http-client";

export class GetContextFileUploadUrlResponse {
    private readonly success: boolean;
    private readonly apiSuccess?: boolean;
    private readonly message?: string;
    private readonly data?: { expireTime?: string; url?: string };
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
            const dataObj = json.data as Record<string, unknown> | undefined;
            this.data = dataObj
                ? {
                    expireTime: dataObj.expireTime as string | undefined,
                    url: dataObj.url as string | undefined,
                }
                : undefined;
        }
    }

    static fromHttpResponse(resp: HttpResponse): GetContextFileUploadUrlResponse {
        return new GetContextFileUploadUrlResponse(resp);
    }

    isSuccessful(): boolean {
        return this.success === true && this.apiSuccess === true;
    }

    getErrorMessage(): string {
        if (this.error) return this.error;
        if (this.message) return this.message;
        return "Unknown error";
    }

    getUploadUrl(): string | undefined {
        return this.data?.url;
    }

    getExpireTime(): string | undefined {
        return this.data?.expireTime;
    }

    getUploadUrlData(): { expireTime?: string; url?: string } | undefined {
        return this.data;
    }

    getRequestId(): string {
        return this.requestId;
    }
}
