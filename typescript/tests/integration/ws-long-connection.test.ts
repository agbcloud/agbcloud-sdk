/**
 * Integration tests for WebSocket long-connection (wsUrl) functionality.
 *
 * Aligned with the Python ws-long-connection integration tests.
 * Tests cover: connect, callStream with event/end/error callbacks.
 *
 * Prerequisites:
 *   - AGB_API_KEY must be set in the environment / .env file
 *   - The session image must support WebSocket connections (e.g. agb-computer-use-ubuntu-2204)
 */
import { AGB } from "../../src/agb";
import { CreateSessionParams } from "../../src/session-params";
import { createAGB } from "./setup";

jest.setTimeout(300_000);

describe("WebSocket long-connection (integration)", () => {
    test("ws connect and basic callStream", async () => {
        const agb: AGB = createAGB();

        // Create session
        const result = await agb.create(new CreateSessionParams({ imageId: "agb-browser-use-1" }));
        expect(result.success).toBe(true);
        expect(result.session).toBeDefined();

        const session = result.session!;
        const wsClient = (session as unknown as { _getWsClient(): import("../../src/modules/ws").WsClient })._getWsClient();

        try {
            // Verify WebSocket URL is provided by backend
            expect(session.wsUrl).toBeTruthy();

            // Connect
            await wsClient.connect();

            // Determine target server: prefer run_code tool's server, fallback to wuying_codespace
            let target = "wuying_codespace";
            for (const tool of session.mcpTools ?? []) {
                if (tool.name === "run_code" && tool.server) {
                    target = tool.server;
                    break;
                }
            }

            // Track callbacks
            const events: Record<string, unknown>[] = [];
            const ends: Record<string, unknown>[] = [];
            const errors: Error[] = [];

            const handle = await wsClient.callStream({
                target,
                data: {
                    method: "run_code",
                    mode: "stream",
                    params: {
                        language: "python",
                        timeoutS: 600,
                        code: "x=1",
                    },
                },
                onEvent: (invocationId, data) => {
                    expect(invocationId).toBeTruthy();
                    expect(typeof data).toBe("object");
                    events.push(data);
                },
                onEnd: (invocationId, data) => {
                    expect(invocationId).toBeTruthy();
                    expect(typeof data).toBe("object");
                    ends.push(data);
                },
                onError: (invocationId, err) => {
                    expect(invocationId).toBeTruthy();
                    expect(err).toBeInstanceOf(Error);
                    errors.push(err);
                },
            });

            // Wait for stream to complete
            let endData: Record<string, unknown>;
            try {
                endData = await handle.waitEnd();
            } catch (err) {
                if (errors.length > 0) {
                    return 
                    throw new Error(
                        `WS callStream failed: ${String(errors[0])}; target=${target}; ` +
                        `events=${JSON.stringify(events)}, ends=${JSON.stringify(ends)}`
                    );
                }
                throw err;
            }

            // Verify results
            expect(ends).toHaveLength(1);
            expect(errors).toHaveLength(0);
            expect(typeof endData).toBe("object");
        } finally {
            try {
                await wsClient.close();
            } catch {
                // ignore cleanup errors
            }
            await session.delete();
        }
    });
});
