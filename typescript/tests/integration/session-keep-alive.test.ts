/**
 * Integration test for Session.keepAlive.
 *
 * This test validates that calling keepAlive refreshes the backend idle timer.
 *
 * Strategy (no mocks, end-to-end):
 * - Create 2 sessions with the same idle_release_timeout.
 * - Call keepAlive on one session halfway through.
 * - Wait until the control session is released.
 * - Assert the refreshed session is still alive at that moment.
 *
 * Notes:
 * - Requires a real AGB_API_KEY environment variable.
 * - Uses getStatus polling to observe lifecycle.
 */
import { createAGB } from "./setup";
import { CreateSessionParams } from "../../src/session-params";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";

jest.setTimeout(300_000);

function sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

function maskSecret(secret: string, visible: number = 4): string {
    if (!secret) return "";
    if (secret.length <= visible) return "*".repeat(secret.length);
    return "*".repeat(secret.length - visible) + secret.slice(-visible);
}

function isNotFoundStatusResult(statusResult: {
    success: boolean;
    errorMessage?: string;
    code?: string;
}): boolean {
    if (statusResult.success) return false;
    const errorMessage = (statusResult.errorMessage || "").toLowerCase();
    const code = (statusResult.code || "").toLowerCase();
    return code.includes("notfound") || errorMessage.includes("not found");
}

function isTerminalStatus(statusResult: {
    success: boolean;
    status?: string;
    errorMessage?: string;
    code?: string;
}): boolean {
    if (!statusResult.success) {
        return isNotFoundStatusResult(statusResult);
    }
    return ["FINISH", "DELETING", "DELETED"].includes(statusResult.status || "");
}

describe("Session.keepAlive (integration)", () => {
    let agb: AGB;

    beforeAll(() => {
        agb = createAGB();
    });

    test("keepAlive resets idle timer", async () => {
        const idleReleaseTimeout = 60; // seconds
        const maxOverSeconds = 60; // control session must be released within timeout + 60s
        const pollInterval = 15; // seconds
        const imageId = "agb-browser-use-1";

        const apiKey = process.env.AGB_API_KEY || "";
        console.log("api_key =", maskSecret(apiKey));
        console.log(
            `Creating 2 sessions with image_id=${imageId}, idle_release_timeout=${idleReleaseTimeout}s`
        );

        let controlSession: Session | null = null;
        let refreshedSession: Session | null = null;

        const startTime = Date.now();

        try {
            const commonLabels = { test: "session-keep-alive", sdk: "typescript" };

            // Create control session
            const controlParams = new CreateSessionParams({
                imageId,
                idleReleaseTimeout,
                labels: { ...commonLabels, role: "control" },
            });
            const controlResult = await agb.create(controlParams);
            expect(controlResult.success).toBe(true);
            expect(controlResult.session).toBeDefined();
            controlSession = controlResult.session!;

            // Create refreshed session
            const refreshedParams = new CreateSessionParams({
                imageId,
                idleReleaseTimeout,
                labels: { ...commonLabels, role: "refreshed" },
            });
            const refreshedResult = await agb.create(refreshedParams);
            expect(refreshedResult.success).toBe(true);
            expect(refreshedResult.session).toBeDefined();
            refreshedSession = refreshedResult.session!;

            console.log(`✅ Control session: ${controlSession.getSessionId()}`);
            console.log(`✅ Refreshed session: ${refreshedSession.getSessionId()}`);

            // Wait until halfway through, then refresh the idle timer for refreshed session
            await sleep((idleReleaseTimeout / 2 + 15) * 1000);
            const keepAliveResult = await refreshedSession.keepAlive();
            expect(keepAliveResult.success).toBe(true);
            console.log(
                `✅ Called keepAlive on refreshed session at ${idleReleaseTimeout / 2}s`
            );

            const deadline = startTime + (idleReleaseTimeout + maxOverSeconds) * 1000;
            let controlReleasedAt: number | null = null;

            // Poll until control session is released
            while (Date.now() < deadline) {
                const controlStatus = await controlSession.getStatus();
                const refreshedStatus = await refreshedSession.getStatus();

                // Check if control session is released
                if (isTerminalStatus(controlStatus)) {
                    controlReleasedAt = Date.now();
                    // At this point, refreshed session should still be alive
                    expect(isTerminalStatus(refreshedStatus)).toBe(false);
                    if (isTerminalStatus(refreshedStatus)) {
                        throw new Error(
                            "Refreshed session was released no later than control session; " +
                            "keepAlive did not extend idle timer as expected"
                        );
                    }
                    const elapsed = (controlReleasedAt - startTime) / 1000;
                    console.log(
                        `✅ Control session released while refreshed session still alive, ` +
                        `elapsed=${elapsed.toFixed(2)}s`
                    );
                    return;
                }

                // Check if refreshed session was released before control session (unexpected)
                if (isTerminalStatus(refreshedStatus)) {
                    throw new Error(
                        "Refreshed session was released before control session; " +
                        "keepAlive may have failed"
                    );
                }

                await sleep(pollInterval * 1000);
            }

            // If we reach here, test failed due to timeout
            throw new Error(
                `Timeout after ${maxOverSeconds}s: control session was not released`
            );
        } finally {
            // Best-effort cleanup
            for (const s of [refreshedSession, controlSession]) {
                if (!s) continue;
                try {
                    const statusFinal = await s.getStatus();
                    if (!isTerminalStatus(statusFinal)) {
                        await agb.delete(s);
                    }
                } catch {
                    // Ignore cleanup errors
                }
            }
        }
    });
});
