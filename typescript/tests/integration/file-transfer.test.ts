/**
 * Integration tests for file transfer (upload/download) via presigned URLs.
 * Reference: python/tests/integration/test_file_transfer_integration.py
 */
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";

jest.setTimeout(300_000);

function sleep(ms: number) {
    return new Promise((r) => setTimeout(r, ms));
}

describe("File transfer (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb, "agb-code-space-2");
        await sleep(6000);
    });

    afterAll(async () => {
        await deleteTestSession(agb, session);
    });

    test("upload file via presigned URL", async () => {
        const contextPath = await session.file.transferPath();
        if (!contextPath) {
            console.warn("transferPath returned undefined – skipping upload test");
            return;
        }

        const remotePath = `${contextPath.replace(/\/+$/, "")}/upload_test.txt`;
        const testContent = "AGB FileTransfer upload integration test content.\n".repeat(10);

        const tmpFile = path.join(os.tmpdir(), `agb-upload-${Date.now()}.txt`);
        fs.writeFileSync(tmpFile, testContent, "utf8");

        try {
            const result = await session.file.upload(tmpFile, remotePath, {
                wait: true,
                waitTimeout: 120_000,
                pollInterval: 2000,
            });

            if (!result.success) {
                console.error("Upload failed:", JSON.stringify(result, null, 2));
            }
            expect(result.success).toBe(true);
            expect(result.bytesSent).toBeGreaterThan(0);

            const listResult = await session.file.list(contextPath.replace(/\/+$/, "") + "/");
            expect(listResult.success).toBe(true);
            const found = listResult.entries?.some((e) => e.name === "upload_test.txt");
            expect(found).toBe(true);

            const readResult = await session.file.read(remotePath);
            expect(readResult.success).toBe(true);
            expect(String(readResult.content).trim()).toBe(testContent.trim());
        } finally {
            try { fs.unlinkSync(tmpFile); } catch { /* ignore */ }
        }
    });

    test("download file via presigned URL", async () => {
        const contextPath = await session.file.transferPath();
        if (!contextPath) {
            console.warn("transferPath returned undefined – skipping download test");
            return;
        }

        const remotePath = `${contextPath.replace(/\/+$/, "")}/download_test.txt`;
        const testContent = "AGB FileTransfer download integration test content.\n".repeat(15);

        await session.file.mkdir(contextPath.replace(/\/+$/, "") + "/");
        const writeResult = await session.file.write(remotePath, testContent);
        expect(writeResult.success).toBe(true);

        const tmpFile = path.join(os.tmpdir(), `agb-download-${Date.now()}.txt`);

        try {
            const result = await session.file.download(remotePath, tmpFile, {
                overwrite: true,
                wait: true,
                waitTimeout: 120_000,
                pollInterval: 2000,
            });

            if (!result.success) {
                console.error("Download failed:", JSON.stringify(result, null, 2));
            }
            expect(result.success).toBe(true);
            expect(result.bytesReceived).toBeGreaterThan(0);

            const downloaded = fs.readFileSync(tmpFile, "utf8");
            expect(downloaded).toBe(testContent);
        } finally {
            try { fs.unlinkSync(tmpFile); } catch { /* ignore */ }
        }
    });
});
