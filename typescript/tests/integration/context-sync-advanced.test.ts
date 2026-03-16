/**
 * Context sync advanced tests: mapping policy, upload mode variations, pagination.
 */
import { createAGB, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import { Context } from "../../src/context";
import {
    ContextSync,
    newSyncPolicy,
    newUploadPolicy,
    UploadMode,
    Lifecycle,
    newRecyclePolicy,
} from "../../src/context-sync";
import { CreateSessionParams } from "../../src/session-params";

jest.setTimeout(300_000);

describe("Context sync mapping policy (integration)", () => {
    let agb: AGB;

    beforeAll(() => {
        agb = createAGB();
    });

    test("session creation with mappingPolicy for cross-platform persistence", async () => {
        const ctxName = `ts-mapping-${Date.now()}`;
        const ctxRes = await agb.context.get(ctxName, true);
        expect(ctxRes.success).toBe(true);
        const contextId = ctxRes.context!.id;

        let session: Session | undefined;
        try {
            const policy = newSyncPolicy({
                mappingPolicy: { path: "/home/mapped" },
            });
            const sync = ContextSync.new(contextId, "/home/sync-test", policy);
            const params = new CreateSessionParams({
                imageId: "agb-code-space-2",
                contextSync: [sync],
            });
            const result = await agb.create(params);
            expect(result.success).toBe(true);
            session = result.session!;
            expect(session.getSessionId()).toBeDefined();
        } finally {
            if (session) await deleteTestSession(agb, session);
            await agb.context.delete(new Context(contextId, ctxName));
        }
    });
});

describe("Context sync upload mode (integration)", () => {
    let agb: AGB;

    beforeAll(() => {
        agb = createAGB();
    });

    test("default File upload mode", async () => {
        const ctxName = `ts-upload-file-${Date.now()}`;
        const ctxRes = await agb.context.get(ctxName, true);
        expect(ctxRes.success).toBe(true);
        const contextId = ctxRes.context!.id;

        let session: Session | undefined;
        try {
            const policy = newSyncPolicy({
                uploadPolicy: newUploadPolicy({ uploadMode: UploadMode.FILE }),
            });
            const sync = ContextSync.new(contextId, "/home/sync-test", policy);
            const params = new CreateSessionParams({
                imageId: "agb-code-space-2",
                contextSync: [sync],
            });
            const result = await agb.create(params);
            expect(result.success).toBe(true);
            session = result.session!;
        } finally {
            if (session) await deleteTestSession(agb, session);
            await agb.context.delete(new Context(contextId, ctxName));
        }
    });

    test("Archive upload mode", async () => {
        const ctxName = `ts-upload-archive-${Date.now()}`;
        const ctxRes = await agb.context.get(ctxName, true);
        expect(ctxRes.success).toBe(true);
        const contextId = ctxRes.context!.id;

        let session: Session | undefined;
        try {
            const policy = newSyncPolicy({
                uploadPolicy: newUploadPolicy({ uploadMode: UploadMode.ARCHIVE }),
            });
            const sync = ContextSync.new(contextId, "/home/sync-test", policy);
            const params = new CreateSessionParams({
                imageId: "agb-code-space-2",
                contextSync: [sync],
            });
            const result = await agb.create(params);
            expect(result.success).toBe(true);
            session = result.session!;
        } finally {
            if (session) await deleteTestSession(agb, session);
            await agb.context.delete(new Context(contextId, ctxName));
        }
    });

    test("custom recyclePolicy lifecycle", async () => {
        const ctxName = `ts-recycle-${Date.now()}`;
        const ctxRes = await agb.context.get(ctxName, true);
        expect(ctxRes.success).toBe(true);
        const contextId = ctxRes.context!.id;

        let session: Session | undefined;
        try {
            const policy = newSyncPolicy({
                recyclePolicy: newRecyclePolicy({
                    lifecycle: Lifecycle.LIFECYCLE_3DAYS,
                }),
            });
            const sync = ContextSync.new(contextId, "/home/sync-test", policy);
            const params = new CreateSessionParams({
                imageId: "agb-code-space-2",
                contextSync: [sync],
            });
            const result = await agb.create(params);
            expect(result.success).toBe(true);
            session = result.session!;
        } finally {
            if (session) await deleteTestSession(agb, session);
            await agb.context.delete(new Context(contextId, ctxName));
        }
    });
});

describe("Context pagination (integration)", () => {
    let agb: AGB;
    const createdContextIds: { id: string; name: string }[] = [];

    beforeAll(async () => {
        agb = createAGB();
        for (let i = 0; i < 3; i++) {
            const name = `ts-page-${Date.now()}-${i}`;
            const res = await agb.context.create(name);
            expect(res.success).toBe(true);
            createdContextIds.push({ id: res.context!.id, name });
        }
    });

    afterAll(async () => {
        for (const ctx of createdContextIds) {
            await agb.context.delete(new Context(ctx.id, ctx.name));
        }
    });

    test("list contexts with default pagination", async () => {
        const result = await agb.context.list();
        expect(result.success).toBe(true);
        expect(result.contexts.length).toBeGreaterThanOrEqual(3);
    });

    test("list contexts with small maxResults", async () => {
        const result = await agb.context.list({ maxResults: 2 });
        expect(result.success).toBe(true);
        expect(result.contexts.length).toBeGreaterThanOrEqual(1);
        expect(result.contexts.length).toBeLessThanOrEqual(2);
    });

    test("list contexts with larger maxResults returns more", async () => {
        const result = await agb.context.list({ maxResults: 50 });
        expect(result.success).toBe(true);
        expect(result.contexts.length).toBeGreaterThanOrEqual(3);
    });
});
