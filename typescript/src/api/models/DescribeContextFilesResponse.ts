import type { HttpResponse } from "../http-client";
import type { DescribeContextFilesItem } from "./DescribeContextFilesRequest";

export class DescribeContextFilesResponse {
    private readonly success: boolean;
    private readonly statusCode: number;
    private readonly apiSuccess?: boolean;
    private readonly message?: string;
    private readonly data?: unknown;
    private readonly json?: Record<string, unknown>;
    private readonly requestId: string;

    constructor(resp: HttpResponse) {
        this.success = resp.success;
        this.statusCode = resp.statusCode;
        this.requestId = resp.requestId ?? "";
        this.json = resp.json ?? undefined;
        const json = resp.json;
        if (json) {
            this.apiSuccess = json.success as boolean | undefined;
            this.message = json.message as string | undefined;
            this.data = json.data;
        }
    }

    static fromHttpResponse(resp: HttpResponse): DescribeContextFilesResponse {
        return new DescribeContextFilesResponse(resp);
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

    getFilesData(): DescribeContextFilesItem[] {
        if (!this.isSuccessful()) return [];
        if (Array.isArray(this.data)) {
            return this.data.map((item) => {
                const obj = item as Record<string, unknown>;
                return {
                    fileId: obj.fileId as string | undefined,
                    fileName: obj.fileName as string | undefined,
                    filePath: obj.filePath as string | undefined,
                    fileType: obj.fileType as string | undefined,
                    gmtCreate: obj.gmtCreate as string | undefined,
                    gmtModified: obj.gmtModified as string | undefined,
                    size: obj.size as number | undefined,
                    status: obj.status as string | undefined,
                };
            });
        }
        return [];
    }

    getNextToken(): string | undefined {
        return this.json?.nextToken as string | undefined;
    }

    getCount(): number | undefined {
        if (!this.isSuccessful()) return undefined;
        if (this.data && typeof this.data === "object") {
            return (this.data as Record<string, unknown>).count as number | undefined;
        }
        return this.json?.count as number | undefined;
    }

    getMaxResults(): number | undefined {
        return this.json?.maxResults as number | undefined;
    }

    getRequestId(): string {
        return this.requestId;
    }
}
