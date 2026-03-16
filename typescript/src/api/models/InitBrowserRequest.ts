export class InitBrowserRequest {
    constructor(
        public authorization: string,
        public sessionId: string,
        public persistentPath: string,
        public browserOption?: Record<string, unknown>
    ) { }

    getParams(): Record<string, string> {
        const params: Record<string, string> = {
            sessionId: this.sessionId,
            persistentPath: this.persistentPath,
        };
        if (this.browserOption) {
            params.browserOption =
                typeof this.browserOption === "object"
                    ? JSON.stringify(this.browserOption)
                    : String(this.browserOption);
        }
        return params;
    }

    getBody(): Record<string, unknown> {
        return {};
    }
}
