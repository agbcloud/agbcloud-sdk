/**
 * Context file URL tests: upload URL, download URL generation, list/delete files.
 * Note: Actual PUT/GET to presigned URLs may fail in non-VPN environments.
 */
import { createAGB } from "./setup";
import type { AGB } from "../../src/agb";
import { Context } from "../../src/context";

jest.setTimeout(300_000);

describe("Context file URLs (integration)", () => {
    let agb: AGB;
    let contextId: string;
    let contextName: string;

    beforeAll(async () => {
        agb = createAGB();
        contextName = `ts-file-url-${Date.now()}`;
        const ctxRes = await agb.context.get(contextName, true);
        expect(ctxRes.success).toBe(true);
        contextId = ctxRes.context!.id;
    });

    afterAll(async () => {
        if (contextId) {
            await agb.context.delete(new Context(contextId, contextName));
        }
    });

    test("get upload URL returns valid URL", async () => {
        const testPath = "/tmp/integration_upload_test.txt";
        const result = await agb.context.getFileUploadUrl(contextId, testPath);
        expect(result.success).toBe(true);
        expect(result.requestId).toBeDefined();
        expect(typeof result.url).toBe("string");
        expect(result.url!.length).toBeGreaterThan(0);
    });

    test("get download URL returns valid URL or fails gracefully for non-existent file", async () => {
        const testPath = "/tmp/nonexistent_file_test.txt";
        const result = await agb.context.getFileDownloadUrl(contextId, testPath);
        expect(result.requestId).toBeDefined();
    });

    test("list files returns result", async () => {
        const result = await agb.context.listFiles(contextId, "/tmp", 1, 50);
        expect(result.success).toBe(true);
        expect(result.requestId).toBeDefined();
    });

    test("delete file on non-existent path", async () => {
        const result = await agb.context.deleteFile(contextId, "/tmp/no_such_file.txt");
        expect(result.requestId).toBeDefined();
    });

    test("get upload URL with empty contextId fails", async () => {
        const result = await agb.context.getFileUploadUrl("", "/tmp/test.txt");
        expect(result.success).toBe(false);
    });

    test("get download URL with empty filePath fails", async () => {
        const result = await agb.context.getFileDownloadUrl(contextId, "");
        expect(result.success).toBe(false);
    });

    test("get upload URL with empty filePath fails", async () => {
        const result = await agb.context.getFileUploadUrl(contextId, "");
        expect(result.success).toBe(false);
    });
});
