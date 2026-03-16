import { BaseService } from "../../src/api/base-service";
import { CallMcpToolRequest } from "../../src/api/models";

/**
 * Test subclass that exposes protected methods for unit testing.
 */
class TestableBaseService extends BaseService {
    public async testCallMcpTool(
        name: string,
        args: Record<string, unknown>,
        readTimeout?: number,
        connectTimeout?: number,
    ) {
        return this.callMcpTool(name, args, readTimeout, connectTimeout);
    }

    public testHandleError(e: unknown) {
        return this.handleError(e);
    }
}

describe("BaseService", () => {
    const mockClient = {
        callMcpTool: jest.fn(),
    };

    const mockSession = {
        getApiKey: () => "test-key",
        getSessionId: () => "test-session-id",
        getClient: () => mockClient,
    };

    let service: TestableBaseService;

    beforeEach(() => {
        jest.clearAllMocks();
        service = new TestableBaseService(mockSession);
    });

    test("constructor creates BaseService instance", () => {
        expect(service).toBeInstanceOf(BaseService);
    });

    test("callMcpTool API failure should return success false", async () => {
        mockClient.callMcpTool.mockResolvedValue({
            requestId: "req-123",
            isSuccessful: () => false,
            getToolResult: () => null,
            getErrorMessage: () => "Tool execution failed",
        });

        const result = await service.testCallMcpTool("some_tool", { foo: "bar" });

        expect(result.success).toBe(false);
        expect(result.errorMessage).toBe("Tool execution failed");
        expect(result.requestId).toBe("req-123");
    });

    test("callMcpTool null response should fail", async () => {
        mockClient.callMcpTool.mockResolvedValue(null);

        const result = await service.testCallMcpTool("some_tool", {});

        expect(result.success).toBe(false);
        expect(result.errorMessage).toBe("API client returned null response");
        expect(result.requestId).toBe("");
    });

    test("callMcpTool success returns data", async () => {
        const toolData = JSON.stringify({ output: "hello", exitCode: 0 });
        mockClient.callMcpTool.mockResolvedValue({
            requestId: "req-456",
            isSuccessful: () => true,
            getToolResult: () => toolData,
            getErrorMessage: () => null,
        });

        const result = await service.testCallMcpTool("shell", { command: "echo hello" });

        expect(result.success).toBe(true);
        expect(result.data).toBe(toolData);
        expect(result.requestId).toBe("req-456");
    });

    test("callMcpTool handles exception", async () => {
        mockClient.callMcpTool.mockRejectedValue(new Error("Network error"));

        const result = await service.testCallMcpTool("some_tool", {});

        expect(result.success).toBe(false);
        expect(result.errorMessage).toContain("Failed to call MCP tool some_tool");
        expect(result.errorMessage).toContain("Network error");
        expect(result.requestId).toBe("");
    });

    test("callMcpTool with custom timeouts", async () => {
        mockClient.callMcpTool.mockResolvedValue({
            requestId: "req-789",
            isSuccessful: () => true,
            getToolResult: () => "ok",
            getErrorMessage: () => null,
        });

        await service.testCallMcpTool("some_tool", {}, 60000, 10000);

        expect(mockClient.callMcpTool).toHaveBeenCalledWith(
            expect.any(CallMcpToolRequest),
            60000,
            10000,
        );
    });

    test("callMcpTool creates proper request with args JSON", async () => {
        mockClient.callMcpTool.mockResolvedValue({
            requestId: "req-abc",
            isSuccessful: () => true,
            getToolResult: () => "{}",
            getErrorMessage: () => null,
        });

        const args = { command: "ls -la", timeout_ms: 5000 };
        await service.testCallMcpTool("shell", args);

        const callArg = mockClient.callMcpTool.mock.calls[0][0] as CallMcpToolRequest;
        expect(callArg).toBeInstanceOf(CallMcpToolRequest);
        expect(callArg.args).toBe(JSON.stringify(args));
        expect(callArg.authorization).toBe("Bearer test-key");
        expect(callArg.name).toBe("shell");
        expect(callArg.sessionId).toBe("test-session-id");
    });

    test("handleError returns the error as-is", () => {
        const err = new Error("test error");
        const result = service.testHandleError(err);
        expect(result).toBe(err);

        const plainErr = "string error";
        const result2 = service.testHandleError(plainErr);
        expect(result2).toBe(plainErr);
    });

    test("callMcpTool when response has undefined requestId uses empty string", async () => {
        mockClient.callMcpTool.mockResolvedValue({
            requestId: undefined,
            isSuccessful: () => true,
            getToolResult: () => "data",
            getErrorMessage: () => null,
        });

        const result = await service.testCallMcpTool("tool", {});

        expect(result.success).toBe(true);
        expect(result.requestId).toBe("");
    });

    test("callMcpTool when isSuccessful false and getErrorMessage returns null uses default", async () => {
        mockClient.callMcpTool.mockResolvedValue({
            requestId: "req-x",
            isSuccessful: () => false,
            getToolResult: () => null,
            getErrorMessage: () => null,
        });

        const result = await service.testCallMcpTool("tool", {});

        expect(result.success).toBe(false);
        expect(result.errorMessage).toBe("Tool execution failed");
    });
});
