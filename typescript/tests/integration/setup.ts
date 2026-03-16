/**
 * Shared setup for integration tests.
 *
 * Reads AGB_API_KEY and AGB_ENDPOINT from .env file (same as Python tests).
 */
import { AGB } from "../../src/agb";
import { CreateSessionParams } from "../../src/session-params";
import type { Session } from "../../src/session";
import { loadDotEnvWithFallback } from "../../src/config";

const DEFAULT_IMAGE_ID = "agb-code-space-2";

loadDotEnvWithFallback();

export function getApiKey(): string {
    const key = process.env.AGB_API_KEY;
    if (!key) {
        throw new Error(
            "AGB_API_KEY environment variable is not set. " +
            "Please set it before running integration tests.",
        );
    }
    return key;
}

export function createAGB(): AGB {
    return new AGB(getApiKey());
}

export async function createTestSession(
    agb: AGB,
    imageId: string = DEFAULT_IMAGE_ID,
): Promise<Session> {
    const params = new CreateSessionParams({ imageId });
    const result = await agb.create(params);
    if (!result.success || !result.session) {
        throw new Error(
            `Failed to create session: ${result.errorMessage ?? "unknown error"}`,
        );
    }
    return result.session;
}

export async function deleteTestSession(
    agb: AGB,
    session: Session,
): Promise<void> {
    try {
        await agb.delete(session);
    } catch (e) {
        console.warn(`Warning: failed to delete session: ${e}`);
    }
}

export { DEFAULT_IMAGE_ID };
