/**
 * Integration tests for multi-page list queries (session list + context list pagination).
 * Reference: python/tests/integration/test_agb_list_integration.py
 * Reference: TypeScript context-pagination tests
 */
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";

jest.setTimeout(300_000);

describe("List pagination (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    test("list sessions returns array", async () => {
        const result = await agb.list();
        expect(result.success).toBe(true);
        expect(Array.isArray(result.sessionIds)).toBe(true);
        expect(result.sessionIds.length).toBeGreaterThanOrEqual(1);
    });

    test("list sessions with pagination (maxResults=1)", async () => {
        const result = await agb.list(undefined, undefined, 1);
        expect(result.success).toBe(true);
        expect(result.sessionIds.length).toBeLessThanOrEqual(1);
    });

    test("list sessions with non-matching label returns empty", async () => {
        const result = await agb.list({ nonexistent_key: "nonexistent_value" });
        expect(result.success).toBe(true);
        expect(result.sessionIds.length).toBe(0);
    });

    test("list contexts with default pagination", async () => {
        const result = await agb.context.list();
        expect(result.success).toBe(true);
        expect(Array.isArray(result.contexts)).toBe(true);
    });

    test("list contexts with small maxResults", async () => {
        const result = await agb.context.list({ maxResults: 2 });
        expect(result.success).toBe(true);
        expect(result.contexts.length).toBeLessThanOrEqual(2);
    });

    test("list contexts with larger maxResults", async () => {
        const result = await agb.context.list({ maxResults: 50 });
        expect(result.success).toBe(true);
        expect(Array.isArray(result.contexts)).toBe(true);
    });

    test("paginate through all sessions", async () => {
        const baseline = await agb.list();
        expect(baseline.success).toBe(true);
        const totalCount = baseline.totalCount;
        expect(totalCount).toBeGreaterThanOrEqual(1);

        const allSessions: string[] = [];
        let page = 1;
        const limit = 2;

        while (page <= 50) {
            const result = await agb.list(undefined, page, limit);
            if (!result.success) break;

            allSessions.push(...result.sessionIds);

            if (result.sessionIds.length < limit) break;
            page++;
        }

        expect(allSessions.length).toBe(totalCount);
    });
});
