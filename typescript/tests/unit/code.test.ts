import { Code } from "../../src/modules/code";
import { BaseService } from "../../src/api/base-service";
import type { SessionLike } from "../../src/api/base-service";

const mockSession: SessionLike = {
    getApiKey: () => "test-key",
    getSessionId: () => "test-session",
    getClient: () => ({}),
};

describe("Code", () => {
    let code: Code;
    let callMcpToolSpy: jest.SpyInstance;

    beforeEach(() => {
        code = new Code(mockSession);
        callMcpToolSpy = jest.spyOn(
            BaseService.prototype as unknown as { callMcpTool: () => Promise<unknown> },
            "callMcpTool",
        );
    });

    afterEach(() => {
        callMcpToolSpy.mockRestore();
    });

    test("run success with Python", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-py",
            success: true,
            data: JSON.stringify({
                result: [{ "text/plain": "Hello from Python" }],
                stdout: [],
                stderr: [],
                execution_time: 0.1,
            }),
        });

        const result = await code.run("print('Hello from Python')", "python");

        expect(result.success).toBe(true);
        expect(result.results).toHaveLength(1);
        expect(result.results[0].text).toBe("Hello from Python");
        expect(callMcpToolSpy).toHaveBeenCalledWith("run_code", {
            code: "print('Hello from Python')",
            language: "python",
            timeout_s: 60,
        });
    });

    test("run success with JavaScript", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-js",
            success: true,
            data: JSON.stringify({
                result: [{ text: "Hello from JS" }],
                stdout: [],
                stderr: [],
                execution_time: 0.05,
            }),
        });

        const result = await code.run("console.log('Hello from JS')", "javascript");

        expect(result.success).toBe(true);
        expect(result.results[0].text).toBe("Hello from JS");
        expect(callMcpToolSpy).toHaveBeenCalledWith("run_code", {
            code: "console.log('Hello from JS')",
            language: "javascript",
            timeout_s: 60,
        });
    });

    test("run success with Java", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-java",
            success: true,
            data: JSON.stringify({
                result: [{ text: "Hello from Java" }],
                stdout: [],
                stderr: [],
                execution_time: 0.1,
            }),
        });

        const result = await code.run("System.out.println(\"Hello from Java\");", "java");

        expect(result.success).toBe(true);
        expect(result.results[0].text).toBe("Hello from Java");
    });

    test("run success with R", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-r",
            success: true,
            data: JSON.stringify({
                result: [{ text: "Hello from R" }],
                stdout: [],
                stderr: [],
                execution_time: 0.08,
            }),
        });

        const result = await code.run("print('Hello from R')", "r");

        expect(result.success).toBe(true);
        expect(result.results[0].text).toBe("Hello from R");
    });

    test("run case insensitive language", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-1",
            success: true,
            data: JSON.stringify({
                result: [{ text: "ok" }],
                stdout: [],
                stderr: [],
                execution_time: 0,
            }),
        });

        const result = await code.run("print(1)", "PYTHON");

        expect(result.success).toBe(true);
        expect(callMcpToolSpy).toHaveBeenCalledWith("run_code", {
            code: "print(1)",
            language: "python",
            timeout_s: 60,
        });
    });

    test("run unsupported language", async () => {
        const result = await code.run("print(1)", "ruby");

        expect(result.success).toBe(false);
        expect(result.errorMessage).toContain("Unsupported language");
        expect(result.errorMessage).toContain("ruby");
        expect(result.errorMessage).toContain("python, javascript, java, r");
        expect(callMcpToolSpy).not.toHaveBeenCalled();
    });

    test("run API failure", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-fail",
            success: false,
            errorMessage: "Execution timeout",
        });

        const result = await code.run("while True: pass", "python");

        expect(result.success).toBe(false);
        expect(result.errorMessage).toBe("Execution timeout");
        expect(result.results).toEqual([]);
    });

    test("run exception handling", async () => {
        callMcpToolSpy.mockRejectedValue(new Error("Network error"));

        const result = await code.run("print(1)", "python");

        expect(result.success).toBe(false);
        expect(result.errorMessage).toContain("Failed to run code");
        expect(result.errorMessage).toContain("Network error");
    });

    test("run default timeout", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-1",
            success: true,
            data: JSON.stringify({
                result: [{ text: "ok" }],
                stdout: [],
                stderr: [],
                execution_time: 0,
            }),
        });

        await code.run("print(1)", "python");

        expect(callMcpToolSpy).toHaveBeenCalledWith("run_code", {
            code: "print(1)",
            language: "python",
            timeout_s: 60,
        });
    });

    test("run language aliases (py, js, node, python3)", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-1",
            success: true,
            data: JSON.stringify({
                result: [{ text: "ok" }],
                stdout: [],
                stderr: [],
                execution_time: 0,
            }),
        });

        await code.run("print(1)", "py");
        expect(callMcpToolSpy).toHaveBeenLastCalledWith("run_code", {
            code: "print(1)",
            language: "python",
            timeout_s: 60,
        });

        await code.run("console.log(1)", "js");
        expect(callMcpToolSpy).toHaveBeenLastCalledWith("run_code", {
            code: "console.log(1)",
            language: "javascript",
            timeout_s: 60,
        });

        await code.run("console.log(1)", "node");
        expect(callMcpToolSpy).toHaveBeenLastCalledWith("run_code", {
            code: "console.log(1)",
            language: "javascript",
            timeout_s: 60,
        });

        await code.run("print(1)", "python3");
        expect(callMcpToolSpy).toHaveBeenLastCalledWith("run_code", {
            code: "print(1)",
            language: "python",
            timeout_s: 60,
        });
    });

    test("run success - new format with result array", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-new",
            success: true,
            data: JSON.stringify({
                result: [
                    { "text/plain": "output 1" },
                    { "text/plain": "output 2" },
                ],
                stdout: ["stdout line"],
                stderr: [],
                execution_time: 0.5,
                execution_count: 2,
            }),
        });

        const result = await code.run("print(1)", "python");

        expect(result.success).toBe(true);
        expect(result.results).toHaveLength(2);
        expect(result.results[0].text).toBe("output 1");
        expect(result.results[1].text).toBe("output 2");
        expect(result.logs.stdout).toEqual(["stdout line"]);
        expect(result.executionTime).toBe(0.5);
        expect(result.executionCount).toBe(2);
    });

    test("run success - rich format with logs/results", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-rich",
            success: true,
            data: JSON.stringify({
                logs: {
                    stdout: ["log line 1"],
                    stderr: [],
                },
                results: [{ text: "result text", is_main_result: true }],
                execution_time: 0.2,
                execution_count: 1,
                isError: false,
            }),
        });

        const result = await code.run("print(1)", "python");

        expect(result.success).toBe(true);
        expect(result.results).toHaveLength(1);
        expect(result.results[0].text).toBe("result text");
        expect(result.results[0].isMainResult).toBe(true);
        expect(result.logs.stdout).toEqual(["log line 1"]);
    });

    test("run success - legacy format with content", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-legacy",
            success: true,
            data: JSON.stringify({
                content: [{ text: "legacy output" }],
            }),
        });

        const result = await code.run("print(1)", "python");

        expect(result.success).toBe(true);
        expect(result.results).toHaveLength(1);
        expect(result.results[0].text).toBe("legacy output");
        expect(result.logs.stdout).toEqual(["legacy output"]);
    });

    test("run with no data returned", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-1",
            success: true,
            data: null,
        });

        const result = await code.run("print(1)", "python");

        expect(result.success).toBe(false);
        expect(result.errorMessage).toBe("No data returned");
    });

    test("run with non-object response (fallback)", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-1",
            success: true,
            data: "plain string output",
        });

        const result = await code.run("print(1)", "python");

        expect(result.success).toBe(true);
        expect(result.results).toHaveLength(1);
        expect(result.results[0].text).toBe("plain string output");
        expect(result.results[0].isMainResult).toBe(true);
    });

    test("execute alias works", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-exec",
            success: true,
            data: JSON.stringify({
                result: [{ text: "execute alias" }],
                stdout: [],
                stderr: [],
                execution_time: 0,
            }),
        });

        const result = await code.execute("print(1)", "python");

        expect(result.success).toBe(true);
        expect(result.results[0].text).toBe("execute alias");
        expect(callMcpToolSpy).toHaveBeenCalledWith("run_code", {
            code: "print(1)",
            language: "python",
            timeout_s: 60,
        });
    });

    test("run custom timeout", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-1",
            success: true,
            data: JSON.stringify({
                result: [{ text: "ok" }],
                stdout: [],
                stderr: [],
                execution_time: 0,
            }),
        });

        await code.run("print(1)", "python", 120);

        expect(callMcpToolSpy).toHaveBeenCalledWith("run_code", {
            code: "print(1)",
            language: "python",
            timeout_s: 120,
        });
    });

    test("run new format with executionError", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-err",
            success: true,
            data: JSON.stringify({
                result: [],
                stdout: [],
                stderr: ["error line"],
                execution_time: 0,
                executionError: "SyntaxError: invalid syntax",
            }),
        });

        const result = await code.run("print(", "python");

        expect(result.success).toBe(false);
        expect(result.errorMessage).toBe("SyntaxError: invalid syntax");
    });

    test("run rich format with isError", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-err",
            success: true,
            data: JSON.stringify({
                logs: { stdout: [], stderr: ["error"] },
                results: [],
                execution_time: 0,
                isError: true,
                error: { value: "Runtime error" },
            }),
        });

        const result = await code.run("1/0", "python");

        expect(result.success).toBe(false);
        expect(result.errorMessage).toBe("Runtime error");
    });
});
