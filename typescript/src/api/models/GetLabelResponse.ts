import type { HttpResponse } from "../http-client";

export class GetLabelResponse {
    readonly requestId: string;
    readonly statusCode: number;
    readonly code?: string;
    readonly httpStatusCode?: number;
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
            this.code = json.code as string | undefined;
            this.message = json.message as string | undefined;
            this.httpStatusCode = json.httpStatusCode as number | undefined;
            this.data = json.data;
        }
    }

    static fromHttpResponse(resp: HttpResponse): GetLabelResponse {
        return new GetLabelResponse(resp);
    }

    isSuccessful(): boolean {
        return this.success === true && this.apiSuccess === true;
    }

    getErrorMessage(): string {
        if (this.error) return this.error;
        if (this.message) return this.message;
        return "Unknown error";
    }

    getLabelsData(): unknown {
        return this.data;
    }

    getCount(): number | undefined {
        if (!this.isSuccessful()) return undefined;
        if (this.data && typeof this.data === "object") {
            return (this.data as Record<string, unknown>).count as number | undefined;
        }
        return undefined;
    }

    getNextToken(): string | undefined {
        if (!this.isSuccessful()) return undefined;
        if (this.data && typeof this.data === "object") {
            return (this.data as Record<string, unknown>).nextToken as string | undefined;
        }
        return undefined;
    }

    getMaxResults(): number | undefined {
        if (!this.isSuccessful()) return undefined;
        if (this.data && typeof this.data === "object") {
            return (this.data as Record<string, unknown>).maxResults as number | undefined;
        }
        return undefined;
    }
}
