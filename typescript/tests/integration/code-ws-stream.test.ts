/**
 * WebSocket streaming code execution integration tests for AGB SDK.
 *
 * Covers:
 *   - streamBeta=true real-time stdout/stderr callback streaming
 *   - Low-level callStream cancel via handle.cancel()
 */
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import { WsClient, WsCancelledError } from "../../src/modules/ws";


jest.setTimeout(300_000);

describe("WebSocket streaming code execution (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    // ---------------------------------------------------------------
    // Test 1 – stream_beta streaming E2E
    // ---------------------------------------------------------------

    test("streamBeta delivers real-time stdout chunks", async () => {
        const stdoutChunks: string[] = [];
        const stdoutTimes: number[] = [];
        const stderrChunks: string[] = [];
        const errors: unknown[] = [];

        const startT = performance.now();
        const result = await session.code.run(
            "import time\n" +
            "print('hello', flush=True)\n" +
            "time.sleep(1.0)\n" +
            "print(2, flush=True)\n",
            "python",
            60,
            {
                streamBeta: true,
                onStdout: (chunk) => {
                    stdoutChunks.push(chunk);
                    stdoutTimes.push(performance.now());
                },
                onStderr: (chunk) => stderrChunks.push(chunk),
                onError: (err) => errors.push(err),
            },
        );
        const endT = performance.now();

        // Basic assertions
        expect(errors).toEqual([]);
        expect(result.success).toBe(true);

        // At least two separate stdout events (one per print)
        expect(stdoutChunks.length).toBeGreaterThanOrEqual(2);

        // Total wall-clock time should reflect the sleep(1.0)
        expect(endT - startT).toBeGreaterThanOrEqual(1000);

        // Content check
        const joined = stdoutChunks.join("");
        expect(joined).toContain("hello");
        expect(joined).toContain("2");

        // Streaming timing: "2" should arrive ≥800ms after "hello"
        const helloIdx = stdoutChunks.findIndex((c) => c.includes("hello"));
        const twoIdx = stdoutChunks.findIndex((c) => c.includes("2"));
        expect(helloIdx).toBeGreaterThanOrEqual(0);
        expect(twoIdx).toBeGreaterThanOrEqual(0);

        const helloT = stdoutTimes[helloIdx];
        const twoT = stdoutTimes[twoIdx];
        expect(twoT - helloT).toBeGreaterThanOrEqual(800);
    });

    // ---------------------------------------------------------------
    // Test 2 – callStream cancel E2E
    // ---------------------------------------------------------------

    test("handle.cancel() aborts a running stream and raises WsCancelledError", async () => {
        expect(session.wsUrl).toBeTruthy();

        const wsClient = (
            session as unknown as { _getWsClient(): WsClient }
        )._getWsClient();
        await wsClient.connect();

        // Resolve target (mirrors resolveStreamTarget logic)
        let target = "wuying_codespace";
        for (const tool of session.mcpTools ?? []) {
            if (tool.name === "run_code" && tool.server) {
                target = tool.server;
                break;
            }
        }

        const events: Record<string, unknown>[] = [];
        const ends: Record<string, unknown>[] = [];
        const errors: Error[] = [];

        try {
            const handle = await wsClient.callStream({
                target,
                data: {
                    method: "run_code",
                    mode: "stream",
                    params: {
                        language: "python",
                        timeoutS: 60,
                        code:
                            "import time\n" +
                            "print(0, flush=True)\n" +
                            "time.sleep(10)\n" +
                            "print(1, flush=True)\n",
                    },
                },
                onEvent: (inv, data) => events.push(data),
                onEnd: (inv, data) => ends.push(data),
                onError: (inv, err) => errors.push(err),
            });

            // Give the server a moment to start, then cancel
            await new Promise((r) => setTimeout(r, 500));
            handle.cancel();

            const t0 = performance.now();
            // Cancel should raise WsCancelledError (aligns with Python behavior)
            await expect(handle.waitEnd()).rejects.toThrow(WsCancelledError);
            expect(performance.now() - t0).toBeLessThan(2000);

            expect(ends).toEqual([]);
            expect(errors).toHaveLength(1);
            expect(errors[0]).toBeInstanceOf(WsCancelledError);
        } finally {
            try {
                await wsClient.close();
            } catch {
                // ignore cleanup errors
            }
        }
    });
});
