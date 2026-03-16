/**
 * Integration tests for Java code execution.
 * Reference: python/tests/integration/test_java_simple.py
 * Reference: TypeScript code tests (Java)
 */
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import type { EnhancedCodeExecutionResult } from "../../src/types/api-response";

jest.setTimeout(300_000);

function getOutput(r: EnhancedCodeExecutionResult): string {
    const texts = r.results?.map((x) => x.text ?? "").join("\n") ?? "";
    const stdout = r.logs?.stdout?.join("\n") ?? "";
    return [texts, stdout].filter(Boolean).join("\n");
}

describe("Java code execution (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    test("execute simple Java code", async () => {
        const code = `System.out.println("Hello from Java!");`;
        const result = await session.code.execute(code, "java");
        expect(result.success).toBe(true);
        expect(getOutput(result)).toContain("Hello from Java!");
    });

    test("Java with arithmetic operations", async () => {
        const code = `
int a = 10;
int b = 20;
System.out.println("Sum: " + (a + b));
`;
        const result = await session.code.execute(code, "java");
        expect(result.success).toBe(true);
        expect(getOutput(result)).toContain("Sum: 30");
    });

    test("Java with string operations", async () => {
        const code = `
String greeting = "Hello";
String name = "AGB";
System.out.println(greeting + " " + name + "!");
`;
        const result = await session.code.execute(code, "java");
        expect(result.success).toBe(true);
        expect(getOutput(result)).toContain("Hello AGB!");
    });

    test("Java with ArrayList", async () => {
        const code = `
import java.util.ArrayList;
ArrayList<String> list = new ArrayList<>();
list.add("alpha");
list.add("beta");
list.add("gamma");
System.out.println("Size: " + list.size());
for (String s : list) {
    System.out.println(s);
}
`;
        const result = await session.code.execute(code, "java");
        expect(result.success).toBe(true);
        expect(getOutput(result)).toContain("Size: 3");
        expect(getOutput(result)).toContain("alpha");
    });

    test("Java error handling", async () => {
        const code = `
try {
    int result = 10 / 0;
} catch (ArithmeticException e) {
    System.out.println("Caught: " + e.getMessage());
}
`;
        const result = await session.code.execute(code, "java");
        expect(result.success).toBe(true);
        expect(getOutput(result)).toContain("Caught:");
    });

    test("Java Jupyter-like persistence", async () => {
        // First execution: define variable
        const code1 = `
int counter = 42;
System.out.println("counter = " + counter);
`;
        const r1 = await session.code.execute(code1, "java");
        expect(r1.success).toBe(true);
        expect(getOutput(r1)).toContain("counter = 42");

        // Second execution: use same variable (Jupyter-like)
        const code2 = `
counter = counter + 8;
System.out.println("counter = " + counter);
`;
        const r2 = await session.code.execute(code2, "java");
        expect(r2.success).toBe(true);
        expect(getOutput(r2)).toContain("counter = 50");
    });
});
