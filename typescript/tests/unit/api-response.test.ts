import {
    extractRequestId,
    type SessionResult,
    type DeleteResult,
    type OperationResult,
    type BoolResult,
    type CommandResult,
    type EnhancedCodeExecutionResult,
    type FileContentResult,
    type WindowInfo,
} from "../../src/types/api-response";

describe("extractRequestId", () => {
    test("extractRequestId with requestId present", () => {
        const response = { requestId: "req-123", success: true };
        expect(extractRequestId(response)).toBe("req-123");
    });

    test("extractRequestId with missing requestId returns undefined", () => {
        const response = { success: true };
        expect(extractRequestId(response)).toBeUndefined();
    });

    test("extractRequestId with empty object", () => {
        expect(extractRequestId({})).toBeUndefined();
    });

    test("extractRequestId with null requestId returns undefined", () => {
        const response = { requestId: null, success: true };
        expect(extractRequestId(response)).toBeUndefined();
    });

    test("extractRequestId with undefined requestId returns undefined", () => {
        const response = { requestId: undefined, success: true };
        expect(extractRequestId(response)).toBeUndefined();
    });

    test("extractRequestId with empty string requestId returns empty string", () => {
        const response = { requestId: "", success: true };
        expect(extractRequestId(response)).toBe("");
    });
});

describe("API response interface shapes", () => {
    test("SessionResult shape", () => {
        const result: SessionResult = {
            requestId: "req-1",
            success: true,
        };
        expect(result.success).toBe(true);
        expect(result.requestId).toBe("req-1");

        const failure: SessionResult = {
            requestId: "req-2",
            success: false,
            errorMessage: "Session not found",
        };
        expect(failure.success).toBe(false);
        expect(failure.errorMessage).toBe("Session not found");
    });

    test("DeleteResult shape", () => {
        const result: DeleteResult = {
            requestId: "req-del",
            success: true,
        };
        expect(result.success).toBe(true);

        const failure: DeleteResult = {
            success: false,
            errorMessage: "Delete failed",
        };
        expect(failure.success).toBe(false);
        expect(failure.errorMessage).toBe("Delete failed");
    });

    test("OperationResult shape", () => {
        const success: OperationResult = {
            requestId: "req-op",
            success: true,
            data: { output: "hello" },
        };
        expect(success.success).toBe(true);
        expect(success.data).toEqual({ output: "hello" });

        const failure: OperationResult = {
            success: false,
            errorMessage: "Operation failed",
        };
        expect(failure.success).toBe(false);
        expect(failure.errorMessage).toBe("Operation failed");
    });

    test("BoolResult shape", () => {
        const result: BoolResult = {
            requestId: "req-bool",
            success: true,
            data: true,
        };
        expect(result.success).toBe(true);
        expect(result.data).toBe(true);
    });

    test("CommandResult shape", () => {
        const result: CommandResult = {
            requestId: "req-cmd",
            success: true,
            output: "hello world",
            exitCode: 0,
            stdout: "hello world",
            stderr: "",
            traceId: "trace-123",
        };
        expect(result.success).toBe(true);
        expect(result.output).toBe("hello world");
        expect(result.exitCode).toBe(0);
        expect(result.stdout).toBe("hello world");
        expect(result.stderr).toBe("");
        expect(result.traceId).toBe("trace-123");
    });

    test("EnhancedCodeExecutionResult shape", () => {
        const result: EnhancedCodeExecutionResult = {
            requestId: "req-code",
            success: true,
            executionCount: 1,
            executionTime: 100,
            logs: { stdout: ["out"], stderr: [] },
            results: [
                {
                    text: "result",
                    isMainResult: true,
                },
            ],
            errorMessage: "",
        };
        expect(result.success).toBe(true);
        expect(result.executionTime).toBe(100);
        expect(result.logs.stdout).toEqual(["out"]);
        expect(result.results).toHaveLength(1);
        expect(result.results[0].text).toBe("result");
        expect(result.results[0].isMainResult).toBe(true);
    });

    test("FileContentResult shape", () => {
        const result: FileContentResult = {
            requestId: "req-file",
            success: true,
            content: "file contents here",
        };
        expect(result.success).toBe(true);
        expect(result.content).toBe("file contents here");

        const failure: FileContentResult = {
            success: false,
            content: "",
            errorMessage: "File not found",
        };
        expect(failure.success).toBe(false);
        expect(failure.errorMessage).toBe("File not found");
    });

    test("WindowInfo shape", () => {
        const window: WindowInfo = {
            id: "win-1",
            title: "Test Window",
            x: 100,
            y: 200,
            width: 800,
            height: 600,
        };
        expect(window.id).toBe("win-1");
        expect(window.title).toBe("Test Window");
        expect(window.x).toBe(100);
        expect(window.y).toBe(200);
        expect(window.width).toBe(800);
        expect(window.height).toBe(600);

        const minimal: WindowInfo = {};
        expect(minimal).toEqual({});
    });
});
