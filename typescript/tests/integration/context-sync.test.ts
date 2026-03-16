/**
 * Integration tests for Context Sync: mount context into session, sync, info.
 */
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import { Context } from "../../src/context";
import { ContextSync, newSyncPolicy } from "../../src/context-sync";
import { CreateSessionParams } from "../../src/session-params";

jest.setTimeout(180_000);

describe("Context Sync (integration)", () => {
    let agb: AGB;
    const ctxName = `ts-sync-ctx-${Date.now()}`;
    let contextId: string;

    beforeAll(() => {
        agb = createAGB();
    });

    afterAll(async () => {
        if (contextId) {
            try {
                await agb.context.delete(new Context(contextId, ctxName));
            } catch { /* best effort */ }
        }
    });

    test("create context for sync tests", async () => {
        const result = await agb.context.get(ctxName, true);
        expect(result.success).toBe(true);
        expect(result.context).toBeDefined();
        contextId = result.context!.id;
    });

    test("create session with context sync mount", async () => {
        const sync = ContextSync.new(contextId, "/home/sync-test", newSyncPolicy());
        const params = new CreateSessionParams({
            imageId: "agb-code-space-2",
            contextSync: [sync],
        });

        const result = await agb.create(params);
        expect(result.success).toBe(true);
        expect(result.session).toBeDefined();

        const session = result.session!;

        try {
            const writeResult = await session.command.execute(
                'echo "sync-test-data" > /home/sync-test/test.txt',
                10000,
            );
            expect(writeResult.success).toBe(true);

            const readResult = await session.command.execute(
                "cat /home/sync-test/test.txt",
                10000,
            );
            expect(readResult.success).toBe(true);
            expect(readResult.output).toContain("sync-test-data");
        } finally {
            await deleteTestSession(agb, session);
        }
    });

    test("context sync info on session", async () => {
        const sync = ContextSync.new(contextId, "/home/sync-info", newSyncPolicy());
        const params = new CreateSessionParams({
            imageId: "agb-code-space-2",
            contextSync: [sync],
        });

        const result = await agb.create(params);
        expect(result.success).toBe(true);
        const session = result.session!;

        try {
            const infoResult = await session.context.info();
            expect(infoResult.success).toBe(true);
            expect(Array.isArray(infoResult.items)).toBe(true);
        } finally {
            await deleteTestSession(agb, session);
        }
    });

    test("manual sync triggers without error", async () => {
        const sync = ContextSync.new(contextId, "/home/sync-manual", newSyncPolicy());
        const params = new CreateSessionParams({
            imageId: "agb-code-space-2",
            contextSync: [sync],
        });

        const result = await agb.create(params);
        expect(result.success).toBe(true);
        const session = result.session!;

        try {
            const syncResult = await session.context.sync();
            expect(syncResult.success).toBe(true);
        } finally {
            await deleteTestSession(agb, session);
        }
    });
});
