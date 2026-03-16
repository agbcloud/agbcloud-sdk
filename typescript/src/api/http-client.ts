import axios, { AxiosInstance, AxiosRequestConfig } from "axios";
import type { Config } from "../config";
import { logApiCall, logApiResponse, maskSensitiveData, logDebug } from "../logger";

export interface HttpResponse {
    statusCode: number;
    url: string;
    headers: Record<string, string>;
    success: boolean;
    json?: Record<string, unknown> | null;
    text?: string;
    requestId: string;
}

export class HTTPClient {
    private static _defaultConfig: Config | null = null;

    private baseUrl: string;
    private timeoutMs: number;
    private apiKey: string;
    private client: AxiosInstance;

    static setDefaultConfig(config: Config): void {
        HTTPClient._defaultConfig = config;
    }

    static getDefaultConfig(): Config | null {
        return HTTPClient._defaultConfig;
    }

    constructor(apiKey: string = "", cfg?: Config) {
        const config = cfg ?? HTTPClient._defaultConfig;
        if (!config) {
            throw new Error("No configuration provided and no default config set");
        }

        this.apiKey = apiKey;
        this.timeoutMs = config.timeoutMs;

        let endpoint = config.endpoint;
        if (endpoint && !endpoint.startsWith("http://") && !endpoint.startsWith("https://")) {
            this.baseUrl = `https://${endpoint}`;
        } else {
            this.baseUrl = endpoint;
        }

        if (!this.baseUrl) {
            throw new Error("baseUrl cannot be empty");
        }

        this.client = axios.create({
            baseURL: this.baseUrl,
            timeout: this.timeoutMs,
            headers: {
                "Content-Type": "application/json",
                authorization: this.apiKey,
            },
        });
    }

    async makeRequest(options: {
        method: string;
        endpoint: string;
        headers?: Record<string, string>;
        params?: Record<string, unknown>;
        jsonData?: Record<string, unknown>;
        data?: unknown;
        readTimeout?: number;
        connectTimeout?: number;
    }): Promise<HttpResponse> {
        const {
            method,
            endpoint,
            headers,
            params,
            jsonData,
            data,
            readTimeout,
        } = options;

        const url = endpoint;
        const apiName = endpoint.split("/").pop() || endpoint;

        const requestDataParts: string[] = [];
        if (params) {
            requestDataParts.push(`Params: ${JSON.stringify(maskSensitiveData(params))}`);
        }
        if (jsonData) {
            requestDataParts.push(`Body: ${JSON.stringify(maskSensitiveData(jsonData))}`);
        }
        logApiCall(apiName, requestDataParts.join(" | "));

        const axiosConfig: AxiosRequestConfig = {
            method: method.toUpperCase() as AxiosRequestConfig["method"],
            url,
            headers: { ...headers },
            params,
            timeout: readTimeout ?? this.timeoutMs,
            validateStatus: () => true,
        };

        if (jsonData !== undefined) {
            axiosConfig.data = jsonData;
        } else if (data !== undefined) {
            axiosConfig.data = data;
        }

        try {
            const response = await this.client.request(axiosConfig);

            const result: HttpResponse = {
                statusCode: response.status,
                url: `${this.baseUrl}${endpoint}`,
                headers: response.headers as Record<string, string>,
                success: response.status < 400,
                json: null,
                requestId: "",
            };

            if (typeof response.data === "object" && response.data !== null) {
                result.json = response.data as Record<string, unknown>;
                if (result.json && typeof result.json.requestId === "string") {
                    result.requestId = result.json.requestId;
                }
            } else if (typeof response.data === "string") {
                try {
                    result.json = JSON.parse(response.data);
                    if (result.json && typeof result.json.requestId === "string") {
                        result.requestId = result.json.requestId;
                    }
                } catch {
                    result.text = response.data;
                }
            }

            if (!result.requestId) {
                result.requestId =
                    (response.headers["x-request-id"] as string) || "";
            }

            let responseExtra: string | undefined;
            if (apiName === "getCdpLink" && result.json) {
                const data = result.json.data as Record<string, unknown> | undefined;
                const hasUrl = !!(data && typeof data.url === "string");
                responseExtra = `success=${result.json.success}, hasUrl=${hasUrl}`;
            }
            logApiResponse(apiName, result.requestId, result.success, responseExtra);
            logDebug(`Response [${apiName}]: ${JSON.stringify(result.json ?? result.text)}`);

            return result;
        } catch (error: unknown) {
            const errMsg = error instanceof Error ? error.message : String(error);
            logApiResponse(apiName, "", false);
            return {
                statusCode: 0,
                url: `${this.baseUrl}${endpoint}`,
                headers: {},
                success: false,
                json: null,
                text: errMsg,
                requestId: "",
            };
        }
    }

    close(): void {
        // Axios doesn't need explicit cleanup
    }
}
