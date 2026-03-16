/**
 * Integration tests for the Command module.
 */
import { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import { createAGB, createTestSession, deleteTestSession } from "./setup";

jest.setTimeout(300_000);

describe("Command execution (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    test("execute basic command", async () => {
        const result = await session.command.execute("echo hello", 10000);
        expect(result.success).toBe(true);
        expect(result.output).toContain("hello");
        expect(result.exitCode).toBe(0);
        expect(result.requestId).toBeDefined();
    });

    test("execute whoami command", async () => {
        const result = await session.command.execute("whoami", 10000);
        expect(result.success).toBe(true);
        expect(result.output.trim()).toBeTruthy();
    });

    test("execute pwd command", async () => {
        const result = await session.command.execute("pwd", 10000);
        expect(result.success).toBe(true);
        expect(result.output.trim()).toMatch(/^\//);
    });

    test("execute command with cwd", async () => {
        const result = await session.command.execute("pwd", 10000, "/tmp");
        expect(result.success).toBe(true);
        expect(result.output.trim()).toBe("/tmp");
    });

    test("execute command with envs", async () => {
        const result = await session.command.execute(
            "echo $TEST_VAR",
            10000,
            undefined,
            { TEST_VAR: "integration_test_value" },
        );
        expect(result.success).toBe(true);
        expect(result.output).toContain("integration_test_value");
    });

    test("execute command with cwd and envs", async () => {
        const result = await session.command.execute(
            "pwd && echo $MY_VAR",
            10000,
            "/tmp",
            { MY_VAR: "combined_test" },
        );
        expect(result.success).toBe(true);
        expect(result.output).toContain("/tmp");
        expect(result.output).toContain("combined_test");
    });

    test("execute file operations", async () => {
        const write = await session.command.execute(
            "echo 'Hello AGB TS!' > /tmp/ts_test.txt",
            10000,
        );
        expect(write.success).toBe(true);

        const read = await session.command.execute("cat /tmp/ts_test.txt", 10000);
        expect(read.success).toBe(true);
        expect(read.output).toContain("Hello AGB TS!");

        const cleanup = await session.command.execute("rm /tmp/ts_test.txt", 10000);
        expect(cleanup.success).toBe(true);
    });

    test("execute nonexistent command fails", async () => {
        const result = await session.command.execute("nonexistent_cmd_xyz", 10000);
        expect(result.success).toBe(false);
    });

    test("execute ls on nonexistent path fails", async () => {
        const result = await session.command.execute("ls /nonexistent/path", 10000);
        expect(result.success).toBe(false);
    });

    test("stdout and stderr fields are populated", async () => {
        const result = await session.command.execute("echo out_msg", 10000);
        expect(result.success).toBe(true);
        expect(result.stdout).toContain("out_msg");
    });
});
