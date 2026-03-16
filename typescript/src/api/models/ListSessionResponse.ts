import type { HttpResponse } from "../http-client";
import type { ListSessionItem } from "./ListSessionRequest";

export class ListSessionResponse {
    readonly requestId: string;
    private readonly success: boolean;
    private readonly statusCode: number;
    private readonly apiSuccess?: boolean;
    private readonly message?: string;
    private readonly data?: unknown;
    private readonly json?: Record<string, unknown>;

    constructor(resp: HttpResponse) {
        this.requestId = resp.requestId ?? "";
        this.success = resp.success;
        this.statusCode = resp.statusCode;
        this.json = resp.json ?? undefined;
        const json = resp.json;
        if (json) {
            this.apiSuccess = json.success as boolean | undefined;
            this.message = json.message as string | undefined;
            this.data = json.data;
        }
    }

    static fromHttpResponse(resp: HttpResponse): ListSessionResponse {
        return new ListSessionResponse(resp);
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

    getSessionData(): ListSessionItem[] {
        if (!this.isSuccessful()) return [];
        if (Array.isArray(this.data)) {
            return this.data.map((item) => {
                const obj = item as Record<string, unknown>;
                return {
                    sessionId: obj.sessionId as string | undefined,
                    sessionStatus: obj.sessionStatus as string | undefined,
                };
            });
        }
        return [];
    }

    getNextToken(): string | undefined {
        return this.json?.nextToken as string | undefined;
    }

    getMaxResults(): number | undefined {
        return this.json?.maxResults as number | undefined;
    }

    getCount(): number | undefined {
        return this.json?.count as number | undefined;
    }
}
