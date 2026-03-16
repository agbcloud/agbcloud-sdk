import { CreateSessionParams, BrowserContext, BrowserFingerprintContext } from "../../src/session-params";
import { ContextSync } from "../../src/context-sync";

describe("CreateSessionParams", () => {
    test("default params", () => {
        const params = new CreateSessionParams();
        expect(params.labels).toBeUndefined();
        expect(params.imageId).toBeUndefined();
        expect(params.contextSync).toEqual([]);
    });

    test("params with options", () => {
        const params = new CreateSessionParams({
            imageId: "agb-code-space-2",
            labels: { env: "test" },
        });
        expect(params.imageId).toBe("agb-code-space-2");
        expect(params.labels).toEqual({ env: "test" });
    });

    test("params with context sync", () => {
        const sync = ContextSync.new("ctx-1", "/path");
        const params = new CreateSessionParams({
            imageId: "agb-code-space-2",
            contextSync: [sync],
        });
        expect(params.contextSync).toHaveLength(1);
    });

    test("params with browserContext merges extension and fingerprint syncs", () => {
        const bc = new BrowserContext("browser-ctx", true, {
            contextId: "ext-ctx",
            extensionIds: ["ext-1"],
        });
        const params = new CreateSessionParams({
            imageId: "img-1",
            browserContext: bc,
        });
        expect(params.contextSync.length).toBeGreaterThanOrEqual(1);
        expect(params.browserContext).toBe(bc);
    });

    test("params with idleReleaseTimeout and mcpPolicyId", () => {
        const params = new CreateSessionParams({
            imageId: "img-1",
            idleReleaseTimeout: 3600,
            mcpPolicyId: "policy-1",
        });
        expect(params.idleReleaseTimeout).toBe(3600);
        expect(params.mcpPolicyId).toBe("policy-1");
    });
});

describe("BrowserContext", () => {
    test("creates with contextId", () => {
        const bc = new BrowserContext("browser-ctx-123");
        expect(bc.contextId).toBe("browser-ctx-123");
        expect(bc.autoUpload).toBe(true);
    });

    test("creates with autoUpload false", () => {
        const bc = new BrowserContext("ctx-1", false);
        expect(bc.autoUpload).toBe(false);
    });

    test("getExtensionContextSyncs returns syncs when extensionOption set", () => {
        const bc = new BrowserContext("ctx-1", true, {
            contextId: "ext-ctx",
            extensionIds: ["e1", "e2"],
        });
        const syncs = bc.getExtensionContextSyncs();
        expect(syncs).toHaveLength(1);
        expect(syncs[0]).toBeInstanceOf(ContextSync);
    });

    test("getExtensionContextSyncs returns empty when no extensionIds", () => {
        const bc = new BrowserContext("ctx-1", true, {
            contextId: "ext-ctx",
            extensionIds: [],
        });
        expect(bc.getExtensionContextSyncs()).toEqual([]);
    });

    test("getExtensionContextSyncs returns empty when no extensionOption", () => {
        const bc = new BrowserContext("ctx-1");
        expect(bc.getExtensionContextSyncs()).toEqual([]);
    });

    test("getFingerprintContextSync returns sync when fingerprintContext set", () => {
        const fp = new BrowserFingerprintContext("fp-ctx-1");
        const bc = new BrowserContext("ctx-1", true, undefined, fp);
        const sync = bc.getFingerprintContextSync();
        expect(sync).toBeDefined();
        expect(sync).toBeInstanceOf(ContextSync);
    });

    test("getFingerprintContextSync returns undefined when no fingerprintContext", () => {
        const bc = new BrowserContext("ctx-1");
        expect(bc.getFingerprintContextSync()).toBeUndefined();
    });
});
