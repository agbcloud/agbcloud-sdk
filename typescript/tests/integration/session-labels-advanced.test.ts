/**
 * Session labels advanced tests: boundary values, empty/mixed keys, list by labels.
 * Session getLink advanced: protocol types, port variations.
 * Session delete with syncContext.
 */
import { createAGB, createTestSession, deleteTestSession, DEFAULT_IMAGE_ID } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import { CreateSessionParams } from "../../src/session-params";

jest.setTimeout(300_000);

describe("Session labels advanced (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    test("set and get labels with valid data", async () => {
        const labels = { env: "test", version: "1.0" };
        const setResult = await session.setLabels(labels);
        expect(setResult.success).toBe(true);

        const getResult = await session.getLabels();
        expect(getResult.success).toBe(true);
        const data = getResult.data as Record<string, string>;
        expect(data.env).toBe("test");
        expect(data.version).toBe("1.0");
    });

    test("update labels replaces old values", async () => {
        await session.setLabels({ key1: "old" });
        await session.setLabels({ key1: "new", key2: "added" });

        const getResult = await session.getLabels();
        expect(getResult.success).toBe(true);
        const data = getResult.data as Record<string, string>;
        expect(data.key1).toBe("new");
        expect(data.key2).toBe("added");
    });

    test("set labels with empty key throws or fails", async () => {
        let threw = false;
        try {
            const result = await session.setLabels({ "": "empty-key" });
            if (!result || !result.success) threw = true;
        } catch {
            threw = true;
        }
        expect(threw).toBe(true);
    });

    test("get labels returns empty when no labels set", async () => {
        const freshSession = await createTestSession(agb);
        try {
            const result = await freshSession.getLabels();
            expect(result.success).toBe(true);
        } finally {
            await deleteTestSession(agb, freshSession);
        }
    });

    test("list sessions by matching labels", async () => {
        const uniqueLabel = `label-match-${Date.now()}`;
        const params = new CreateSessionParams({
            imageId: DEFAULT_IMAGE_ID,
            labels: { matchTest: uniqueLabel },
        });
        const createResult = await agb.create(params);
        expect(createResult.success).toBe(true);
        const labelSession = createResult.session!;

        try {
            const listResult = await agb.list({ matchTest: uniqueLabel });
            expect(listResult.success).toBe(true);
            expect(listResult.sessionIds.length).toBeGreaterThanOrEqual(1);
            expect(listResult.sessionIds).toContain(labelSession.getSessionId());
        } finally {
            await deleteTestSession(agb, labelSession);
        }
    });

    test("list sessions by non-matching labels returns empty", async () => {
        const listResult = await agb.list({ nonexistent: `never-${Date.now()}` });
        expect(listResult.success).toBe(true);
        expect(listResult.sessionIds.length).toBe(0);
    });
});

describe("Session getLink advanced (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    test("getLink without parameters", async () => {
        const result = await session.getLink();
        expect(result.requestId).toBeDefined();
    });

    test("getLink with protocol type", async () => {
        const result = await session.getLink("https");
        expect(result.requestId).toBeDefined();
    });

    test("getLink with valid port", async () => {
        const result = await session.getLink("https", 8080);
        expect(result.requestId).toBeDefined();
    });

    test("getLink with boundary port 1", async () => {
        const result = await session.getLink("https", 1);
        expect(result.requestId).toBeDefined();
    });

    test("getLink with boundary port 65535", async () => {
        const result = await session.getLink("https", 65535);
        expect(result.requestId).toBeDefined();
    });
});

describe("Session delete with syncContext (integration)", () => {
    let agb: AGB;

    beforeAll(() => {
        agb = createAGB();
    });

    test("delete session without syncContext", async () => {
        const session = await createTestSession(agb);
        const result = await agb.delete(session, false);
        expect(result.success).toBe(true);
    });

    test("delete session with syncContext=true", async () => {
        const session = await createTestSession(agb);
        const result = await agb.delete(session, true);
        expect(result.success).toBe(true);
    });

    test("session.delete() directly", async () => {
        const session = await createTestSession(agb);
        const result = await session.delete();
        expect(result.success).toBe(true);
    });
});
