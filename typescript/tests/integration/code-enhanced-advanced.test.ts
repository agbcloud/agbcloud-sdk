/**
 * Code execution enhanced tests: Jupyter-like persistence, concurrent execution,
 * complex code with file ops, rich outputs (SVG/image), cross-language.
 */
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import type { EnhancedCodeExecutionResult } from "../../src/types/api-response";

jest.setTimeout(300_000);

function outputContains(result: EnhancedCodeExecutionResult, needle: string): boolean {
    const inResults = result.results?.some((r) => r.text?.includes(needle)) ?? false;
    const inStdout = result.logs?.stdout?.some((s) => s.includes(needle)) ?? false;
    return inResults || inStdout;
}

describe("Code execution enhanced (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    test("Python Jupyter-like persistence: variable carries across executions", async () => {
        const setVar = await session.code.run("x = 42\nprint('set x')", "python", 30);
        expect(setVar.success).toBe(true);
        expect(outputContains(setVar, "set x")).toBe(true);

        const getVar = await session.code.run("print(x)", "python", 30);
        expect(getVar.success).toBe(true);
        expect(outputContains(getVar, "42")).toBe(true);
    });

    test("R Jupyter-like persistence", async () => {
        const setVar = await session.code.run('y <- 99\ncat("set y")', "r", 30);
        expect(setVar.success).toBe(true);

        const getVar = await session.code.run("cat(y)", "r", 30);
        expect(getVar.success).toBe(true);
        expect(outputContains(getVar, "99")).toBe(true);
    });

    test("Java execution", async () => {
        const javaCode = `
System.out.println("Hello from Java");
int sum = 0;
for (int i = 1; i <= 10; i++) sum += i;
System.out.println("Sum: " + sum);
`.trim();
        const result = await session.code.run(javaCode, "java", 60);
        expect(result.success).toBe(true);
        expect(outputContains(result, "Hello from Java")).toBe(true);
        expect(outputContains(result, "Sum: 55")).toBe(true);
    });

    test("Python complex code with file operations", async () => {
        const pythonCode = `
import os, json
with open('/tmp/code_test.txt', 'w') as f:
    f.write('Code execution file test')
with open('/tmp/code_test.txt', 'r') as f:
    content = f.read()
result = {"content": content, "exists": os.path.exists('/tmp/code_test.txt')}
print(json.dumps(result))
`.trim();
        const result = await session.code.run(pythonCode, "python", 30);
        expect(result.success).toBe(true);
        expect(outputContains(result, "Code execution file test")).toBe(true);
    });

    test("Python matplotlib SVG output", async () => {
        const matplotlibCode = `
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
ax.set_title("Test Chart")

buf = io.BytesIO()
fig.savefig(buf, format='svg')
buf.seek(0)
print(buf.read().decode('utf-8')[:200])
plt.close()
`.trim();
        const result = await session.code.run(matplotlibCode, "python", 60);
        expect(result.success).toBe(true);
        expect(outputContains(result, "svg")).toBe(true);
    });

    test("case-insensitive language name", async () => {
        const result = await session.code.run("print('case-test')", "Python", 30);
        expect(result.success).toBe(true);
        expect(outputContains(result, "case-test")).toBe(true);
    });

    test("language alias py", async () => {
        const result = await session.code.run("print('alias-test')", "py", 30);
        expect(result.success).toBe(true);
        expect(outputContains(result, "alias-test")).toBe(true);
    });

    test("language alias js", async () => {
        const result = await session.code.run("console.log('js-alias')", "js", 30);
        expect(result.success).toBe(true);
        expect(outputContains(result, "js-alias")).toBe(true);
    });

    test("enhanced result structure", async () => {
        const result = await session.code.run("print('structure')", "python", 30);
        expect(result.success).toBe(true);
        expect(result.requestId).toBeDefined();
        expect(result.logs).toBeDefined();
        expect(result.results).toBeDefined();
    });
});

describe("Code concurrent execution (integration)", () => {
    let agb: AGB;
    let session1: Session;
    let session2: Session;

    beforeAll(async () => {
        agb = createAGB();
        session1 = await createTestSession(agb);
        session2 = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session1);
        await deleteTestSession(agb, session2);
    });

    test("concurrent code execution in different sessions", async () => {
        const pythonCode = `
import json, time
result = {"lang": "python", "ts": time.time()}
print(json.dumps(result))
`.trim();
        const jsCode = `
const result = { lang: "javascript", ts: Date.now() };
console.log(JSON.stringify(result));
`.trim();

        const [pyResult, jsResult] = await Promise.all([
            session1.code.run(pythonCode, "python", 30),
            session2.code.run(jsCode, "javascript", 30),
        ]);

        expect(pyResult.success).toBe(true);
        expect(outputContains(pyResult, "python")).toBe(true);

        expect(jsResult.success).toBe(true);
        expect(outputContains(jsResult, "javascript")).toBe(true);
    });
});
