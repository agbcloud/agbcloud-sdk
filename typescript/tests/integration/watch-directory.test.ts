/**
 * Integration tests for directory watching (watchDir).
 * Reference: python/tests/integration/test_agb_watch_directory.py
 */
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import type { FileChangeEvent } from "../../src/types/api-response";

jest.setTimeout(300_000);

function sleep(ms: number) {
    return new Promise((r) => setTimeout(r, ms));
}

describe("Watch directory (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    test("detects file creation events", async () => {
        const testDir = `/tmp/watch_test_${Date.now()}`;
        await session.file.mkdir(testDir);

        const detected: FileChangeEvent[] = [];
        const watcher = session.file.watchDir(
            testDir,
            (events) => detected.push(...events),
            500,
        );

        try {
            await sleep(1000);

            await session.file.write(`${testDir}/a.txt`, "content-a");
            await sleep(2000);

            await session.file.write(`${testDir}/b.txt`, "content-b");
            await sleep(2000);

            expect(detected.length).toBeGreaterThanOrEqual(1);
            const paths = detected.map((e) => e.path);
            const hasFileEvent = paths.some(
                (p) => p.includes("a.txt") || p.includes("b.txt"),
            );
            expect(hasFileEvent).toBe(true);
        } finally {
            watcher.stop();
            await session.command.execute(`rm -rf ${testDir}`, 10000);
        }
    });

    test("detects file modification events", async () => {
        const testDir = `/tmp/watch_mod_${Date.now()}`;
        await session.file.mkdir(testDir);
        await session.file.write(`${testDir}/mod.txt`, "initial");

        const detected: FileChangeEvent[] = [];
        const watcher = session.file.watchDir(
            testDir,
            (events) => detected.push(...events),
            500,
        );

        try {
            await sleep(1000);

            for (let i = 1; i <= 3; i++) {
                await session.file.write(`${testDir}/mod.txt`, `version ${i}`);
                await sleep(1500);
            }

            await sleep(2000);
            expect(detected.length).toBeGreaterThanOrEqual(2);
        } finally {
            watcher.stop();
            await session.command.execute(`rm -rf ${testDir}`, 10000);
        }
    });
});
