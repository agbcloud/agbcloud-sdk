export class DeleteSessionAsyncRequest {
    constructor(
        public authorization: string,
        public sessionId: string
    ) { }

    getBody(): Record<string, unknown> {
        return { sessionId: this.sessionId };
    }

    getParams(): Record<string, unknown> {
        return {};
    }
}
