import type { HttpResponse } from "../http-client";

export class CallMcpToolResponse {
    readonly requestId: string;
    private readonly success: boolean;
    private readonly statusCode: number;
    private readonly apiSuccess?: boolean;
    private readonly toolSuccess: boolean;
    private readonly result?: string;
    private readonly message?: string;
    private readonly error?: string;

    constructor(resp: HttpResponse) {
        this.requestId = resp.requestId ?? "";
        this.success = resp.success;
        this.statusCode = resp.statusCode;
        this.error = resp.text;
        const json = resp.json;
        if (json) {
            this.apiSuccess = json.success as boolean | undefined;
            this.message = json.message as string | undefined;
            const data = json.data as Record<string, unknown> | undefined;
            this.toolSuccess =
                data !== undefined ? !(data.isError as boolean) : true;
            const content = data?.content as Array<Record<string, unknown>> | undefined;
            if (content && Array.isArray(content) && content.length > 0) {
                const textParts = content
                    .filter((item) => item.type === "text")
                    .map((item) => (item.text as string) ?? "");
                if (textParts.length > 0) {
                    this.result = textParts.join("\n");
                } else {
                    const c0 = content[0];
                    if (typeof c0.text === "string" && c0.text) {
                        this.result = c0.text;
                    } else if (typeof c0.blob === "string" && c0.blob) {
                        this.result = c0.blob;
                    } else if (typeof c0.data === "string" && c0.data) {
                        this.result = c0.data;
                    }
                }
            }
        } else {
            this.toolSuccess = false;
        }
    }

    static fromHttpResponse(resp: HttpResponse): CallMcpToolResponse {
        return new CallMcpToolResponse(resp);
    }

    isSuccessful(): boolean {
        return (
            this.success === true &&
            this.statusCode === 200 &&
            this.apiSuccess === true &&
            this.toolSuccess === true
        );
    }

    getErrorMessage(): string | undefined {
        if (this.error) return this.error;
        if (this.message) return this.message;
        if (!this.toolSuccess && this.result) return this.result;
        return undefined;
    }

    getToolResult(): string | undefined {
        return this.result;
    }
}
