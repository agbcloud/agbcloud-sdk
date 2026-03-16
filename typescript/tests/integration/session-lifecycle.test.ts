/**
 * Integration tests for session lifecycle: create, get, list, delete.
 */
import { AGB } from "../../src/agb";
import { CreateSessionParams } from "../../src/session-params";
import { Session } from "../../src/session";
import { createAGB, createTestSession, deleteTestSession, DEFAULT_IMAGE_ID } from "./setup";

jest.setTimeout(300_000);

describe("Session lifecycle (integration)", () => {
    let agb: AGB;

    beforeAll(() => {
        agb = createAGB();
    });

    test("create and delete session", async () => {
        const params = new CreateSessionParams({ imageId: DEFAULT_IMAGE_ID });
        const result = await agb.create(params);

        expect(result.success).toBe(true);
        expect(result.session).toBeDefined();
        expect(result.requestId).toBeTruthy();

        const session = result.session!;
        expect(session.getSessionId()).toBeTruthy();

        const deleteResult = await agb.delete(session);
        expect(deleteResult.success).toBe(true);
    });

    test("create session with empty imageId fails", async () => {
        const params = new CreateSessionParams({});
        const result = await agb.create(params);
        expect(result.success).toBe(false);
        expect(result.errorMessage).toBeTruthy();
    });

    test("create with null params fails", async () => {
        const result = await agb.create(null);
        expect(result.success).toBe(false);
        expect(result.errorMessage).toContain("params is required");
    });

    test("get session by ID", async () => {
        const session = await createTestSession(agb);
        const sessionId = session.getSessionId();

        try {
            const getResult = await agb.get(sessionId);
            expect(getResult.success).toBe(true);
            expect(getResult.session).toBeDefined();
            expect(getResult.session!.getSessionId()).toBe(sessionId);
        } finally {
            await deleteTestSession(agb, session);
        }
    });

    test("get deleted session returns success false and session null", async () => {
        const session = await createTestSession(agb);
        const sessionId = session.getSessionId();

        const deleteResult = await agb.delete(session);
        expect(deleteResult.success).toBe(true);

        const getResult = await agb.get(sessionId);
        expect(getResult.success).toBe(false);
        // Client should return session: null on failure for predictable assertion (not undefined)
        expect(getResult.session).toBeNull();
    });

    test("get non-existent session fails", async () => {
        const result = await agb.get("session-nonexistent-12345");
        expect(result.success).toBe(false);
        expect(result.errorMessage).toBeTruthy();
    });

    test("get empty session ID fails", async () => {
        const result = await agb.get("");
        expect(result.success).toBe(false);
        expect(result.errorMessage).toContain("sessionId is required");
    });

    test("get whitespace session ID fails", async () => {
        const result = await agb.get("   ");
        expect(result.success).toBe(false);
        expect(result.errorMessage).toContain("sessionId is required");
    });

    test("list sessions", async () => {
        const session = await createTestSession(agb);

        try {
            const listResult = await agb.list();
            expect(listResult.success).toBe(true);
            expect(Array.isArray(listResult.sessionIds)).toBe(true);
            expect(listResult.sessionIds.length).toBeGreaterThan(0);

            const found = listResult.sessionIds.includes(session.getSessionId());
            expect(found).toBe(true);
        } finally {
            await deleteTestSession(agb, session);
        }
    });

    test("list sessions with pagination", async () => {
        const session = await createTestSession(agb);

        try {
            const page1 = await agb.list(undefined, 1, 1);
            expect(page1.success).toBe(true);
            expect(page1.sessionIds.length).toBeLessThanOrEqual(1);
        } finally {
            await deleteTestSession(agb, session);
        }
    });

    test("getSession returns session detail", async () => {
        const session = await createTestSession(agb);

        try {
            const result = await agb.getSession(session.getSessionId());
            expect(result.success).toBe(true);
            expect(result.data).toBeDefined();
            expect(result.data!.sessionId).toBe(session.getSessionId());
            expect(result.data!.appInstanceId).toBeTruthy();
            expect(result.data!.resourceId).toBeTruthy();
        } finally {
            await deleteTestSession(agb, session);
        }
    });
});
