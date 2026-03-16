/**
 * Integration tests for session getLink functionality.
 * Reference: python/tests/integration/test_agb_get_link.py
 */
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";

jest.setTimeout(300_000);

describe("Session getLink (integration)", () => {
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
        if (result.success) {
            expect(result.data).toBeDefined();
            expect(typeof result.data).toBe("string");
        }
    });

    test("getLink with protocol type", async () => {
        const result = await session.getLink("https");
        expect(result.requestId).toBeDefined();
    });

    test("getLink with valid port", async () => {
        const result = await session.getLink(undefined, 30100);
        expect(result.requestId).toBeDefined();
    });

    test("getLink with boundary port 30100", async () => {
        const result = await session.getLink(undefined, 30100);
        expect(result.requestId).toBeDefined();
    });

    test("getLink with boundary port 30199", async () => {
        const result = await session.getLink(undefined, 30199);
        expect(result.requestId).toBeDefined();
    });
});
