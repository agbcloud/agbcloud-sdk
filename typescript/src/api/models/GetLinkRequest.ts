export class GetLinkRequest {
    constructor(
        public authorization?: string,
        public port?: number,
        public protocolType?: string,
        public sessionId?: string
    ) { }

    getParams(): Record<string, string | number | undefined> {
        const params: Record<string, string | number | undefined> = {};
        if (this.sessionId) params.sessionId = this.sessionId;
        if (this.protocolType) params.protocolType = this.protocolType;
        if (this.port !== undefined) params.port = this.port;
        return params;
    }

    getBody(): Record<string, unknown> {
        return {};
    }
}
