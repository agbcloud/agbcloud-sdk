export class GetLabelRequest {
    constructor(
        public authorization: string = "",
        public sessionId?: string,
        public maxResults?: number,
        public nextToken?: string
    ) { }

    getParams(): Record<string, string | number | undefined> {
        const params: Record<string, string | number | undefined> = {};
        if (this.sessionId) params.sessionId = this.sessionId;
        if (this.maxResults !== undefined) params.maxResults = this.maxResults;
        if (this.nextToken) params.nextToken = this.nextToken;
        return params;
    }

    getBody(): Record<string, unknown> {
        return {};
    }
}
