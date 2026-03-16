import {
    ContextSync,
    newSyncPolicy,
    newRecyclePolicy,
    syncPolicyToDict,
    Lifecycle,
    UploadStrategy,
    UploadMode,
    DownloadStrategy,
} from "../../src/context-sync";

describe("ContextSync", () => {
    test("ContextSync.new creates instance", () => {
        const cs = ContextSync.new("ctx-123", "/data/path");
        expect(cs.contextId).toBe("ctx-123");
        expect(cs.path).toBe("/data/path");
        expect(cs.policy).toBeUndefined();
    });

    test("withPolicy sets policy", () => {
        const policy = newSyncPolicy();
        const cs = ContextSync.new("ctx-123", "/data/path").withPolicy(policy);
        expect(cs.policy).toBe(policy);
    });
});

describe("SyncPolicy", () => {
    test("newSyncPolicy creates default policy", () => {
        const policy = newSyncPolicy();
        expect(policy.uploadPolicy).toBeDefined();
        expect(policy.downloadPolicy).toBeDefined();
        expect(policy.deletePolicy).toBeDefined();
        expect(policy.extractPolicy).toBeDefined();
        expect(policy.recyclePolicy).toBeDefined();
        expect(policy.bwList).toBeDefined();
    });

    test("syncPolicyToDict converts to JSON-ready dict", () => {
        const policy = newSyncPolicy();
        const dict = syncPolicyToDict(policy);
        expect(dict.uploadPolicy).toBeDefined();
        expect((dict.uploadPolicy as Record<string, unknown>).autoUpload).toBe(true);
        expect((dict.uploadPolicy as Record<string, unknown>).uploadStrategy).toBe(
            UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
        );
    });

    test("newRecyclePolicy rejects wildcards", () => {
        expect(() => newRecyclePolicy({ paths: ["/data/*"] })).toThrow(
            "Wildcard patterns are not supported",
        );
    });

    test("default lifecycle is FOREVER", () => {
        const rp = newRecyclePolicy();
        expect(rp.lifecycle).toBe(Lifecycle.LIFECYCLE_FOREVER);
    });
});
