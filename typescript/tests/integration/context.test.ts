/**
 * Integration tests for Context service: create, get, list, delete, clear.
 */
import { createAGB } from "./setup";
import type { AGB } from "../../src/agb";
import { Context } from "../../src/context";

jest.setTimeout(120_000);

describe("Context service (integration)", () => {
    let agb: AGB;
    const contextName = `ts-integ-ctx-${Date.now()}`;
    let contextId: string;

    beforeAll(() => {
        agb = createAGB();
    });

    test("create context", async () => {
        const result = await agb.context.create(contextName);
        expect(result.success).toBe(true);
        expect(result.context).toBeDefined();
        expect(result.context!.id).toBeTruthy();
        expect(result.context!.name).toBe(contextName);
        contextId = result.context!.id;
    });

    test("create context with empty name fails", async () => {
        const result = await agb.context.create("");
        expect(result.success).toBe(false);
        expect(result.errorMessage).toBeTruthy();
    });

    test("get context by name", async () => {
        const result = await agb.context.get(contextName, false);
        expect(result.success).toBe(true);
        expect(result.context).toBeDefined();
        expect(result.context!.id).toBe(contextId);
    });

    test("get context with create=true (idempotent)", async () => {
        const result = await agb.context.get(contextName, true);
        expect(result.success).toBe(true);
        expect(result.context).toBeDefined();
        expect(result.context!.id).toBe(contextId);
    });

    test("get context by id", async () => {
        const result = await agb.context.get(undefined, false, undefined, contextId);
        expect(result.success).toBe(true);
        expect(result.context).toBeDefined();
        expect(result.context!.id).toBe(contextId);
    });

    test("get with empty name and no id fails", async () => {
        const result = await agb.context.get("", false);
        expect(result.success).toBe(false);
    });

    test("list contexts returns array", async () => {
        const result = await agb.context.list({ maxResults: 10 });
        expect(result.success).toBe(true);
        expect(Array.isArray(result.contexts)).toBe(true);
        expect(result.contexts!.length).toBeGreaterThanOrEqual(1);

        const found = result.contexts!.find((c) => c.id === contextId);
        expect(found).toBeDefined();
    });

    test("list contexts with pagination", async () => {
        const result = await agb.context.list({ maxResults: 1 });
        expect(result.success).toBe(true);
        expect(result.contexts!.length).toBeLessThanOrEqual(1);
    });

    test("clear context", async () => {
        const result = await agb.context.clear(contextId);
        expect(result.success).toBe(true);
    });

    test("delete context", async () => {
        const ctx = new Context(contextId, contextName);
        const result = await agb.context.delete(ctx);
        expect(result.success).toBe(true);
    });

    test("get deleted context fails", async () => {
        const result = await agb.context.get(undefined, false, undefined, contextId);
        expect(result.success).toBe(false);
    });
});
