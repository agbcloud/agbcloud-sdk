/**
 * Extended session tests: getSession detail, list with labels, lifecycle edge cases.
 */
import { createAGB, createTestSession, deleteTestSession, DEFAULT_IMAGE_ID } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import { CreateSessionParams } from "../../src/session-params";

jest.setTimeout(300_000);

describe("Session extended (integration)", () => {
    let agb: AGB;

    beforeAll(() => {
        agb = createAGB();
    });

    test("create session with labels", async () => {
        const labels = { team: "ts-test", env: `ext-${Date.now()}` };
        const params = new CreateSessionParams({
            imageId: DEFAULT_IMAGE_ID,
            labels,
        });
        const result = await agb.create(params);
        expect(result.success).toBe(true);
        expect(result.session).toBeDefined();

        const session = result.session!;
        try {
            const getResult = await session.getLabels();
            expect(getResult.success).toBe(true);
            const data = getResult.data as Record<string, string>;
            expect(data.team).toBe("ts-test");
        } finally {
            await deleteTestSession(agb, session);
        }
    });

    test("getSession returns detailed info", async () => {
        const session = await createTestSession(agb);
        try {
            const detail = await agb.getSession(session.getSessionId());
            expect(detail.success).toBe(true);
            expect(detail.data).toBeDefined();
            expect(detail.data!.sessionId).toBe(session.getSessionId());
        } finally {
            await deleteTestSession(agb, session);
        }
    });

    test("list sessions with label filter", async () => {
        const uniqueLabel = `filter-${Date.now()}`;
        const params = new CreateSessionParams({
            imageId: DEFAULT_IMAGE_ID,
            labels: { filterTest: uniqueLabel },
        });
        const result = await agb.create(params);
        expect(result.success).toBe(true);
        const session = result.session!;

        try {
            const listResult = await agb.list({ filterTest: uniqueLabel });
            expect(listResult.success).toBe(true);
            expect(listResult.sessionIds).toBeDefined();
            expect(listResult.sessionIds.length).toBeGreaterThanOrEqual(1);
        } finally {
            await deleteTestSession(agb, session);
        }
    });

    test("delete already deleted session is idempotent", async () => {
        const session = await createTestSession(agb);
        const sessionId = session.getSessionId();

        const firstDelete = await agb.delete(session);
        expect(firstDelete.success).toBe(true);

        const secondDelete = await agb.delete(session);
        expect(secondDelete.requestId).toBeDefined();
    });

    test("operations on deleted session fail gracefully", async () => {
        const session = await createTestSession(agb);
        await agb.delete(session);

        const cmdResult = await session.command.execute("echo test", 10000);
        expect(cmdResult.success).toBe(false);
    });

    test("session info contains sessionId", async () => {
        const session = await createTestSession(agb);
        try {
            const info = await session.info();
            expect(info.success).toBe(true);
            const data = info.data as Record<string, unknown>;
            expect(data.sessionId).toBe(session.getSessionId());
        } finally {
            await deleteTestSession(agb, session);
        }
    });

    test("list sessions returns array", async () => {
        const listResult = await agb.list();
        expect(listResult.success).toBe(true);
        expect(Array.isArray(listResult.sessionIds)).toBe(true);
    });
});
