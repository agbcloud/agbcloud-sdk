export interface ListSessionItem {
    sessionId?: string;
    sessionStatus?: string;
}

export class ListSessionRequest {
    constructor(
        public authorization: string = "",
        public maxResults?: number,
        public nextToken?: string,
        public labels?: string,
        public isAll?: boolean
    ) { }

    getParams(): Record<string, string> {
        const params: Record<string, string> = {};
        if (this.maxResults !== undefined) params.maxResults = String(this.maxResults);
        if (this.nextToken) params.nextToken = this.nextToken;
        if (this.labels) params.labels = this.labels;
        if (this.isAll !== undefined) params.isAll = String(this.isAll);
        return params;
    }

    getBody(): Record<string, unknown> {
        return {};
    }
}
