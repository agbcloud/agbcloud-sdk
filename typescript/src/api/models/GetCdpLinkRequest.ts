export class GetCdpLinkRequest {
    constructor(
        public authorization?: string,
        public sessionId?: string,
    ) { }

    getParams(): Record<string, string | undefined> {
        const params: Record<string, string | undefined> = {};
        if (this.sessionId) params.sessionId = this.sessionId;
        return params;
    }

    getBody(): Record<string, unknown> {
        return {};
    }
}
