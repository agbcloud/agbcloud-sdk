/**
 * Integration tests for the Code module.
 */
import { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import { createAGB, createTestSession, deleteTestSession } from "./setup";

jest.setTimeout(300_000);

describe("Code execution (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    test("run Python code", async () => {
        const result = await session.code.run(
            'print("Hello from Python")',
            "python",
            60,
        );
        expect(result.success).toBe(true);
        expect(result.requestId).toBeDefined();

        const hasOutput =
            result.results.some((r) => r.text?.includes("Hello from Python")) ||
            result.logs.stdout.some((s) => s.includes("Hello from Python"));
        expect(hasOutput).toBe(true);
    });

    test("run JavaScript code", async () => {
        const result = await session.code.run(
            'console.log("Hello from JS")',
            "javascript",
            60,
        );
        expect(result.success).toBe(true);
        const hasOutput =
            result.results.some((r) => r.text?.includes("Hello from JS")) ||
            result.logs.stdout.some((s) => s.includes("Hello from JS"));
        expect(hasOutput).toBe(true);
    });

    test("run Java code", async () => {
        const javaCode = `
System.out.println("Hello from Java");
int a = 10;
int b = 20;
System.out.println("Sum: " + (a + b));
`;
        const result = await session.code.run(javaCode, "java", 60);
        expect(result.success).toBe(true);
        const hasOutput =
            result.results.some((r) => r.text?.includes("Hello from Java")) ||
            result.logs.stdout.some((s) => s.includes("Hello from Java"));
        expect(hasOutput).toBe(true);
    });

    test("run R code", async () => {
        const rCode = `
numbers <- c(10, 20, 30, 40, 50)
cat("Mean:", mean(numbers), "\\n")
cat("Sum:", sum(numbers), "\\n")
`;
        const result = await session.code.run(rCode, "r", 60);
        expect(result.success).toBe(true);
        const hasOutput =
            result.results.some((r) => r.text?.includes("Mean:")) ||
            result.logs.stdout.some((s) => s.includes("Mean:"));
        expect(hasOutput).toBe(true);
    });

    test("case-insensitive language", async () => {
        const result = await session.code.run(
            'print("case test")',
            "PYTHON",
            30,
        );
        expect(result.success).toBe(true);
    });

    test("language alias py", async () => {
        const result = await session.code.run(
            'print("alias py")',
            "py",
            30,
        );
        expect(result.success).toBe(true);
    });

    test("language alias js", async () => {
        const result = await session.code.run(
            'console.log("alias js")',
            "js",
            30,
        );
        expect(result.success).toBe(true);
    });

    test("unsupported language rejected locally", async () => {
        const result = await session.code.run(
            'puts "hello"',
            "ruby",
            30,
        );
        expect(result.success).toBe(false);
        expect(result.errorMessage).toContain("Unsupported language");
    });

    test("Python error handling", async () => {
        const result = await session.code.run(
            "undefined_variable + 1",
            "python",
            30,
        );
        expect(result.success).toBe(false);
    });

    test("Python multi-line with imports", async () => {
        const code = `
import datetime
import platform
print(f"Python: {platform.python_version()}")
print(f"Time: {datetime.datetime.now()}")
`;
        const result = await session.code.run(code, "python", 60);
        expect(result.success).toBe(true);
        const hasOutput =
            result.results.some((r) => r.text?.includes("Python:")) ||
            result.logs.stdout.some((s) => s.includes("Python:"));
        expect(hasOutput).toBe(true);
    });

    test("execution result structure", async () => {
        const result = await session.code.run(
            'print("structure test")',
            "python",
            30,
        );
        expect(result.success).toBe(true);
        expect(result).toHaveProperty("logs");
        expect(result).toHaveProperty("results");
        expect(result).toHaveProperty("executionTime");
        expect(result.logs).toHaveProperty("stdout");
        expect(result.logs).toHaveProperty("stderr");
    });
});
