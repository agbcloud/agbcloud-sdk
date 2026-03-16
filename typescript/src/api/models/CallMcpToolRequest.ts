export class CallMcpToolRequest {
    constructor(
        public args?: string | Record<string, unknown>,
        public authorization?: string,
        public imageId?: string,
        public name?: string,
        public server?: string,
        public sessionId?: string
    ) { }

    getBody(): Record<string, unknown> {
        const body: Record<string, unknown> = {};
        if (this.args !== undefined) {
            body.args =
                typeof this.args === "object"
                    ? JSON.stringify(this.args)
                    : String(this.args);
        }
        if (this.sessionId) body.sessionId = this.sessionId;
        if (this.name) body.name = this.name;
        if (this.server) body.server = this.server;
        return body;
    }

    getParams(): Record<string, string> {
        const params: Record<string, string> = {};
        if (this.imageId) params.imageId = this.imageId;
        params.autoGenSession = "false";
        return params;
    }
}
