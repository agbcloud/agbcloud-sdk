import type { HttpResponse } from "../http-client";
import type { ListContextsItem } from "./ListContextsRequest";

export class ListContextsResponse {
    private readonly success: boolean;
    private readonly statusCode: number;
    private readonly apiSuccess?: boolean;
    private readonly message?: string;
    private readonly data?: unknown;
    private readonly requestId: string;

    constructor(resp: HttpResponse) {
        this.success = resp.success;
        this.statusCode = resp.statusCode;
        this.requestId = resp.requestId ?? "";
        const json = resp.json;
        if (json) {
            this.apiSuccess = json.success as boolean | undefined;
            this.message = json.message as string | undefined;
            this.data = json.data;
        }
    }

    static fromHttpResponse(resp: HttpResponse): ListContextsResponse {
        return new ListContextsResponse(resp);
    }

    isSuccessful(): boolean {
        return this.statusCode === 200 && this.apiSuccess === true;
    }

    getErrorMessage(): string {
        if (!this.isSuccessful()) {
            return this.message ?? `HTTP ${this.statusCode} error`;
        }
        return "";
    }

    getContextsData(): ListContextsItem[] {
        if (!this.isSuccessful()) return [];
        if (Array.isArray(this.data)) {
            return this.data.map((item) => {
                const obj = item as Record<string, unknown>;
                return {
                    createTime: obj.createTime as string | undefined,
                    id: obj.id as string | undefined,
                    lastUsedTime: obj.lastUsedTime as string | undefined,
                    name: obj.name as string | undefined,
                };
            });
        }
        return [];
    }

    getNextToken(): string | undefined {
        if (!this.isSuccessful()) return undefined;
        return (this.data as Record<string, unknown>)?.nextToken as string | undefined;
    }

    getMaxResults(): number | undefined {
        if (!this.isSuccessful()) return undefined;
        return (this.data as Record<string, unknown>)?.maxResults as number | undefined;
    }

    getTotalCount(): number | undefined {
        if (!this.isSuccessful()) return undefined;
        if (this.data && typeof this.data === "object" && !Array.isArray(this.data)) {
            return (this.data as Record<string, unknown>).totalCount as number | undefined;
        }
        return undefined;
    }

    getRequestId(): string {
        return this.requestId;
    }
}
