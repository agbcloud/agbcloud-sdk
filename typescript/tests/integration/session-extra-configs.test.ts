/**
 * Integration tests for session extra configurations.
 * Reference: python/tests/integration/test_session_extra_configs_integration.py
 */
import { createAGB, deleteTestSession, getApiKey } from "./setup";
import { AGB } from "../../src/agb";
import { CreateSessionParams } from "../../src/session-params";
import type { Session } from "../../src/session";

jest.setTimeout(300_000);

describe("Session extra configs (integration)", () => {
    let agb: AGB;

    beforeAll(() => {
        agb = createAGB();
    });

    test("create session with labels verification", async () => {
        const params = new CreateSessionParams({
            imageId: "agb-code-space-2",
            labels: { env: "integration-test", team: "sdk" },
        });

        const result = await agb.create(params);
        expect(result.success).toBe(true);
        expect(result.session).toBeDefined();

        const session = result.session!;
        try {
            const setResult = await session.setLabels({ env: "integration-test", team: "sdk" });
            expect(setResult.success).toBe(true);

            const getResult = await session.getLabels();
            expect(getResult.success).toBe(true);
            if (getResult.data && typeof getResult.data === "object") {
                const labels = getResult.data as Record<string, string>;
                expect(labels.env).toBe("integration-test");
                expect(labels.team).toBe("sdk");
            }
        } finally {
            await deleteTestSession(agb, session);
        }
    });

    test("create session with basic config", async () => {
        const params = new CreateSessionParams({
            imageId: "agb-code-space-2",
        });

        const result = await agb.create(params);
        expect(result.success).toBe(true);
        expect(result.session).toBeDefined();

        const session = result.session!;
        try {
            const info = await session.info();
            expect(info.success).toBe(true);
            expect(info.data).toBeDefined();
        } finally {
            await deleteTestSession(agb, session);
        }
    });
});
