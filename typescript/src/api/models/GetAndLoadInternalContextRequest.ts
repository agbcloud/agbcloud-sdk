export interface GetAndLoadInternalContextItem {
    contextId?: string;
    contextType?: string;
    contextPath?: string;
}

export class GetAndLoadInternalContextRequest {
    constructor(
        public authorization: string,
        public sessionId: string,
        public contextTypes?: string[]
    ) { }

    getParams(): Record<string, string> {
        const params: Record<string, string> = {};
        if (this.sessionId) params.sessionId = this.sessionId;
        if (this.contextTypes && this.contextTypes.length > 0) {
            params.contextTypes = JSON.stringify(this.contextTypes);
        }
        return params;
    }

    getBody(): Record<string, unknown> {
        return {};
    }
}
