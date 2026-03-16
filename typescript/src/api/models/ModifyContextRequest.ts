export class ModifyContextRequest {
    constructor(
        public authorization: string = "",
        public id: string = "",
        public name: string = ""
    ) { }

    getParams(): Record<string, string> {
        return { id: this.id, name: this.name };
    }

    getBody(): Record<string, unknown> {
        return {};
    }
}
