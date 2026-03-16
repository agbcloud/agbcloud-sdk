export class RefreshSessionIdleTimeRequest {
    constructor(
        public authorization: string,
        public sessionId: string
    ) { }

    getBody(): Record<string, unknown> {
        return {};
    }

    getParams(): Record<string, unknown> {
        return {sessionId: this.sessionId};
    }
}
