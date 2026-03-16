export interface DescribeContextFilesItem {
    fileId?: string;
    fileName?: string;
    filePath?: string;
    fileType?: string;
    gmtCreate?: string;
    gmtModified?: string;
    size?: number;
    status?: string;
}

export class DescribeContextFilesRequest {
    constructor(
        public authorization: string = "",
        public contextId: string = "",
        public parentFolderPath: string = "",
        public pageNumber: number = 1,
        public pageSize: number = 50
    ) { }

    getParams(): Record<string, string> {
        return {
            contextId: this.contextId,
            parentFolderPath: this.parentFolderPath,
            pageNumber: String(this.pageNumber),
            pageSize: String(this.pageSize),
        };
    }

    getBody(): Record<string, unknown> {
        return {};
    }
}
