/**
 * Context persistence tests: file persistence across sessions in same context,
 * file isolation between different contexts.
 */
import { createAGB, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import { Context } from "../../src/context";
import { ContextSync, newSyncPolicy } from "../../src/context-sync";
import { CreateSessionParams } from "../../src/session-params";

jest.setTimeout(600_000);

describe("Context persistence (integration)", () => {
    let agb: AGB;

    beforeAll(() => {
        agb = createAGB();
    });

    test("files persist between sessions in the same context", async () => {
        const ctxName = `ts-persist-${Date.now()}`;
        const syncPath = "/home/sync-test";
        const ctxResult = await agb.context.get(ctxName, true);
        expect(ctxResult.success).toBe(true);
        const contextId = ctxResult.context!.id;

        const testFilePath = `${syncPath}/persist-file-${Date.now()}.txt`;
        const testContent = "persistence-test-content-12345";

        let session1: Session | undefined;
        try {
            const sync = ContextSync.new(contextId, syncPath, newSyncPolicy());
            const params = new CreateSessionParams({
                imageId: "agb-code-space-2",
                contextSync: [sync],
            });
            const result = await agb.create(params);
            expect(result.success).toBe(true);
            session1 = result.session!;

            await session1.command.execute(`mkdir -p ${syncPath}`, 10000);

            const writeResult = await session1.command.execute(
                `echo '${testContent}' > ${testFilePath}`, 10000,
            );
            expect(writeResult.success).toBe(true);

            const verifyResult = await session1.command.execute(`cat ${testFilePath}`, 10000);
            expect(verifyResult.output).toContain(testContent);

            await session1.context.sync(contextId, syncPath, "upload");
        } finally {
            if (session1) {
                await agb.delete(session1, true);
            }
        }

        await new Promise((r) => setTimeout(r, 30000));

        let session2: Session | undefined;
        try {
            const sync = ContextSync.new(contextId, syncPath, newSyncPolicy());
            const params = new CreateSessionParams({
                imageId: "agb-code-space-2",
                contextSync: [sync],
            });
            const result = await agb.create(params);
            expect(result.success).toBe(true);
            session2 = result.session!;

            let found = false;
            for (let attempt = 0; attempt < 10; attempt++) {
                const readResult = await session2.command.execute(`cat ${testFilePath} 2>&1`, 10000);
                if (readResult.output?.includes(testContent)) {
                    found = true;
                    break;
                }
                await new Promise((r) => setTimeout(r, 5000));
            }
            expect(found).toBe(true);
        } finally {
            if (session2) await deleteTestSession(agb, session2);
            await agb.context.delete(new Context(contextId, ctxName));
        }
    });

    test("files are isolated between different contexts", async () => {
        const ctxName1 = `ts-iso-a-${Date.now()}`;
        const ctxName2 = `ts-iso-b-${Date.now()}`;
        const ctx1 = await agb.context.get(ctxName1, true);
        const ctx2 = await agb.context.get(ctxName2, true);
        expect(ctx1.success).toBe(true);
        expect(ctx2.success).toBe(true);
        const ctxId1 = ctx1.context!.id;
        const ctxId2 = ctx2.context!.id;

        const testFile = `/home/sync-test/isolated-${Date.now()}.txt`;
        const testContent = "isolation-test-data";

        let session1: Session | undefined;
        try {
            const sync = ContextSync.new(ctxId1, "/home/sync-test", newSyncPolicy());
            const params = new CreateSessionParams({
                imageId: "agb-code-space-2",
                contextSync: [sync],
            });
            const result = await agb.create(params);
            session1 = result.session!;
            await session1.command.execute(`echo '${testContent}' > ${testFile}`, 10000);
        } finally {
            if (session1) await deleteTestSession(agb, session1);
        }

        let session2: Session | undefined;
        try {
            const sync = ContextSync.new(ctxId2, "/home/sync-test", newSyncPolicy());
            const params = new CreateSessionParams({
                imageId: "agb-code-space-2",
                contextSync: [sync],
            });
            const result = await agb.create(params);
            session2 = result.session!;

            const readResult = await session2.command.execute(`cat ${testFile} 2>&1`, 10000);
            const fileFound = readResult.output?.includes(testContent) ?? false;
            expect(fileFound).toBe(false);
        } finally {
            if (session2) await deleteTestSession(agb, session2);
            await agb.context.delete(new Context(ctxId1, ctxName1));
            await agb.context.delete(new Context(ctxId2, ctxName2));
        }
    });
});
