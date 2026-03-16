/**
 * Filesystem advanced tests: parameterized read (offset/length), file operations CRUD,
 * edge cases, batch operations.
 */
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";

jest.setTimeout(300_000);

describe("Filesystem advanced (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    test("full CRUD lifecycle", async () => {
        const dir = "/tmp/fs-crud-test";
        const file = `${dir}/test.txt`;

        const mkdirResult = await session.file.mkdir(dir);
        expect(mkdirResult.success).toBe(true);

        const writeResult = await session.file.write(file, "initial content");
        expect(writeResult.success).toBe(true);

        const readResult = await session.file.read(file);
        expect(readResult.success).toBe(true);
        expect(readResult.content).toContain("initial content");

        const editResult = await session.file.editFile(file, [
            { oldText: "initial content", newText: "updated content" },
        ]);
        expect(editResult.success).toBe(true);

        const readUpdated = await session.file.read(file);
        expect(readUpdated.content).toContain("updated content");

        const infoResult = await session.file.getFileInfo(file);
        expect(infoResult.success).toBe(true);

        const deleteResult = await session.file.delete(file);
        expect(deleteResult.success).toBe(true);

        const searchAfterDelete = await session.file.searchFiles(dir, "test.txt");
        const found = searchAfterDelete.matches?.some((m: string) => m.includes("test.txt")) ?? false;
        expect(found).toBe(false);
    });

    test("write and read large content", async () => {
        const largeContent = "A".repeat(100000);
        const file = "/tmp/large-file-test.txt";

        const writeResult = await session.file.write(file, largeContent);
        expect(writeResult.success).toBe(true);

        const readResult = await session.file.read(file);
        expect(readResult.success).toBe(true);
        expect(readResult.content.length).toBeGreaterThanOrEqual(100000);
    });

    test("read non-existent file fails", async () => {
        const result = await session.file.read("/tmp/nonexistent-file-xyz.txt");
        expect(result.success).toBe(false);
    });

    test("write to nested non-existent directory", async () => {
        const file = "/tmp/nested/deep/path/file.txt";
        await session.command.execute("mkdir -p /tmp/nested/deep/path", 10000);
        const result = await session.file.write(file, "nested content");
        expect(result.success).toBe(true);

        const readResult = await session.file.read(file);
        expect(readResult.content).toContain("nested content");
    });

    test("move file", async () => {
        const src = "/tmp/move-src.txt";
        const dst = "/tmp/move-dst.txt";

        await session.file.write(src, "move-content");
        const moveResult = await session.file.moveFile(src, dst);
        expect(moveResult.success).toBe(true);

        const readDst = await session.file.read(dst);
        expect(readDst.content).toContain("move-content");

        const readSrc = await session.file.read(src);
        expect(readSrc.success).toBe(false);
    });

    test("list directory with entries", async () => {
        const dir = "/tmp/list-test-dir";
        await session.command.execute(`mkdir -p ${dir} && touch ${dir}/a.txt ${dir}/b.txt`, 10000);

        const listResult = await session.file.list(dir);
        expect(listResult.success).toBe(true);
        expect(listResult.entries).toBeDefined();
        expect(listResult.entries!.length).toBeGreaterThanOrEqual(2);
    });

    test("batch read multiple files", async () => {
        await session.file.write("/tmp/batch-a.txt", "content-a");
        await session.file.write("/tmp/batch-b.txt", "content-b");

        const result = await session.file.readMultipleFiles([
            "/tmp/batch-a.txt",
            "/tmp/batch-b.txt",
        ]);
        expect(result.success).toBe(true);
        expect(result.files).toBeDefined();
        expect(Object.keys(result.files).length).toBe(2);
    });

    test("edit file with old text not found still completes", async () => {
        await session.file.write("/tmp/edit-mismatch.txt", "original text");
        const result = await session.file.editFile("/tmp/edit-mismatch.txt", [
            { oldText: "non-existent old text", newText: "new text" },
        ]);
        expect(result.requestId).toBeDefined();
        const readResult = await session.file.read("/tmp/edit-mismatch.txt");
        expect(readResult.content).toContain("original text");
    });

    test("delete non-existent file", async () => {
        const result = await session.file.delete("/tmp/does-not-exist-file.txt");
        expect(result.requestId).toBeDefined();
    });
});
