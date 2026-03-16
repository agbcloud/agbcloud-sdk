import type { HttpResponse } from "../http-client";

export interface GetContextData {
    createTime?: string;
    id?: string;
    lastUsedTime?: string;
    name?: string;
    state?: string;
}

export class GetContextResponse {
    private readonly success: boolean;
    private readonly apiSuccess?: boolean;
    private readonly message?: string;
    private readonly data?: GetContextData;
    private readonly error?: string;
    private readonly requestId: string;

    constructor(resp: HttpResponse) {
        this.success = resp.success;
        this.error = resp.text;
        this.requestId = resp.requestId ?? "";
        const json = resp.json;
        if (json) {
            this.apiSuccess = json.success as boolean | undefined;
            this.message = json.message as string | undefined;
            const dataObj = json.data as Record<string, unknown> | undefined;
            this.data = dataObj
                ? {
                    createTime: dataObj.createTime as string | undefined,
                    id: dataObj.id as string | undefined,
                    lastUsedTime: dataObj.lastUsedTime as string | undefined,
                    name: dataObj.name as string | undefined,
                    state: dataObj.state as string | undefined,
                }
                : undefined;
        }
    }

    static fromHttpResponse(resp: HttpResponse): GetContextResponse {
        return new GetContextResponse(resp);
    }

    isSuccessful(): boolean {
        return this.success === true && this.apiSuccess === true;
    }

    getErrorMessage(): string {
        if (this.error) return this.error;
        if (this.message) return this.message;
        return "Unknown error";
    }

    getContextData(): GetContextData | undefined {
        return this.data;
    }

    getRequestId(): string {
        return this.requestId;
    }
}
