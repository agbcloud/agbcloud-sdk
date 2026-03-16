export class GetSessionDetailRequest {
    constructor(
        public authorization: string = "",
        public sessionId?: string
    ) { }

    getBody(): Record<string, unknown> {
        const body: Record<string, unknown> = {};
        if (this.sessionId) {
            body.sessionId = this.sessionId;
        }
        return body;
    }

    getParams(): Record<string, unknown> {
        return {};
    }
}
