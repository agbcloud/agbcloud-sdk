import { CreateMcpSessionRequestPersistenceDataList } from "./CreateMcpSessionRequestPersistenceDataList";

export interface SessionData {
    appInstanceId?: string;
    resourceId?: string;
    resourceUrl?: string;
    success?: boolean;
    errMsg?: string;
    sessionId?: string;
    taskId?: string;
    networkInterfaceIp?: string;
    linkUrl?: string;
    wsUrl?: string;
    token?: string;
    toolList?: string;
}

export class CreateSessionRequest {
    constructor(
        public authorization: string = "",
        public contextId?: string,
        public imageId: string = "",
        public labels?: string,
        public persistenceDataList?: CreateMcpSessionRequestPersistenceDataList[],
        public sessionId?: string,
        public sdkStats?: Record<string, unknown>,
        public mcpPolicyId?: string,
        public timeout?: number,
    ) { }

    getBody(): Record<string, unknown> {
        const body: Record<string, unknown> = {};
        if (this.sessionId) body.sessionId = this.sessionId;
        if (this.persistenceDataList) {
            body.persistenceDataList = this.persistenceDataList.map((d) =>
                d ? d.toMap() : null
            );
        }
        if (this.contextId) body.contextId = this.contextId;
        if (this.labels) body.labels = this.labels;
        if (this.mcpPolicyId) body.mcpPolicyId = this.mcpPolicyId;
        if (this.timeout !== undefined) body.timeout = this.timeout;
        return body;
    }

    getParams(): Record<string, string> {
        const params: Record<string, string> = {};
        if (this.imageId) params.imageId = this.imageId;
        if (this.sdkStats) {
            params.sdkStats = JSON.stringify(this.sdkStats);
        }
        return params;
    }
}
