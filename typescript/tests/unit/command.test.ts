import { Command } from "../../src/modules/command";
import { BaseService } from "../../src/api/base-service";
import type { SessionLike } from "../../src/api/base-service";

const mockSession: SessionLike = {
    getApiKey: () => "test-key",
    getSessionId: () => "test-session",
    getClient: () => ({}),
};

describe("Command", () => {
    let command: Command;
    let callMcpToolSpy: jest.SpyInstance;

    beforeEach(() => {
        command = new Command(mockSession);
        callMcpToolSpy = jest.spyOn(
            BaseService.prototype as unknown as { callMcpTool: () => Promise<unknown> },
            "callMcpTool",
        );
    });

    afterEach(() => {
        callMcpToolSpy.mockRestore();
    });

    test("execute success - JSON format response with stdout/stderr/exit_code", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-123",
            success: true,
            data: JSON.stringify({
                stdout: "hello world",
                stderr: "",
                exit_code: 0,
                traceId: "trace-1",
            }),
        });

        const result = await command.execute("echo hello");

        expect(result.success).toBe(true);
        expect(result.output).toBe("hello world");
        expect(result.stdout).toBe("hello world");
        expect(result.stderr).toBe("");
        expect(result.exitCode).toBe(0);
        expect(result.requestId).toBe("req-123");
        expect(result.traceId).toBe("trace-1");
        expect(callMcpToolSpy).toHaveBeenCalledWith("shell", {
            command: "echo hello",
            timeout_ms: 1000,
        });
    });

    test("execute with empty output", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-456",
            success: true,
            data: JSON.stringify({
                stdout: "",
                stderr: "",
                exit_code: 0,
                traceId: "",
            }),
        });

        const result = await command.execute("true");

        expect(result.success).toBe(true);
        expect(result.output).toBe("");
        expect(result.stdout).toBe("");
        expect(result.stderr).toBe("");
        expect(result.exitCode).toBe(0);
    });

    test("execute default timeout", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-1",
            success: true,
            data: JSON.stringify({ stdout: "ok", stderr: "", exit_code: 0 }),
        });

        await command.execute("ls");

        expect(callMcpToolSpy).toHaveBeenCalledWith("shell", {
            command: "ls",
            timeout_ms: 1000,
        });
    });

    test("execute custom timeout", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-1",
            success: true,
            data: JSON.stringify({ stdout: "ok", stderr: "", exit_code: 0 }),
        });

        await command.execute("sleep 5", 5000);

        expect(callMcpToolSpy).toHaveBeenCalledWith("shell", {
            command: "sleep 5",
            timeout_ms: 5000,
        });
    });

    test("execute API failure", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-fail",
            success: false,
            errorMessage: "Command timed out",
        });

        const result = await command.execute("sleep 100");

        expect(result.success).toBe(false);
        expect(result.exitCode).toBe(-1);
        expect(result.errorMessage).toBe("Command timed out");
        expect(result.output).toBe("");
    });

    test("execute exception handling", async () => {
        callMcpToolSpy.mockRejectedValue(new Error("Network error"));

        const result = await command.execute("ls");

        expect(result.success).toBe(false);
        expect(result.exitCode).toBe(-1);
        expect(result.errorMessage).toContain("Failed to execute command");
        expect(result.errorMessage).toContain("Network error");
    });

    test("execute with cwd parameter", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-1",
            success: true,
            data: JSON.stringify({ stdout: "ok", stderr: "", exit_code: 0 }),
        });

        await command.execute("pwd", 1000, "/tmp");

        expect(callMcpToolSpy).toHaveBeenCalledWith("shell", {
            command: "pwd",
            timeout_ms: 1000,
            cwd: "/tmp",
        });
    });

    test("execute with envs parameter", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-1",
            success: true,
            data: JSON.stringify({ stdout: "ok", stderr: "", exit_code: 0 }),
        });

        await command.execute("echo $FOO", 1000, undefined, { FOO: "bar" });

        expect(callMcpToolSpy).toHaveBeenCalledWith("shell", {
            command: "echo $FOO",
            timeout_ms: 1000,
            envs: { FOO: "bar" },
        });
    });

    test("execute with both cwd and envs", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-1",
            success: true,
            data: JSON.stringify({ stdout: "ok", stderr: "", exit_code: 0 }),
        });

        await command.execute("ls", 1000, "/home", { HOME: "/home/user" });

        expect(callMcpToolSpy).toHaveBeenCalledWith("shell", {
            command: "ls",
            timeout_ms: 1000,
            cwd: "/home",
            envs: { HOME: "/home/user" },
        });
    });

    test("execute envs validation - invalid key type", async () => {
        await expect(
            command.execute("ls", 1000, undefined, {
                key: 123 as unknown as string,
            }),
        ).rejects.toThrow("Invalid environment variables: all keys and values must be strings");
        expect(callMcpToolSpy).not.toHaveBeenCalled();
    });

    test("execute envs validation - invalid value type", async () => {
        await expect(
            command.execute("ls", 1000, undefined, {
                KEY: {} as unknown as string,
            }),
        ).rejects.toThrow("Invalid environment variables: all keys and values must be strings");
        expect(callMcpToolSpy).not.toHaveBeenCalled();
    });

    test("execute error JSON format with errorCode", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-err",
            success: false,
            errorMessage: JSON.stringify({
                stdout: "partial output",
                stderr: "error occurred",
                errorCode: 1,
                traceId: "trace-err",
            }),
        });

        const result = await command.execute("false");

        expect(result.success).toBe(false);
        expect(result.exitCode).toBe(1);
        expect(result.stdout).toBe("partial output");
        expect(result.stderr).toBe("error occurred");
        expect(result.output).toBe("partial outputerror occurred");
        expect(result.errorMessage).toBe("error occurred");
    });

    test("execute backward compatibility (non-JSON response)", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-legacy",
            success: true,
            data: "plain text output",
        });

        const result = await command.execute("echo hello");

        expect(result.success).toBe(true);
        expect(result.output).toBe("plain text output");
        expect(result.stdout).toBe("plain text output");
        expect(result.stderr).toBe("");
        expect(result.exitCode).toBe(0);
    });

    test("run alias works", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-run",
            success: true,
            data: JSON.stringify({ stdout: "run ok", stderr: "", exit_code: 0 }),
        });

        const result = await command.run("echo run");

        expect(result.success).toBe(true);
        expect(result.output).toBe("run ok");
        expect(callMcpToolSpy).toHaveBeenCalledWith("shell", {
            command: "echo run",
            timeout_ms: 1000,
        });
    });

    test("exec alias works", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-exec",
            success: true,
            data: JSON.stringify({ stdout: "exec ok", stderr: "", exit_code: 0 }),
        });

        const result = await command.exec("echo exec");

        expect(result.success).toBe(true);
        expect(result.output).toBe("exec ok");
        expect(callMcpToolSpy).toHaveBeenCalledWith("shell", {
            command: "echo exec",
            timeout_ms: 1000,
        });
    });

    test("execute non-zero exit code returns success false", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-1",
            success: true,
            data: JSON.stringify({
                stdout: "",
                stderr: "command not found",
                exit_code: 127,
                traceId: "",
            }),
        });

        const result = await command.execute("nonexistent-cmd");

        expect(result.success).toBe(false);
        expect(result.exitCode).toBe(127);
        expect(result.stderr).toBe("command not found");
        expect(result.output).toBe("command not found");
    });

    test("execute error JSON with exit_code fallback", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-1",
            success: false,
            errorMessage: JSON.stringify({
                stdout: "",
                stderr: "killed",
                exit_code: 137,
                traceId: "t1",
            }),
        });

        const result = await command.execute("sleep 999");

        expect(result.success).toBe(false);
        expect(result.exitCode).toBe(137);
        expect(result.traceId).toBe("t1");
    });

    test("execute non-JSON error message", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-1",
            success: false,
            errorMessage: "Plain error message",
        });

        const result = await command.execute("fail");

        expect(result.success).toBe(false);
        expect(result.exitCode).toBe(-1);
        expect(result.errorMessage).toBe("Plain error message");
    });

    test("execute data as object (not string)", async () => {
        callMcpToolSpy.mockResolvedValue({
            requestId: "req-1",
            success: true,
            data: { stdout: "obj out", stderr: "", exit_code: 0 },
        });

        const result = await command.execute("echo test");

        expect(result.success).toBe(true);
        expect(result.stdout).toBe("obj out");
        expect(result.output).toBe("obj out");
    });
});
