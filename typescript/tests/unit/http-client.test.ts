import axios from "axios";
import { HTTPClient } from "../../src/api/http-client";
import type { Config } from "../../src/config";

jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;

const defaultTestConfig: Config = {
    endpoint: "https://api.test.com",
    timeoutMs: 10000,
};

describe("HTTPClient", () => {
    let mockRequest: jest.Mock;

    beforeEach(() => {
        jest.clearAllMocks();
        (HTTPClient as { setDefaultConfig(c: Config | null): void }).setDefaultConfig(null);
        mockRequest = jest.fn();
        mockedAxios.create.mockReturnValue({
            request: mockRequest,
        } as unknown as ReturnType<typeof axios.create>);
    });

    afterEach(() => {
        (HTTPClient as { setDefaultConfig(c: Config | null): void }).setDefaultConfig(null);
    });

    describe("static config", () => {
        test("setDefaultConfig and getDefaultConfig", () => {
            expect(HTTPClient.getDefaultConfig()).toBeNull();
            HTTPClient.setDefaultConfig(defaultTestConfig);
            expect(HTTPClient.getDefaultConfig()).toEqual(defaultTestConfig);
            (HTTPClient as { setDefaultConfig(c: Config | null): void }).setDefaultConfig(null);
            expect(HTTPClient.getDefaultConfig()).toBeNull();
        });
    });

    describe("constructor", () => {
        test("uses provided config", () => {
            new HTTPClient("key", defaultTestConfig);
            expect(mockedAxios.create).toHaveBeenCalledWith(
                expect.objectContaining({
                    baseURL: "https://api.test.com",
                    timeout: 10000,
                    headers: {
                        "Content-Type": "application/json",
                        authorization: "key",
                    },
                }),
            );
        });

        test("uses default config when no config provided", () => {
            HTTPClient.setDefaultConfig(defaultTestConfig);
            new HTTPClient("key");
            expect(mockedAxios.create).toHaveBeenCalledWith(
                expect.objectContaining({
                    baseURL: "https://api.test.com",
                    timeout: 10000,
                }),
            );
        });

        test("throws when no config and no default", () => {
            expect(() => new HTTPClient("key")).toThrow(
                "No configuration provided and no default config set",
            );
            expect(mockedAxios.create).not.toHaveBeenCalled();
        });

        test("adds https:// to endpoint when missing", () => {
            new HTTPClient("key", {
                endpoint: "api.plain.com",
                timeoutMs: 5000,
            });
            expect(mockedAxios.create).toHaveBeenCalledWith(
                expect.objectContaining({
                    baseURL: "https://api.plain.com",
                }),
            );
        });

        test("keeps http:// endpoint as-is", () => {
            new HTTPClient("key", {
                endpoint: "http://local.test",
                timeoutMs: 5000,
            });
            expect(mockedAxios.create).toHaveBeenCalledWith(
                expect.objectContaining({
                    baseURL: "http://local.test",
                }),
            );
        });

        test("throws when baseUrl would be empty", () => {
            expect(
                () =>
                    new HTTPClient("key", {
                        endpoint: "",
                        timeoutMs: 5000,
                    } as Config),
            ).toThrow("baseUrl cannot be empty");
        });
    });

    describe("makeRequest", () => {
        test("success with json object and requestId in body", async () => {
            const client = new HTTPClient("key", defaultTestConfig);
            mockRequest.mockResolvedValue({
                status: 200,
                data: { success: true, requestId: "req-123", data: {} },
                headers: {},
            });

            const result = await client.makeRequest({
                method: "POST",
                endpoint: "/foo/bar",
            });

            expect(result.success).toBe(true);
            expect(result.statusCode).toBe(200);
            expect(result.requestId).toBe("req-123");
            expect(result.json).toEqual({
                success: true,
                requestId: "req-123",
                data: {},
            });
            expect(result.url).toBe("https://api.test.com/foo/bar");
        });

        test("success with string body parsed as JSON", async () => {
            const client = new HTTPClient("key", defaultTestConfig);
            mockRequest.mockResolvedValue({
                status: 200,
                data: '{"success":true,"requestId":"str-req"}',
                headers: {},
            });

            const result = await client.makeRequest({
                method: "GET",
                endpoint: "/get",
            });

            expect(result.success).toBe(true);
            expect(result.json).toEqual({
                success: true,
                requestId: "str-req",
            });
            expect(result.requestId).toBe("str-req");
        });

        test("success with non-JSON string sets text", async () => {
            const client = new HTTPClient("key", defaultTestConfig);
            mockRequest.mockResolvedValue({
                status: 200,
                data: "plain text",
                headers: {},
            });

            const result = await client.makeRequest({
                method: "GET",
                endpoint: "/text",
            });

            expect(result.success).toBe(true);
            expect(result.json).toBeNull();
            expect(result.text).toBe("plain text");
        });

        test("requestId from header when not in body", async () => {
            const client = new HTTPClient("key", defaultTestConfig);
            mockRequest.mockResolvedValue({
                status: 200,
                data: { success: true },
                headers: { "x-request-id": "header-req-id" },
            });

            const result = await client.makeRequest({
                method: "POST",
                endpoint: "/post",
            });

            expect(result.requestId).toBe("header-req-id");
        });

        test("4xx response sets success false", async () => {
            const client = new HTTPClient("key", defaultTestConfig);
            mockRequest.mockResolvedValue({
                status: 404,
                data: { message: "Not Found" },
                headers: {},
            });

            const result = await client.makeRequest({
                method: "GET",
                endpoint: "/missing",
            });

            expect(result.success).toBe(false);
            expect(result.statusCode).toBe(404);
        });

        test("passes params and jsonData to axios", async () => {
            const client = new HTTPClient("key", defaultTestConfig);
            mockRequest.mockResolvedValue({ status: 200, data: {}, headers: {} });

            await client.makeRequest({
                method: "POST",
                endpoint: "/action",
                params: { a: 1 },
                jsonData: { b: 2 },
            });

            expect(mockRequest).toHaveBeenCalledWith(
                expect.objectContaining({
                    method: "POST",
                    url: "/action",
                    params: { a: 1 },
                    data: { b: 2 },
                }),
            );
        });

        test("uses readTimeout when provided", async () => {
            const client = new HTTPClient("key", defaultTestConfig);
            mockRequest.mockResolvedValue({ status: 200, data: {}, headers: {} });

            await client.makeRequest({
                method: "GET",
                endpoint: "/slow",
                readTimeout: 30000,
            });

            expect(mockRequest).toHaveBeenCalledWith(
                expect.objectContaining({
                    timeout: 30000,
                }),
            );
        });

        test("network error returns statusCode 0 and text", async () => {
            const client = new HTTPClient("key", defaultTestConfig);
            mockRequest.mockRejectedValue(new Error("Network failure"));

            const result = await client.makeRequest({
                method: "GET",
                endpoint: "/fail",
            });

            expect(result.success).toBe(false);
            expect(result.statusCode).toBe(0);
            expect(result.url).toBe("https://api.test.com/fail");
            expect(result.text).toBe("Network failure");
            expect(result.requestId).toBe("");
        });

        test("close does not throw", () => {
            const client = new HTTPClient("key", defaultTestConfig);
            expect(() => client.close()).not.toThrow();
        });
    });
});
