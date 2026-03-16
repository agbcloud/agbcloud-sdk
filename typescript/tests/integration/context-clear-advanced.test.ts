/**
 * Context clear advanced tests: clearAsync, full lifecycle, multiple clears, invalid ID.
 */
import { createAGB } from "./setup";
import type { AGB } from "../../src/agb";
import { Context } from "../../src/context";

jest.setTimeout(300_000);

describe("Context clear advanced (integration)", () => {
    let agb: AGB;

    beforeAll(() => {
        agb = createAGB();
    });

    test("clearAsync initiates clearing", async () => {
        const ctxName = `ts-clear-async-${Date.now()}`;
        const createResult = await agb.context.create(ctxName);
        expect(createResult.success).toBe(true);
        const contextId = createResult.context!.id;

        const clearResult = await agb.context.clearAsync(contextId);
        expect(clearResult.success).toBe(true);
        expect(clearResult.requestId).toBeDefined();

        await agb.context.delete(new Context(contextId, ctxName));
    });

    test("clear (synchronous) completes successfully", async () => {
        const ctxName = `ts-clear-sync-${Date.now()}`;
        const createResult = await agb.context.create(ctxName);
        expect(createResult.success).toBe(true);
        const contextId = createResult.context!.id;

        const clearResult = await agb.context.clear(contextId, 30, 2);
        expect(clearResult.success).toBe(true);

        await agb.context.delete(new Context(contextId, ctxName));
    });

    test("clearAsync with invalid context ID fails", async () => {
        const result = await agb.context.clearAsync("invalid-context-id-12345");
        expect(result.success).toBe(false);
    });

    test("full lifecycle: create, clearAsync, clear, verify, delete", async () => {
        const ctxName = `ts-clear-lifecycle-${Date.now()}`;
        const createResult = await agb.context.create(ctxName);
        expect(createResult.success).toBe(true);
        const contextId = createResult.context!.id;

        const asyncResult = await agb.context.clearAsync(contextId);
        expect(asyncResult.success).toBe(true);

        await new Promise((r) => setTimeout(r, 2000));

        const syncResult = await agb.context.clear(contextId, 30, 2);
        expect(syncResult.success).toBe(true);

        const getResult = await agb.context.get(ctxName, false);
        expect(getResult.success).toBe(true);
        expect(getResult.context).toBeDefined();

        await agb.context.delete(new Context(contextId, ctxName));
    });

    test("multiple clearAsync calls are idempotent", async () => {
        const ctxName = `ts-clear-multi-${Date.now()}`;
        const createResult = await agb.context.create(ctxName);
        expect(createResult.success).toBe(true);
        const contextId = createResult.context!.id;

        for (let i = 0; i < 3; i++) {
            const result = await agb.context.clearAsync(contextId);
            expect(result.success).toBe(true);
            await new Promise((r) => setTimeout(r, 500));
        }

        await agb.context.delete(new Context(contextId, ctxName));
    });
});
