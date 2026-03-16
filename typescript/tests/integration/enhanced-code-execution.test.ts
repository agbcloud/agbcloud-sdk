/**
 * Enhanced code execution tests: multi-language, rich output, logs, errors.
 */
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";

jest.setTimeout(300_000);

describe("Enhanced code execution (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    // Multi-language support

    test("execute JavaScript code", async () => {
        const result = await session.code.run(
            'console.log("Hello JS");',
            "javascript",
            60,
        );
        expect(result.success).toBe(true);
        const hasOutput =
            result.results.some((r) => r.text?.includes("Hello JS")) ||
            result.logs?.stdout?.some((l) => l.includes("Hello JS"));
        expect(hasOutput).toBe(true);
    });

    test("unsupported language (bash) rejected locally", async () => {
        const result = await session.code.run(
            'echo "Hello Shell"',
            "bash",
            60,
        );
        expect(result.success).toBe(false);
        expect(result.errorMessage).toContain("Unsupported language");
    });

    test("Python math operations", async () => {
        const result = await session.code.run(
            "import math\nprint(math.pi)\nprint(math.sqrt(144))",
            "python",
            60,
        );
        expect(result.success).toBe(true);
        const output = result.results.map((r) => r.text).join("\n") +
            (result.logs?.stdout?.join("\n") ?? "");
        expect(output).toContain("3.14");
        expect(output).toContain("12");
    });

    test("Python list comprehension", async () => {
        const result = await session.code.run(
            "squares = [x**2 for x in range(5)]\nprint(squares)",
            "python",
            60,
        );
        expect(result.success).toBe(true);
        const output = result.results.map((r) => r.text).join("\n") +
            (result.logs?.stdout?.join("\n") ?? "");
        expect(output).toContain("[0, 1, 4, 9, 16]");
    });

    // Error handling

    test("Python syntax error returns error info", async () => {
        const result = await session.code.run(
            "def foo(\n  pass",
            "python",
            60,
        );
        const allErrors = (result.errorMessage ?? "") +
            (result.logs?.stderr?.join("\n") ?? "");
        expect(allErrors.length).toBeGreaterThan(0);
    });

    test("Python runtime error (division by zero)", async () => {
        const result = await session.code.run(
            "x = 1 / 0",
            "python",
            60,
        );
        const allErrors = (result.errorMessage ?? "") +
            (result.logs?.stderr?.join("\n") ?? "");
        expect(allErrors).toContain("division by zero");
    });

    test("Python import error returns error info", async () => {
        const result = await session.code.run(
            "import nonexistent_module_xyz",
            "python",
            60,
        );
        const allErrors = (result.errorMessage ?? "") +
            (result.logs?.stderr?.join("\n") ?? "");
        expect(allErrors.length).toBeGreaterThan(0);
    });

    // Output & logs

    test("Python stdout in logs", async () => {
        const result = await session.code.run(
            'print("log-line-1")\nprint("log-line-2")',
            "python",
            60,
        );
        expect(result.success).toBe(true);
        const allOutput = result.results.map((r) => r.text).join("\n") +
            (result.logs?.stdout?.join("\n") ?? "");
        expect(allOutput).toContain("log-line-1");
        expect(allOutput).toContain("log-line-2");
    });

    test("Python stderr captured", async () => {
        const result = await session.code.run(
            'import sys\nsys.stderr.write("err-msg\\n")\nprint("ok")',
            "python",
            60,
        );
        expect(result.success).toBe(true);
        const allOutput = (result.logs?.stderr?.join("\n") ?? "") +
            (result.logs?.stdout?.join("\n") ?? "") +
            result.results.map((r) => r.text).join("\n");
        expect(allOutput).toContain("ok");
    });

    test("Python multiline output", async () => {
        const code = 'for i in range(5):\n    print(f"line-{i}")';
        const result = await session.code.run(code, "python", 60);
        expect(result.success).toBe(true);
        const allOutput = result.results.map((r) => r.text).join("\n") +
            (result.logs?.stdout?.join("\n") ?? "");
        for (let i = 0; i < 5; i++) {
            expect(allOutput).toContain(`line-${i}`);
        }
    });

    // Rich output (matplotlib)

    test("Python matplotlib generates image", async () => {
        const code = `
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.figure(figsize=(4, 3))
plt.plot([1, 2, 3], [1, 4, 9])
plt.title("Test Plot")
plt.savefig("/tmp/test_plot.png")
print("plot-saved")
`;
        const result = await session.code.run(code, "python", 120);
        expect(result.success).toBe(true);
        const allOutput = result.results.map((r) => r.text).join("\n") +
            (result.logs?.stdout?.join("\n") ?? "");
        expect(allOutput).toContain("plot-saved");
    });

    // Empty code

    test("empty code string", async () => {
        const result = await session.code.run("", "python", 60);
        expect(result.success).toBe(false);
    });
});
