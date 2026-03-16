export class ReleaseSessionRequest {
    constructor(
        public sessionId: string,
        public authorization: string
    ) { }

    getBody(): Record<string, unknown> {
        return { sessionId: this.sessionId };
    }

    getParams(): Record<string, unknown> {
        return {};
    }
}
