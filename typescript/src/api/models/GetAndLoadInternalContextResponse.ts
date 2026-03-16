import type { HttpResponse } from "../http-client";
import type { GetAndLoadInternalContextItem } from "./GetAndLoadInternalContextRequest";

export class GetAndLoadInternalContextResponse {
    readonly requestId: string;
    readonly statusCode: number;
    private readonly success: boolean;
    private readonly apiSuccess?: boolean;
    private readonly message?: string;
    private readonly data?: unknown;
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
            this.data = json.data;
        }
    }

    static fromHttpResponse(resp: HttpResponse): GetAndLoadInternalContextResponse {
        return new GetAndLoadInternalContextResponse(resp);
    }

    isSuccessful(): boolean {
        return this.success === true && this.apiSuccess === true;
    }

    getErrorMessage(): string {
        if (this.error) return this.error;
        if (this.message) return this.message;
        return "Unknown error";
    }

    getContextList(): GetAndLoadInternalContextItem[] {
        if (!this.isSuccessful()) return [];
        if (Array.isArray(this.data)) {
            return this.data.map((item) => {
                const obj = item as Record<string, unknown>;
                return {
                    contextId: obj.contextId as string | undefined,
                    contextType: obj.contextType as string | undefined,
                    contextPath: obj.contextPath as string | undefined,
                };
            });
        }
        return [];
    }
}
