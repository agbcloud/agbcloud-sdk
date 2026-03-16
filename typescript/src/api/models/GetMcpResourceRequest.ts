export interface McpResourceData {
    desktopInfo?: unknown;
    resourceUrl?: string;
    sessionId?: string;
}

export class GetMcpResourceRequest {
    constructor(
        public sessionId: string = "",
        public authorization?: string
    ) { }

    getBody(): Record<string, unknown> {
        return { sessionId: this.sessionId };
    }

    getParams(): Record<string, unknown> {
        return {};
    }
}
