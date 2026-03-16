export class ListMcpToolsRequest {
    constructor(
        public imageId: string = "",
        public authorization?: string
    ) { }

    getBody(): Record<string, unknown> {
        return {};
    }

    getParams(): Record<string, string> {
        return { imageId: this.imageId };
    }
}
