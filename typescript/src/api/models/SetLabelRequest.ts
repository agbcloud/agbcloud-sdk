export class SetLabelRequest {
    constructor(
        public authorization: string = "",
        public sessionId?: string,
        public labels?: string
    ) { }

    getParams(): Record<string, string> {
        const params: Record<string, string> = {};
        if (this.sessionId) params.sessionId = this.sessionId;
        if (this.labels) params.Labels = this.labels;
        return params;
    }

    getBody(): Record<string, unknown> {
        return {};
    }
}
