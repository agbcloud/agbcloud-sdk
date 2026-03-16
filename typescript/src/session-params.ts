import { ContextSync } from "./context-sync";
import { BrowserFingerprintContext } from "./modules/browser/browser";

export { BrowserFingerprintContext };

const BROWSER_FINGERPRINT_PERSIST_PATH = "/tmp/browser_fingerprint";

/** Extension context and extension IDs for browser session. */
export interface ExtensionOption {
    contextId: string;
    extensionIds: string[];
}

/**
 * Browser-specific context for session creation (extensions, fingerprint, auto-upload).
 */
export class BrowserContext {
    contextId: string;
    autoUpload: boolean;
    extensionOption?: ExtensionOption;
    fingerprintContext?: BrowserFingerprintContext;
    fingerprintContextId?: string;
    fingerprintContextSync?: ContextSync;

    constructor(
        contextId: string,
        autoUpload: boolean = true,
        extensionOption?: ExtensionOption,
        fingerprintContext?: BrowserFingerprintContext,
    ) {
        this.contextId = contextId;
        this.autoUpload = autoUpload;
        this.extensionOption = extensionOption;
        this.fingerprintContext = fingerprintContext;

        if (fingerprintContext) {
            this.fingerprintContextId = fingerprintContext.fingerprintContextId;
            this.fingerprintContextSync = this._createFingerprintContextSync();
        }
    }

    getExtensionContextSyncs(): ContextSync[] {
        if (!this.extensionOption?.extensionIds?.length || !this.extensionOption.contextId) {
            return [];
        }
        return [
            new ContextSync(
                this.extensionOption.contextId,
                "/home/user/.browser_extensions",
            ),
        ];
    }

    getFingerprintContextSync(): ContextSync | undefined {
        return this.fingerprintContextSync;
    }

    private _createFingerprintContextSync(): ContextSync | undefined {
        if (!this.fingerprintContextId?.trim()) {
            return undefined;
        }
        return new ContextSync(
            this.fingerprintContextId,
            BROWSER_FINGERPRINT_PERSIST_PATH,
        );
    }
}

/** Options for creating a session (passed to CreateSessionParams or AGB.create). */
export interface CreateSessionParamsOptions {
    labels?: Record<string, string>;
    imageId?: string;
    policyId?: string;
    contextSync?: ContextSync[];
    browserContext?: BrowserContext;
    mcpPolicyId?: string;
    idleReleaseTimeout?: number;
}

/**
 * Parameters for creating a session (imageId, labels, contextSync, browserContext, etc.).
 */
export class CreateSessionParams {
    labels?: Record<string, string>;
    imageId?: string;
    policyId?: string;
    contextSync: ContextSync[];
    browserContext?: BrowserContext;
    mcpPolicyId?: string;
    idleReleaseTimeout?: number;

    constructor(options?: CreateSessionParamsOptions) {
        const opts = options ?? {};
        this.labels = opts.labels;
        this.imageId = opts.imageId;
        this.policyId = opts.policyId;
        this.browserContext = opts.browserContext;
        this.mcpPolicyId = opts.mcpPolicyId;
        this.idleReleaseTimeout = opts.idleReleaseTimeout;

        const baseSyncs = opts.contextSync ?? [];
        const allContextSyncs: ContextSync[] = [...baseSyncs];

        if (opts.browserContext) {
            const extSyncs = opts.browserContext.getExtensionContextSyncs();
            allContextSyncs.push(...extSyncs);

            const fpSync = opts.browserContext.getFingerprintContextSync();
            if (fpSync) {
                allContextSyncs.push(fpSync);
            }
        }

        this.contextSync = allContextSyncs;
    }
}
