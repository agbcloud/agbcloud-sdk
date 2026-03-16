export class SyncContextRequest {
    constructor(
        public authorization: string,
        public sessionId: string,
        public contextId?: string,
        public path?: string,
        public mode?: string
    ) { }

    getParams(): Record<string, string | undefined> {
        const params: Record<string, string | undefined> = {};
        if (this.sessionId) params.sessionId = this.sessionId;
        if (this.contextId) params.contextId = this.contextId;
        if (this.path) params.path = this.path;
        if (this.mode) params.mode = this.mode;
        return params;
    }

    getBody(): Record<string, unknown> {
        return {};
    }
}
