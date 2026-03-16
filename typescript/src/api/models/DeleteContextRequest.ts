export class DeleteContextRequest {
    constructor(
        public authorization: string = "",
        public id: string = ""
    ) { }

    getParams(): Record<string, string> {
        return { id: this.id };
    }

    getBody(): Record<string, unknown> {
        return {};
    }
}
