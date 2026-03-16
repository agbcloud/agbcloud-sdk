export class GetContextRequest {
    constructor(
        public authorization: string = "",
        public id?: string,
        public name?: string,
        public allowCreate: boolean = false,
        public loginRegionId?: string
    ) { }

    getParams(): Record<string, string> {
        const params: Record<string, string> = {};
        if (this.id) params.id = this.id;
        if (this.name) params.name = this.name;
        if (this.loginRegionId) params.loginRegionId = this.loginRegionId;
        params.allowCreate = String(this.allowCreate);
        return params;
    }

    getBody(): Record<string, unknown> {
        return {};
    }
}
