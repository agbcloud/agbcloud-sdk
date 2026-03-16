import { FileSystem } from "../../src/modules/filesystem";

const mockSession = {
    getApiKey: () => "test-key",
    getSessionId: () => "test-session",
    getClient: () => ({}),
};

describe("FileSystem", () => {
    let fs: FileSystem;
    let spy: jest.SpyInstance;

    beforeEach(() => {
        fs = new FileSystem(mockSession);
        spy = jest.spyOn(fs as any, "callMcpTool");
    });

    afterEach(() => {
        spy.mockRestore();
    });

    describe("createDirectory", () => {
        test("success", async () => {
            spy.mockResolvedValue({
                requestId: "req-1",
                success: true,
                data: true,
            });
            const result = await fs.createDirectory("/foo/bar");
            expect(result.success).toBe(true);
            expect(result.data).toBe(true);
            expect(result.requestId).toBe("req-1");
            expect(spy).toHaveBeenCalledWith("create_directory", { path: "/foo/bar" });
        });

        test("failure", async () => {
            spy.mockResolvedValue({
                requestId: "req-2",
                success: false,
                errorMessage: "Permission denied",
            });
            const result = await fs.createDirectory("/foo/bar");
            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("Permission denied");
        });

        test("exception", async () => {
            spy.mockRejectedValue(new Error("Network error"));
            const result = await fs.createDirectory("/foo/bar");
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("Network error");
        });
    });

    describe("deleteFile", () => {
        test("success", async () => {
            spy.mockResolvedValue({
                requestId: "req-3",
                success: true,
                data: true,
            });
            const result = await fs.deleteFile("/foo/file.txt");
            expect(result.success).toBe(true);
            expect(spy).toHaveBeenCalledWith("delete_file", { path: "/foo/file.txt" });
        });

        test("failure", async () => {
            spy.mockResolvedValue({
                requestId: "req-4",
                success: false,
                errorMessage: "File not found",
            });
            const result = await fs.deleteFile("/foo/missing.txt");
            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("File not found");
        });
    });

    describe("editFile", () => {
        test("success", async () => {
            spy.mockResolvedValue({
                requestId: "req-5",
                success: true,
                data: true,
            });
            const edits = [{ oldText: "old", newText: "new" }];
            const result = await fs.editFile("/foo/file.txt", edits);
            expect(result.success).toBe(true);
            expect(spy).toHaveBeenCalledWith("edit_file", {
                path: "/foo/file.txt",
                edits,
                dryRun: false,
            });
        });

        test("dry run", async () => {
            spy.mockResolvedValue({
                requestId: "req-6",
                success: true,
                data: true,
            });
            const edits = [{ oldText: "a", newText: "b" }];
            const result = await fs.editFile("/foo/file.txt", edits, true);
            expect(result.success).toBe(true);
            expect(spy).toHaveBeenCalledWith("edit_file", {
                path: "/foo/file.txt",
                edits,
                dryRun: true,
            });
        });

        test("failure", async () => {
            spy.mockResolvedValue({
                requestId: "req-7",
                success: false,
                errorMessage: "Edit failed",
            });
            const result = await fs.editFile("/foo/file.txt", [
                { oldText: "x", newText: "y" },
            ]);
            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("Edit failed");
        });
    });

    describe("getFileInfo", () => {
        test("success - parsing file info string", async () => {
            const fileInfoStr = `size: 1024
isDirectory: false
modified: 1234567890`;
            spy.mockResolvedValue({
                requestId: "req-8",
                success: true,
                data: fileInfoStr,
            });
            const result = await fs.getFileInfo("/foo/file.txt");
            expect(result.success).toBe(true);
            expect(result.fileInfo).toBeDefined();
            expect(result.fileInfo?.size).toBe(1024);
            expect(result.fileInfo?.isDirectory).toBe(false);
        });

        test("success - parses boolean true/false", async () => {
            spy.mockResolvedValue({
                requestId: "req-8b",
                success: true,
                data: "isDirectory: true\nreadable: false",
            });
            const result = await fs.getFileInfo("/foo/dir");
            expect(result.success).toBe(true);
            expect(result.fileInfo?.isDirectory).toBe(true);
        });

        test("failure", async () => {
            spy.mockResolvedValue({
                requestId: "req-9",
                success: false,
                errorMessage: "Path not found",
            });
            const result = await fs.getFileInfo("/foo/missing");
            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("Path not found");
        });
    });

    describe("listDirectory", () => {
        test("success - parsing [DIR]/[FILE] format", async () => {
            const listing = `[DIR] subdir
[FILE] file1.txt
[FILE] file2.txt`;
            spy.mockResolvedValue({
                requestId: "req-10",
                success: true,
                data: listing,
            });
            const result = await fs.listDirectory("/foo");
            expect(result.success).toBe(true);
            expect(result.entries).toEqual([
                { type: "directory", name: "subdir" },
                { type: "file", name: "file1.txt" },
                { type: "file", name: "file2.txt" },
            ]);
        });

        test("failure", async () => {
            spy.mockResolvedValue({
                requestId: "req-11",
                success: false,
                errorMessage: "Not a directory",
            });
            const result = await fs.listDirectory("/foo/file.txt");
            expect(result.success).toBe(false);
            expect(result.entries).toEqual([]);
            expect(result.errorMessage).toBe("Not a directory");
        });
    });

    describe("moveFile", () => {
        test("success", async () => {
            spy.mockResolvedValue({
                requestId: "req-12",
                success: true,
                data: true,
            });
            const result = await fs.moveFile("/foo/a.txt", "/bar/b.txt");
            expect(result.success).toBe(true);
            expect(spy).toHaveBeenCalledWith("move_file", {
                source: "/foo/a.txt",
                destination: "/bar/b.txt",
            });
        });

        test("failure", async () => {
            spy.mockResolvedValue({
                requestId: "req-13",
                success: false,
                errorMessage: "Move failed",
            });
            const result = await fs.moveFile("/foo/a.txt", "/bar/b.txt");
            expect(result.success).toBe(false);
        });
    });

    describe("readFile", () => {
        test("text format - getFileInfo then readFileChunk", async () => {
            spy
                .mockResolvedValueOnce({
                    requestId: "req-14",
                    success: true,
                    data: "path: /foo/file.txt\nsize: 12\nisDirectory: false",
                })
                .mockResolvedValueOnce({
                    requestId: "req-15",
                    success: true,
                    data: "hello world!",
                });
            const result = await fs.readFile("/foo/file.txt", { format: "text" });
            expect(result.success).toBe(true);
            expect((result as any).content).toBe("hello world!");
            expect(spy).toHaveBeenCalledTimes(2);
            expect(spy).toHaveBeenNthCalledWith(1, "get_file_info", {
                path: "/foo/file.txt",
            });
            expect(spy).toHaveBeenNthCalledWith(2, "read_file", {
                path: "/foo/file.txt",
                offset: 0,
                length: 12,
            });
        });

        test("text format - multiple chunks for large file", async () => {
            const chunkSize = 60 * 1024;
            const chunk1 = "a".repeat(chunkSize);
            const chunk2 = "b".repeat(100);
            spy
                .mockResolvedValueOnce({
                    requestId: "req-16",
                    success: true,
                    data: `path: /foo/big.txt\nsize: ${chunkSize + 100}\nisDirectory: false`,
                })
                .mockResolvedValueOnce({
                    requestId: "req-17",
                    success: true,
                    data: chunk1,
                })
                .mockResolvedValueOnce({
                    requestId: "req-18",
                    success: true,
                    data: chunk2,
                });
            const result = await fs.readFile("/foo/big.txt", { format: "text" });
            expect(result.success).toBe(true);
            expect((result as any).content).toBe(chunk1 + chunk2);
            expect(spy).toHaveBeenCalledTimes(3);
        });

        test("bytes format", async () => {
            const base64Content = Buffer.from("hello").toString("base64");
            spy
                .mockResolvedValueOnce({
                    requestId: "req-19",
                    success: true,
                    data: "path: /foo/bin\nsize: 5\nisDirectory: false",
                })
                .mockResolvedValueOnce({
                    requestId: "req-20",
                    success: true,
                    data: base64Content,
                });
            const result = await fs.readFile("/foo/bin", { format: "bytes" });
            expect(result.success).toBe(true);
            expect(Buffer.isBuffer((result as any).content)).toBe(true);
            expect((result as any).content.toString()).toBe("hello");
        });

        test("not found - getFileInfo fails", async () => {
            spy.mockResolvedValueOnce({
                requestId: "req-21",
                success: false,
                errorMessage: "File not found",
            });
            const result = await fs.readFile("/foo/missing.txt", { format: "text" });
            expect(result.success).toBe(false);
            expect((result as any).content).toBe("");
            expect(result.errorMessage).toBe("File not found");
        });

        test("is directory - returns error", async () => {
            spy.mockResolvedValueOnce({
                requestId: "req-22",
                success: true,
                data: "path: /foo/dir\nsize: 0\nisDirectory: true",
            });
            const result = await fs.readFile("/foo/dir", { format: "text" });
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("directory");
        });

        test("empty file - text format", async () => {
            spy.mockResolvedValueOnce({
                requestId: "req-23",
                success: true,
                data: "path: /foo/empty.txt\nsize: 0\nisDirectory: false",
            });
            const result = await fs.readFile("/foo/empty.txt", { format: "text" });
            expect(result.success).toBe(true);
            expect((result as any).content).toBe("");
            expect(spy).toHaveBeenCalledTimes(1);
        });
    });

    describe("writeFile", () => {
        test("small content - single chunk", async () => {
            spy.mockResolvedValue({
                requestId: "req-24",
                success: true,
                data: true,
            });
            const result = await fs.writeFile("/foo/small.txt", "hello", "overwrite");
            expect(result.success).toBe(true);
            expect(spy).toHaveBeenCalledWith("write_file", {
                path: "/foo/small.txt",
                content: "hello",
                mode: "overwrite",
            });
        });

        test("large content - multiple chunks", async () => {
            const chunkSize = FileSystem.DEFAULT_CHUNK_SIZE;
            const content = "x".repeat(chunkSize + 1000);
            spy
                .mockResolvedValueOnce({
                    requestId: "req-25",
                    success: true,
                    data: true,
                })
                .mockResolvedValueOnce({
                    requestId: "req-26",
                    success: true,
                    data: true,
                });
            const result = await fs.writeFile("/foo/large.txt", content, "overwrite");
            expect(result.success).toBe(true);
            expect(spy).toHaveBeenCalledTimes(2);
            expect(spy).toHaveBeenNthCalledWith(1, "write_file", {
                path: "/foo/large.txt",
                content: content.slice(0, chunkSize),
                mode: "overwrite",
            });
            expect(spy).toHaveBeenNthCalledWith(2, "write_file", {
                path: "/foo/large.txt",
                content: content.slice(chunkSize),
                mode: "append",
            });
        });

        test("invalid mode - writeFileChunk returns error", async () => {
            const writeFileChunk = (fs as any).writeFileChunk.bind(fs);
            const result = await writeFileChunk(
                "/foo/file.txt",
                "content",
                "invalid" as any,
            );
            expect(result.success).toBe(false);
            expect(result.errorMessage).toContain("Invalid write mode");
            expect(spy).not.toHaveBeenCalled();
        });
    });

    describe("readMultipleFiles", () => {
        test("success", async () => {
            const data = `/foo/a.txt: content a
---
/foo/b.txt: content b
---`;
            spy.mockResolvedValue({
                requestId: "req-27",
                success: true,
                data,
            });
            const result = await fs.readMultipleFiles(["/foo/a.txt", "/foo/b.txt"]);
            expect(result.success).toBe(true);
            expect(result.files).toEqual({
                "/foo/a.txt": "content a",
                "/foo/b.txt": "content b",
            });
        });

        test("failure", async () => {
            spy.mockResolvedValue({
                requestId: "req-28",
                success: false,
                errorMessage: "Read failed",
            });
            const result = await fs.readMultipleFiles(["/foo/a.txt"]);
            expect(result.success).toBe(false);
            expect(result.files).toEqual({});
        });
    });

    describe("searchFiles", () => {
        test("success", async () => {
            spy.mockResolvedValue({
                requestId: "req-29",
                success: true,
                data: "/foo/a.txt\n/foo/b.txt",
            });
            const result = await fs.searchFiles("/foo", "*.txt");
            expect(result.success).toBe(true);
            expect(result.matches).toEqual(["/foo/a.txt", "/foo/b.txt"]);
        });

        test("success with excludePatterns", async () => {
            spy.mockResolvedValue({
                requestId: "req-29b",
                success: true,
                data: "/foo/a.txt",
            });
            const result = await fs.searchFiles("/foo", "*.txt", ["*.bak"]);
            expect(result.success).toBe(true);
            expect(spy).toHaveBeenCalledWith("search_files", {
                path: "/foo",
                pattern: "*.txt",
                excludePatterns: ["*.bak"],
            });
        });

        test("failure", async () => {
            spy.mockResolvedValue({
                requestId: "req-30",
                success: false,
                errorMessage: "Search failed",
            });
            const result = await fs.searchFiles("/foo", "*.txt");
            expect(result.success).toBe(false);
        });

        test("no matches - returns empty array", async () => {
            spy.mockResolvedValue({
                requestId: "req-30b",
                success: true,
                data: "No matches found",
            });
            const result = await fs.searchFiles("/foo", "*.xyz");
            expect(result.success).toBe(true);
            expect(result.matches).toEqual([]);
        });
    });

    describe("getFileChange", () => {
        test("success", async () => {
            const changeData = JSON.stringify([
                { path: "/foo/a.txt", eventType: "modified", pathType: "file" },
                { path: "/foo/b.txt", eventType: "created", pathType: "file" },
            ]);
            spy.mockResolvedValue({
                requestId: "req-31",
                success: true,
                data: changeData,
            });
            const result = await fs.getFileChange("/foo");
            expect(result.success).toBe(true);
            expect(result.events).toEqual([
                { eventType: "modified", path: "/foo/a.txt", pathType: "file" },
                { eventType: "created", path: "/foo/b.txt", pathType: "file" },
            ]);
            expect(result.rawData).toBeDefined();
        });

        test("failure", async () => {
            spy.mockResolvedValue({
                requestId: "req-32",
                success: false,
                errorMessage: "Get change failed",
            });
            const result = await fs.getFileChange("/foo");
            expect(result.success).toBe(false);
            expect(result.events).toEqual([]);
        });
    });

    describe("aliases", () => {
        test("read alias", async () => {
            spy
                .mockResolvedValueOnce({
                    requestId: "r1",
                    success: true,
                    data: "path: /f\nsize: 5\nisDirectory: false",
                })
                .mockResolvedValueOnce({
                    requestId: "r2",
                    success: true,
                    data: "hello",
                });
            const result = await fs.read("/f");
            expect(result.success).toBe(true);
            expect((result as any).content).toBe("hello");
        });

        test("write alias", async () => {
            spy.mockResolvedValue({ requestId: "r3", success: true, data: true });
            const result = await fs.write("/f", "data");
            expect(result.success).toBe(true);
        });

        test("list alias", async () => {
            spy.mockResolvedValue({
                requestId: "r4",
                success: true,
                data: "[FILE] a.txt",
            });
            const result = await fs.list("/dir");
            expect(result.success).toBe(true);
            expect(result.entries).toHaveLength(1);
        });

        test("ls alias", async () => {
            spy.mockResolvedValue({
                requestId: "r5",
                success: true,
                data: "[DIR] subdir",
            });
            const result = await fs.ls("/dir");
            expect(result.success).toBe(true);
            expect(result.entries[0].name).toBe("subdir");
        });

        test("delete alias", async () => {
            spy.mockResolvedValue({ requestId: "r6", success: true, data: true });
            const result = await fs.delete("/f");
            expect(result.success).toBe(true);
        });

        test("remove alias", async () => {
            spy.mockResolvedValue({ requestId: "r7", success: true, data: true });
            const result = await fs.remove("/f");
            expect(result.success).toBe(true);
        });

        test("rm alias", async () => {
            spy.mockResolvedValue({ requestId: "r8", success: true, data: true });
            const result = await fs.rm("/f");
            expect(result.success).toBe(true);
        });

        test("mkdir alias", async () => {
            spy.mockResolvedValue({ requestId: "r9", success: true, data: true });
            const result = await fs.mkdir("/dir");
            expect(result.success).toBe(true);
        });
    });

    describe("DEFAULT_CHUNK_SIZE", () => {
        test("exposes default chunk size", () => {
            expect(FileSystem.DEFAULT_CHUNK_SIZE).toBe(50 * 1024);
        });
    });
});
