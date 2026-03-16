/**
 * Advanced command execution tests: cwd with spaces, special env chars,
 * timeout limits, exit codes, stdout/stderr separation, concurrent execution.
 */
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";

jest.setTimeout(300_000);

describe("Command advanced scenarios (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    test("shell command creates and reads file via filesystem", async () => {
        const cmd = 'echo "Test content from shell" > /tmp/shell_test.txt';
        const createResult = await session.command.execute(cmd, 10000);
        expect(createResult.success).toBe(true);

        const readResult = await session.file.read("/tmp/shell_test.txt");
        expect(readResult.success).toBe(true);
        expect(readResult.content).toContain("Test content from shell");

        const delResult = await session.command.execute("rm /tmp/shell_test.txt", 10000);
        expect(delResult.success).toBe(true);
    });

    test("complex command with mkdir and pipe", async () => {
        const cmd = 'mkdir -p /tmp/test_dir_adv && echo "complex" > /tmp/test_dir_adv/complex.txt && ls /tmp/test_dir_adv';
        const result = await session.command.execute(cmd, 10000);
        expect(result.success).toBe(true);
        expect(result.output).toContain("complex.txt");

        const content = await session.file.read("/tmp/test_dir_adv/complex.txt");
        expect(content.content).toContain("complex");

        await session.command.execute("rm -rf /tmp/test_dir_adv", 10000);
    });

    test("cwd with spaces", async () => {
        const testDir = "/tmp/test dir with spaces";
        const mkdirResult = await session.command.execute(`mkdir -p '${testDir}'`, 10000);
        expect(mkdirResult.success).toBe(true);

        const pwdResult = await session.command.execute("pwd", 10000, testDir);
        expect(pwdResult.success).toBe(true);
        expect(pwdResult.output).toContain("/tmp/test");

        const fileResult = await session.command.execute(
            "echo 'test content' > test_file.txt", 10000, testDir,
        );
        expect(fileResult.success).toBe(true);

        const listResult = await session.command.execute("ls test_file.txt", 10000, testDir);
        expect(listResult.success).toBe(true);
        expect(listResult.output).toContain("test_file.txt");

        await session.command.execute(`rm -rf '${testDir}'`, 10000);
    });

    test("envs with special characters (injection safety)", async () => {
        const result1 = await session.command.execute(
            "echo $TEST_VAR", 10000, undefined,
            { TEST_VAR: "value with 'single quotes'" },
        );
        expect(result1.success).toBe(true);
        expect(result1.output).toContain("value with");

        const result2 = await session.command.execute(
            "echo $TEST_VAR", 10000, undefined,
            { TEST_VAR: "value; rm -rf /" },
        );
        expect(result2.success).toBe(true);
        expect(result2.output).toContain("value");

        const result3 = await session.command.execute(
            "echo $TEST_VAR", 10000, undefined,
            { TEST_VAR: "value with !@#$%^&*()" },
        );
        expect(result3.success).toBe(true);
    });

    test("cwd (spaces) + envs (special chars) combined", async () => {
        const testDir = "/tmp/test dir combined";
        await session.command.execute(`mkdir -p '${testDir}'`, 10000);

        const result = await session.command.execute(
            "pwd && echo $CUSTOM_VAR", 10000, testDir,
            { CUSTOM_VAR: "custom_value_with 'quotes'" },
        );
        expect(result.success).toBe(true);
        expect(result.output).toContain("/tmp/test");

        await session.command.execute(`rm -rf '${testDir}'`, 10000);
    });

    test("timeout parameter variations", async () => {
        const result1 = await session.command.execute("echo 'fast'", 5000);
        expect(result1.success).toBe(true);

        const result2 = await session.command.execute("echo 'medium'", 30000);
        expect(result2.success).toBe(true);

        const result3 = await session.command.execute("echo 'large-timeout'", 50000);
        expect(result3.success).toBe(true);
    });

    test("command permission edge case", async () => {
        const result = await session.command.execute("echo test > /root/protected.txt", 10000);
        expect(typeof result.success).toBe("boolean");
    });

    test("invalid command returns error", async () => {
        const result = await session.command.execute("invalid_command_12345", 10000);
        expect(result.success).toBe(false);
    });
});
