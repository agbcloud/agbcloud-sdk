/**
 * Integration tests for session metrics.
 * Reference: python/tests/integration/test_session_get_metrics_integration.py
 */
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";

jest.setTimeout(300_000);

describe("Session metrics (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    test("getMetrics returns structured data", async () => {
        const result = await session.getMetrics();
        expect(result.requestId).toBeDefined();
        expect(result.success).toBe(true);
        expect(result.metrics).toBeDefined();
    });

    test("getMetrics with custom timeout", async () => {
        const result = await session.getMetrics(60_000);
        expect(result.requestId).toBeDefined();
        expect(result.success).toBe(true);
    });

    test("getStatus returns session status", async () => {
        const result = await session.getStatus();
        expect(result.requestId).toBeDefined();
        expect(result.success).toBe(true);
        expect(result.status).toBeDefined();
    });
});
