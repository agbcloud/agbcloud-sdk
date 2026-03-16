export class DeleteContextFileRequest {
    constructor(
        public authorization: string = "",
        public contextId: string = "",
        public filePath: string = ""
    ) { }

    getParams(): Record<string, string> {
        return { contextId: this.contextId, filePath: this.filePath };
    }

    getBody(): Record<string, unknown> {
        return {};
    }
}
