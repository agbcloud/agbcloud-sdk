import type { HttpResponse } from "../http-client";

export class ListMcpToolsResponse {
    readonly requestId: string;
    private readonly success: boolean;
    private readonly statusCode: number;
    private readonly apiSuccess?: boolean;
    private readonly code?: string;
    private readonly httpStatusCode?: number;
    private readonly message?: string;
    private readonly data?: unknown;
    private readonly error?: string;

    constructor(resp: HttpResponse) {
        this.requestId = resp.requestId ?? "";
        this.success = resp.success;
        this.statusCode = resp.statusCode;
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

    static fromHttpResponse(resp: HttpResponse): ListMcpToolsResponse {
        return new ListMcpToolsResponse(resp);
    }

    isSuccessful(): boolean {
        return this.success === true && this.statusCode === 200 && this.apiSuccess === true;
    }

    getErrorMessage(): string | undefined {
        if (this.error) return this.error;
        if (!this.apiSuccess) return this.message ?? "API request failed";
        if (
            this.data &&
            typeof this.data === "object" &&
            (this.data as Record<string, unknown>).isError
        ) {
            return (
                (this.data as Record<string, unknown>).errMsg as string ?? "Tool execution failed"
            );
        }
        return undefined;
    }

    getToolsList(): string | undefined {
        if (this.data && typeof this.data === "string") return this.data;
        return undefined;
    }
}
