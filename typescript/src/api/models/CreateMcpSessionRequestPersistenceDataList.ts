export interface CreateMcpSessionRequestPersistenceDataListMap {
    contextId: string;
    path: string;
    policy: string;
}

export class CreateMcpSessionRequestPersistenceDataList {
    constructor(
        public contextId?: string,
        public path?: string,
        public policy?: string
    ) { }

    toMap(): CreateMcpSessionRequestPersistenceDataListMap {
        return {
            contextId: this.contextId ?? "",
            path: this.path ?? "",
            policy: this.policy ?? "",
        };
    }
}
