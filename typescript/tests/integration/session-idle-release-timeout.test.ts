/**
 * Integration test for SDK idle release timeout.
 *
 * Validates that a session created with `idleReleaseTimeout` will be
 * automatically released after being idle for long enough.
 *
 * Notes:
 * - Requires a real AGB_API_KEY environment variable.
 * - Uses session.getStatus() to observe the session lifecycle.
 */
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import { CreateSessionParams } from "../../src/session-params";
import { createAGB } from "./setup";

jest.setTimeout(300_000);

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const IMAGE_ID = "agb-browser-use-1";
const IDLE_RELEASE_TIMEOUT = 60;   // seconds – passed to the API
const MAX_OVER_SECONDS = 60;       // extra grace period after timeout before we fail
const POLL_INTERVAL_MS = 2_000;    // milliseconds between getStatus() calls

// ---------------------------------------------------------------------------
// Helpers (封装多次调用的公共逻辑)
// ---------------------------------------------------------------------------

const sleep = (ms: number): Promise<void> =>
    new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Return true when getStatus() indicates the session no longer exists.
 */
function isNotFoundStatus(statusResult: Awaited<ReturnType<Session["getStatus"]>>): boolean {
    if (statusResult.success) return false;
    const errorMessage = (statusResult.errorMessage ?? "").toLowerCase();
    const code = ((statusResult as any).code ?? "").toLowerCase();
    return code.includes("notfound") || errorMessage.includes("not found");
}

/**
 * Return true when getStatus() shows a terminal release state.
 */
function isReleasedStatus(statusResult: Awaited<ReturnType<Session["getStatus"]>>): boolean {
    if (!statusResult.success) return false;
    return ["FINISH", "DELETING", "DELETED"].includes(statusResult.status ?? "");
}

/**
 * Poll session.getStatus() until the session is released or the deadline (ms epoch) is reached.
 *
 * Returns an object describing whether the session was released and the last status result.
 */
async function pollUntilReleased(
    session: Session,
    deadlineMs: number,
    pollIntervalMs: number = POLL_INTERVAL_MS,
): Promise<{
    released: boolean;
    elapsedMs: number;
    lastStatus: Awaited<ReturnType<Session["getStatus"]>> | null;
}> {
    let lastStatus: Awaited<ReturnType<Session["getStatus"]>> | null = null;
    const startMs = Date.now();

    while (Date.now() < deadlineMs) {
        const status = await session.getStatus();
        lastStatus = status;
        if (isNotFoundStatus(status) || isReleasedStatus(status)) {
            return { released: true, elapsedMs: Date.now() - startMs, lastStatus };
        }
        await sleep(pollIntervalMs);
    }

    return { released: false, elapsedMs: Date.now() - startMs, lastStatus };
}

/**
 * Poll session.getStatus() until timeoutDeadlineMs and assert the session is NOT released early.
 */
async function assertNotReleasedBeforeTimeout(
    session: Session,
    timeoutDeadlineMs: number,
    pollIntervalMs: number = POLL_INTERVAL_MS,
): Promise<void> {
    while (true) {
        const now = Date.now();
        if (now >= timeoutDeadlineMs) break;

        const status = await session.getStatus();

        if (isNotFoundStatus(status)) {
            throw new Error(
                `Session was released too early: got NotFound before ${IDLE_RELEASE_TIMEOUT}s`,
            );
        }
        if (isReleasedStatus(status)) {
            throw new Error(
                `Session was released too early: status=${status.status} before ${IDLE_RELEASE_TIMEOUT}s`,
            );
        }

        const remaining = timeoutDeadlineMs - now;
        await sleep(Math.min(pollIntervalMs, Math.max(0, remaining)));
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("Session idle release timeout (integration)", () => {
    let agb: AGB;

    beforeAll(() => {
        agb = createAGB();
    });

    test("session is released after idle timeout within expected window", async () => {
        /**
         * Create a session with idleReleaseTimeout and verify it is released
         * within [idleReleaseTimeout, idleReleaseTimeout + maxOverSeconds].
         *
         * We only call getStatus() periodically and do not invoke any MCP tools,
         * so the environment is considered idle from the SDK side.
         */
        let session: Session | null = null;
        const startMs = Date.now();

        try {
            const params = new CreateSessionParams({
                imageId: IMAGE_ID,
                idleReleaseTimeout: IDLE_RELEASE_TIMEOUT,
                labels: {
                    test: "idle-release-timeout",
                    sdk: "typescript",
                },
            });
            const result = await agb.create(params);

            expect(result.success).toBe(true);
            expect(result.session).toBeDefined();
            session = result.session!;
            console.log(`✅ Session created: ${session.getSessionId()}`);

            // Phase 1: assert session is NOT released before the timeout
            const timeoutDeadlineMs = startMs + IDLE_RELEASE_TIMEOUT * 1_000;
            await assertNotReleasedBeforeTimeout(session, timeoutDeadlineMs);

            // Phase 2: wait for the session to be released within the grace period
            const releaseDeadlineMs = timeoutDeadlineMs + MAX_OVER_SECONDS * 1_000;
            const { released, elapsedMs, lastStatus } = await pollUntilReleased(
                session,
                releaseDeadlineMs,
            );

            if (!released) {
                const details = lastStatus
                    ? `lastSuccess=${lastStatus.success}, lastStatus=${lastStatus.status}, lastError=${lastStatus.errorMessage}`
                    : "no status available";
                throw new Error(
                    `Session was not released within expected time window ` +
                    `${IDLE_RELEASE_TIMEOUT}s~${IDLE_RELEASE_TIMEOUT + MAX_OVER_SECONDS}s. ${details}`,
                );
            }

            const elapsedSeconds = elapsedMs / 1_000;
            expect(elapsedSeconds).toBeGreaterThanOrEqual(0); // already past timeout phase

            if (isNotFoundStatus(lastStatus!)) {
                console.log(`✅ Session released: getStatus returned NotFound, elapsed=${(elapsedMs / 1_000).toFixed(2)}s`);
            } else {
                console.log(`✅ Session released: status=${lastStatus!.status}, elapsed=${(elapsedMs / 1_000).toFixed(2)}s`);
            }
        } finally {
            if (session !== null) {
                try {
                    const statusFinal = await session.getStatus();
                    if (!isNotFoundStatus(statusFinal) && !isReleasedStatus(statusFinal)) {
                        console.log("🧹 Cleaning up: deleting session explicitly...");
                        await agb.delete(session);
                    }
                } catch {
                    // ignore cleanup errors
                }
            }
        }
    });
});
