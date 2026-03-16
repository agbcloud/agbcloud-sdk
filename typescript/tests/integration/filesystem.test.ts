/**
 * Integration tests for the FileSystem module.
 */
import { AGB } from "../../src/agb";
import type { Session } from "../../src/session";
import { createAGB, createTestSession, deleteTestSession } from "./setup";

jest.setTimeout(300_000);

describe("FileSystem (integration)", () => {
    let agb: AGB;
    let session: Session;
    let testDir: string;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);

        testDir = `/tmp/agb_ts_fs_test_${Date.now()}`;
        const mkdirResult = await session.file.mkdir(testDir);
        if (!mkdirResult.success) {
            throw new Error(`Failed to create test dir: ${mkdirResult.errorMessage}`);
        }
    });

    afterAll(async () => {
        try {
            await session.command.execute(`rm -rf ${testDir}`, 10000);
        } catch { /* best-effort cleanup */ }
        await deleteTestSession(agb, session);
    });

    test("create directory", async () => {
        const subDir = `${testDir}/subdir_${Date.now()}`;
        const result = await session.file.mkdir(subDir);
        expect(result.success).toBe(true);
    });

    test("write and read file", async () => {
        const path = `${testDir}/test.txt`;
        const content = `Hello AGB TS!\nTimestamp: ${Date.now()}\n`;

        const writeResult = await session.file.write(path, content);
        expect(writeResult.success).toBe(true);

        const readResult = await session.file.read(path);
        expect(readResult.success).toBe(true);
        expect((readResult as { content: string }).content).toBe(content);
    });

    test("list empty directory", async () => {
        const emptyDir = `${testDir}/empty_${Date.now()}`;
        await session.file.mkdir(emptyDir);

        const result = await session.file.list(emptyDir);
        expect(result.success).toBe(true);
        expect(result.entries.length).toBe(0);
    });

    test("list directory with entries", async () => {
        const dir = `${testDir}/list_test_${Date.now()}`;
        await session.file.mkdir(dir);
        await session.file.write(`${dir}/a.txt`, "a");
        await session.file.mkdir(`${dir}/subdir`);

        const result = await session.file.list(dir);
        expect(result.success).toBe(true);
        expect(result.entries.length).toBe(2);

        const names = result.entries.map((e) => e.name);
        expect(names).toContain("a.txt");
        expect(names).toContain("subdir");
    });

    test("get file info", async () => {
        const path = `${testDir}/info.txt`;
        await session.file.write(path, "info content\n");

        const result = await session.file.getFileInfo(path);
        expect(result.success).toBe(true);
        expect(result.fileInfo).toBeDefined();
        expect(Number(result.fileInfo!.size)).toBeGreaterThan(0);
    });

    test("edit file", async () => {
        const path = `${testDir}/edit.txt`;
        await session.file.write(path, "old text here");

        const editResult = await session.file.editFile(path, [
            { oldText: "old text", newText: "new text" },
        ]);
        expect(editResult.success).toBe(true);

        const readResult = await session.file.read(path);
        expect(readResult.success).toBe(true);
        expect((readResult as { content: string }).content).toContain("new text");
    });

    test("move file", async () => {
        const src = `${testDir}/move_src.txt`;
        const dst = `${testDir}/move_dst.txt`;
        await session.file.write(src, "move me");

        const moveResult = await session.file.moveFile(src, dst);
        expect(moveResult.success).toBe(true);

        const readResult = await session.file.read(dst);
        expect(readResult.success).toBe(true);
        expect((readResult as { content: string }).content).toContain("move me");
    });

    test("delete file", async () => {
        const path = `${testDir}/delete_me.txt`;
        await session.file.write(path, "to be deleted");

        const delResult = await session.file.delete(path);
        expect(delResult.success).toBe(true);

        const readResult = await session.file.read(path);
        expect(readResult.success).toBe(false);
    });

    test("search files", async () => {
        const dir = `${testDir}/search_${Date.now()}`;
        await session.file.mkdir(dir);
        await session.file.write(`${dir}/match_abc.txt`, "content");
        await session.file.write(`${dir}/other.log`, "content");

        const result = await session.file.searchFiles(dir, "match");
        expect(result.success).toBe(true);
        expect(result.matches).toBeDefined();
    });

    test("read multiple files", async () => {
        const p1 = `${testDir}/multi1.txt`;
        const p2 = `${testDir}/multi2.txt`;
        await session.file.write(p1, "content1");
        await session.file.write(p2, "content2");

        const result = await session.file.readMultipleFiles([p1, p2]);
        expect(result.success).toBe(true);
        expect(Object.keys(result.files).length).toBe(2);
    });

    test("write large file (multi-chunk)", async () => {
        const path = `${testDir}/large.txt`;
        const content = "A".repeat(100_000);

        const writeResult = await session.file.write(path, content);
        expect(writeResult.success).toBe(true);

        const readResult = await session.file.read(path);
        expect(readResult.success).toBe(true);
        expect((readResult as { content: string }).content.length).toBe(100_000);
    });
});
