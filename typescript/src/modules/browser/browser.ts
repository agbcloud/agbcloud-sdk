import { BaseService, type SessionLike } from "../../api/base-service";
import type { BoolResult } from "../../types/api-response";
import { InitBrowserRequest, GetCdpLinkRequest } from "../../api/models";
import type { Client } from "../../api/client";
import { BrowserAgent } from "./browser-agent";
import { BrowserError } from "../../exceptions";
import { FingerprintFormat } from "./fingerprint";
import {
    logOperationStart,
    logOperationSuccess,
    logOperationError,
    logError as logErr,
} from "../../logger";

// ==============================================================================
// Constants
// ==============================================================================
const BROWSER_DATA_PATH = "/tmp/agb_browser_data";
const BROWSER_FINGERPRINT_PERSIST_PATH = "/tmp/browser_fingerprint";

// ==============================================================================
// 1. Data Models
// ==============================================================================

export interface BrowserViewport {
    width: number;
    height: number;
}

export interface BrowserScreen {
    width: number;
    height: number;
}

/**
 * Browser fingerprint generation configuration.
 * Specifies the types of devices, operating systems, and locales
 * to use when generating browser fingerprints.
 */
export interface BrowserFingerprint {
    devices?: Array<"desktop" | "mobile">;
    operatingSystems?: Array<
        "windows" | "macos" | "linux" | "android" | "ios"
    >;
    locales?: string[];
}

/**
 * Browser fingerprint context configuration.
 * Used to persist fingerprints across sessions via a context.
 */
export class BrowserFingerprintContext {
    /** ID of the fingerprint context for browser fingerprint */
    fingerprintContextId: string;

    /**
     * @param fingerprintContextId - ID of the fingerprint context.
     * @throws {Error} If fingerprintContextId is empty.
     */
    constructor(fingerprintContextId: string) {
        if (!fingerprintContextId?.trim()) {
            throw new Error("fingerprintContextId cannot be empty");
        }
        this.fingerprintContextId = fingerprintContextId;
    }
}

// ==============================================================================
// 2. BrowserProxy
// ==============================================================================

export type BrowserProxyType = "custom" | "built-in" | "managed";
export type BrowserProxyStrategy =
    | "restricted"
    | "polling"
    | "sticky"
    | "rotating"
    | "matched";

/**
 * Browser proxy configuration interface.
 */
export interface BrowserProxy {
    type: BrowserProxyType;
    server?: string;
    username?: string;
    password?: string;
    strategy?: BrowserProxyStrategy;
    pollsize?: number;
    userId?: string;
    isp?: string;
    country?: string;
    province?: string;
    city?: string;
    toMap(): Record<string, unknown>;
}

/**
 * Full implementation of BrowserProxy with validation and serialization.
 *
 * Supports three proxy types:
 * - `custom`: Direct proxy with server/username/password
 * - `built-in`: Built-in cloud proxy with restricted/polling strategy
 * - `managed`: Managed proxy with advanced geo/ISP targeting
 */
export class BrowserProxyClass implements BrowserProxy {
    type: BrowserProxyType;
    server?: string;
    username?: string;
    password?: string;
    strategy?: BrowserProxyStrategy;
    pollsize?: number;
    userId?: string;
    isp?: string;
    country?: string;
    province?: string;
    city?: string;

    constructor(
        proxyType: BrowserProxyType,
        server?: string,
        username?: string,
        password?: string,
        strategy?: BrowserProxyStrategy,
        pollsize?: number,
        userId?: string,
        isp?: string,
        country?: string,
        province?: string,
        city?: string,
    ) {
        this.type = proxyType;
        this.server = server;
        this.username = username;
        this.password = password;
        this.strategy = strategy;
        this.pollsize = pollsize;
        this.userId = userId;
        this.isp = isp;
        this.country = country;
        this.province = province;
        this.city = city;

        if (
            proxyType !== "custom" &&
            proxyType !== "built-in" &&
            proxyType !== "managed"
        ) {
            throw new Error("proxy_type must be custom, built-in, or managed");
        }

        if (proxyType === "custom" && !server) {
            throw new Error("server is required for custom proxy type");
        }

        if (proxyType === "built-in") {
            if (!strategy) {
                throw new Error(
                    "strategy is required for built-in proxy type",
                );
            }
            if (strategy !== "restricted" && strategy !== "polling") {
                throw new Error(
                    "strategy must be restricted or polling for built-in proxy type",
                );
            }
            if (
                strategy === "polling" &&
                pollsize !== undefined &&
                pollsize <= 0
            ) {
                throw new Error(
                    "pollsize must be greater than 0 for polling strategy",
                );
            }
        }

        if (proxyType === "managed") {
            if (!strategy) {
                throw new Error(
                    "strategy is required for managed proxy type",
                );
            }
            if (
                strategy !== "polling" &&
                strategy !== "sticky" &&
                strategy !== "rotating" &&
                strategy !== "matched"
            ) {
                throw new Error(
                    "strategy must be polling, sticky, rotating, or matched for managed proxy type",
                );
            }
            if (!userId) {
                throw new Error(
                    "userId is required for managed proxy type",
                );
            }
            if (
                strategy === "matched" &&
                !isp &&
                !country &&
                !province &&
                !city
            ) {
                throw new Error(
                    "at least one of isp, country, province, or city is required for matched strategy",
                );
            }
        }
    }

    toMap(): Record<string, unknown> {
        const proxyMap: Record<string, unknown> = { type: this.type };

        if (this.type === "custom") {
            proxyMap.server = this.server;
            if (this.username) proxyMap.username = this.username;
            if (this.password) proxyMap.password = this.password;
        } else if (this.type === "built-in") {
            proxyMap.strategy = this.strategy;
            if (this.strategy === "polling") {
                proxyMap.pollsize = this.pollsize;
            }
        } else if (this.type === "managed") {
            proxyMap.strategy = this.strategy;
            if (this.userId) proxyMap.userId = this.userId;
            if (this.isp) proxyMap.isp = this.isp;
            if (this.country) proxyMap.country = this.country;
            if (this.province) proxyMap.province = this.province;
            if (this.city) proxyMap.city = this.city;
        }

        return proxyMap;
    }

    static fromMap(
        m: Record<string, unknown> | null | undefined,
    ): BrowserProxyClass | null {
        if (!m || typeof m !== "object") return null;

        const proxyType = m.type as BrowserProxyType | undefined;
        if (!proxyType) return null;

        if (proxyType === "custom") {
            return new BrowserProxyClass(
                proxyType,
                m.server as string | undefined,
                m.username as string | undefined,
                m.password as string | undefined,
            );
        } else if (proxyType === "built-in") {
            return new BrowserProxyClass(
                proxyType,
                undefined,
                undefined,
                undefined,
                m.strategy as BrowserProxyStrategy | undefined,
                (m.pollsize as number) || 10,
            );
        } else if (proxyType === "managed") {
            return new BrowserProxyClass(
                proxyType,
                undefined,
                undefined,
                undefined,
                m.strategy as BrowserProxyStrategy | undefined,
                undefined,
                m.userId as string | undefined,
                m.isp as string | undefined,
                m.country as string | undefined,
                m.province as string | undefined,
                m.city as string | undefined,
            );
        }

        throw new Error(`Unsupported proxy type: ${proxyType}`);
    }
}

// ==============================================================================
// 3. BrowserOption
// ==============================================================================

/**
 * Browser initialization option interface.
 * All properties are optional — omitted properties use server defaults.
 */
export interface BrowserOption {
    persistentPath?: string;
    useStealth?: boolean;
    userAgent?: string;
    viewport?: BrowserViewport;
    screen?: BrowserScreen;
    fingerprint?: BrowserFingerprint;
    /** Detailed fingerprint configuration */
    fingerprintFormat?: FingerprintFormat;
    /** Enable fingerprint persistence across sessions */
    fingerprintPersistent?: boolean;
    solveCaptchas?: boolean;
    proxies?: BrowserProxy[];
    /** Path to the extensions directory. Defaults to "/tmp/extensions/" */
    extensionPath?: string;
    /** Additional command line arguments for the browser */
    cmdArgs?: string[];
    /** Default URL to navigate to when browser starts */
    defaultNavigateUrl?: string;
    /** Browser type: 'chrome' or 'chromium' */
    browserType?: "chrome" | "chromium";
}

/**
 * Full implementation of BrowserOption with validation and serialization.
 *
 * Provides `toMap()` for API serialization and `fromMap()` for deserialization.
 */
export class BrowserOptionClass implements BrowserOption {
    persistentPath?: string;
    useStealth?: boolean;
    userAgent?: string;
    viewport?: BrowserViewport;
    screen?: BrowserScreen;
    fingerprint?: BrowserFingerprint;
    fingerprintFormat?: FingerprintFormat;
    fingerprintPersistent?: boolean;
    fingerprintPersistPath?: string;
    solveCaptchas?: boolean;
    proxies?: BrowserProxy[];
    extensionPath?: string;
    cmdArgs?: string[];
    defaultNavigateUrl?: string;
    browserType?: "chrome" | "chromium";

    constructor(options?: Partial<BrowserOption>) {
        const o = options ?? {};
        this.useStealth = o.useStealth ?? false;
        this.userAgent = o.userAgent;
        this.viewport = o.viewport;
        this.screen = o.screen;
        this.fingerprint = o.fingerprint;
        this.fingerprintFormat = o.fingerprintFormat;
        this.fingerprintPersistent = o.fingerprintPersistent ?? false;
        this.solveCaptchas = o.solveCaptchas ?? false;
        this.extensionPath = o.extensionPath ?? "/tmp/extensions/";
        this.cmdArgs = o.cmdArgs;
        this.defaultNavigateUrl = o.defaultNavigateUrl;
        this.browserType = o.browserType;

        if (this.fingerprintPersistent) {
            this.fingerprintPersistPath = `${BROWSER_FINGERPRINT_PERSIST_PATH}/fingerprint.json`;
        }

        if (o.proxies !== undefined) {
            if (!Array.isArray(o.proxies)) {
                throw new Error("proxies must be a list");
            }
            if (o.proxies.length > 1) {
                throw new Error("proxies list length must be limited to 1");
            }
        }
        this.proxies = o.proxies;

        if (this.cmdArgs !== undefined && !Array.isArray(this.cmdArgs)) {
            throw new Error("cmdArgs must be a list");
        }

        if (
            this.browserType !== undefined &&
            this.browserType !== "chrome" &&
            this.browserType !== "chromium"
        ) {
            throw new Error("browserType must be 'chrome' or 'chromium'");
        }
    }

    /**
     * Serialize the option to a plain map for the API request.
     */
    toMap(): Record<string, unknown> {
        const m: Record<string, unknown> = {};

        if (process.env.AGB_BROWSER_BEHAVIOR_SIMULATE) {
            m.behaviorSimulate =
                process.env.AGB_BROWSER_BEHAVIOR_SIMULATE !== "0";
        }
        if (this.useStealth !== undefined) m.useStealth = this.useStealth;
        if (this.userAgent !== undefined) m.userAgent = this.userAgent;
        if (this.viewport !== undefined) {
            m.viewport = {
                width: this.viewport.width,
                height: this.viewport.height,
            };
        }
        if (this.screen !== undefined) {
            m.screen = {
                width: this.screen.width,
                height: this.screen.height,
            };
        }
        if (this.fingerprint !== undefined) {
            const fp: Record<string, unknown> = {};
            if (this.fingerprint.devices) fp.devices = this.fingerprint.devices;
            if (this.fingerprint.operatingSystems)
                fp.operatingSystems = this.fingerprint.operatingSystems;
            if (this.fingerprint.locales) fp.locales = this.fingerprint.locales;
            m.fingerprint = fp;
        }
        if (this.fingerprintFormat !== undefined) {
            try {
                const jsonStr = this.fingerprintFormat.toJson();
                m.fingerprintRawData = Buffer.from(jsonStr, "utf-8").toString(
                    "base64",
                );
            } catch (error) {
                logErr("Failed to serialize fingerprint format");
            }
        }
        if (this.fingerprintPersistent) {
            this.fingerprintPersistPath = `${BROWSER_FINGERPRINT_PERSIST_PATH}/fingerprint.json`;
            m.fingerprintPersistPath = this.fingerprintPersistPath;
        }
        if (this.solveCaptchas !== undefined)
            m.solveCaptchas = this.solveCaptchas;
        if (this.proxies !== undefined) {
            m.proxies = this.proxies.map((proxy) => {
                if (proxy instanceof BrowserProxyClass) {
                    return proxy.toMap();
                }
                return proxy;
            });
        }
        if (this.extensionPath !== undefined)
            m.extensionPath = this.extensionPath;
        if (this.cmdArgs !== undefined) m.cmdArgs = this.cmdArgs;
        if (this.defaultNavigateUrl !== undefined)
            m.defaultNavigateUrl = this.defaultNavigateUrl;
        if (this.browserType !== undefined) m.browserType = this.browserType;

        return m;
    }

    /**
     * Populate this instance from a plain map (deserialization).
     */
    fromMap(m: Record<string, unknown> | null | undefined): BrowserOptionClass {
        const map = (m ?? {}) as Record<string, any>;

        this.useStealth = map.useStealth ?? false;
        this.userAgent = map.userAgent;

        if (map.viewport) {
            this.viewport = {
                width: map.viewport.width,
                height: map.viewport.height,
            };
        }
        if (map.screen) {
            this.screen = {
                width: map.screen.width,
                height: map.screen.height,
            };
        }
        if (map.fingerprint) {
            const fp: BrowserFingerprint = {};
            if (map.fingerprint.devices) fp.devices = map.fingerprint.devices;
            if (map.fingerprint.operatingSystems)
                fp.operatingSystems = map.fingerprint.operatingSystems;
            if (map.fingerprint.locales) fp.locales = map.fingerprint.locales;
            this.fingerprint = fp;
        }
        if (map.fingerprintFormat !== undefined) {
            if (map.fingerprintFormat instanceof FingerprintFormat) {
                this.fingerprintFormat = map.fingerprintFormat;
            } else {
                try {
                    this.fingerprintFormat = FingerprintFormat.fromDict(
                        map.fingerprintFormat,
                    );
                } catch {
                    this.fingerprintFormat = undefined;
                }
            }
        } else if (map.fingerprintRawData !== undefined) {
            try {
                const jsonStr = Buffer.from(
                    map.fingerprintRawData,
                    "base64",
                ).toString("utf-8");
                this.fingerprintFormat = FingerprintFormat.fromJson(jsonStr);
            } catch {
                this.fingerprintFormat = undefined;
            }
        }

        if (map.fingerprintPersistent !== undefined) {
            this.fingerprintPersistent = map.fingerprintPersistent;
        } else if (map.fingerprintPersistPath !== undefined) {
            this.fingerprintPersistPath = map.fingerprintPersistPath;
            this.fingerprintPersistent = true;
        } else {
            this.fingerprintPersistent = false;
        }

        this.solveCaptchas = map.solveCaptchas;

        if (map.proxies !== undefined) {
            const proxyList = map.proxies as unknown[];
            if (proxyList.length > 1) {
                throw new Error("proxies list length must be limited to 1");
            }
            this.proxies = proxyList
                .map((proxyData: unknown) => {
                    if (proxyData instanceof BrowserProxyClass) {
                        return proxyData;
                    }
                    return BrowserProxyClass.fromMap(
                        proxyData as Record<string, unknown>,
                    );
                })
                .filter(Boolean) as BrowserProxy[];
        }

        this.extensionPath = map.extensionPath;
        this.cmdArgs = map.cmdArgs;
        this.defaultNavigateUrl = map.defaultNavigateUrl;
        this.browserType = map.browserType;

        return this;
    }
}

// ==============================================================================
// 4. Browser Service
// ==============================================================================

/**
 * Browser module for web automation: navigate, click, type, screenshot, and extract content.
 * Requires initialization with browser options. Use session.browser.agent for high-level tasks.
 */
export class Browser extends BaseService {
    private _initialized = false;
    private endpointRouterPort?: number;
    private _option: BrowserOptionClass | null = null;
    private _endpointUrl: string | null = null;
    agent: BrowserAgent;

    constructor(session: SessionLike) {
        super(session);
        this.agent = new BrowserAgent(session, this);
    }

    getOption(): BrowserOptionClass | null {
        return this._option;
    }

    isInitialized(): boolean {
        return this._initialized;
    }

    /**
     * Resolve an incoming option (plain object or BrowserOptionClass) into
     * a BrowserOptionClass and its serialized map, with enableRecord injected.
     */
    private resolveOption(
        option: BrowserOptionClass | BrowserOption,
    ): { browserOption: BrowserOptionClass; browserOptionMap: Record<string, unknown> } {
        let browserOption: BrowserOptionClass;
        if (option instanceof BrowserOptionClass) {
            browserOption = option;
        } else {
            browserOption = new BrowserOptionClass();
            browserOption.fromMap(option as Record<string, unknown>);
        }

        const browserOptionMap = browserOption.toMap();


        return { browserOption, browserOptionMap };
    }

    /**
     * Initialize the browser instance with the given options.
     *
     * Note: In Python, initialize() uses sync HTTP and initialize_async() uses async HTTP.
     * In TypeScript there is no standard synchronous HTTP API; both methods use the same
     * async client and return Promise<boolean>. Use initialize() or initializeAsync()
     * interchangeably (e.g. await session.browser.initialize(option)).
     *
     * @param option - Browser configuration options (BrowserOptionClass or plain BrowserOption).
     * @returns Promise resolving to true if initialization succeeded, false otherwise.
     */
    async initialize(
        option: BrowserOptionClass | BrowserOption,
    ): Promise<boolean> {
        if (this.isInitialized()) {
            return true;
        }

        try {
            logOperationStart(
                "Browser.initialize",
                `SessionId=${this.session.getSessionId()}`,
            );

            const { browserOption, browserOptionMap } =
                this.resolveOption(option);

            const request = new InitBrowserRequest(
                `Bearer ${this.session.getApiKey()}`,
                this.session.getSessionId(),
                BROWSER_DATA_PATH,
                Object.keys(browserOptionMap).length > 0
                    ? browserOptionMap
                    : undefined,
            );

            const client = (
                this.session as unknown as { getClient(): Client }
            ).getClient();
            const response = await client.initBrowser(request);

            const requestId = response.requestId ?? "";
            const port = response.getPort();
            const success =
                response.isSuccessful() &&
                port !== null &&
                port !== undefined;

            if (success) {
                logOperationSuccess(
                    "Browser.initialize",
                    `Port=${port}, RequestId=${requestId}`,
                );
                this._initialized = true;
                this.endpointRouterPort = port;
                this._option = browserOption;
            } else {
                logOperationError(
                    "Browser.initialize",
                    `Port not found in response. RequestId=${requestId}`,
                );
            }

            return success;
        } catch (error) {
            logOperationError(
                "Browser.initialize",
                `Failed to initialize browser instance: ${error}`,
            );
            this._initialized = false;
            this._endpointUrl = null;
            this._option = null;
            return false;
        }
    }

    /**
     * Initialize the browser instance asynchronously.
     * Same as initialize() in TypeScript (both use async HTTP). Exists for API parity with
     * Python SDK where initialize_async uses async HTTP and initialize uses sync HTTP.
     *
     * @param option - Browser configuration options (BrowserOptionClass or plain BrowserOption).
     * @returns Promise resolving to true if initialization succeeded, false otherwise.
     */
    async initializeAsync(
        option: BrowserOptionClass | BrowserOption,
    ): Promise<boolean> {
        return this.initialize(option);
    }

    async destroy(): Promise<BoolResult> {
        if (!this._initialized) {
            throw new BrowserError(
                "Browser is not initialized. Cannot destroy browser.",
            );
        }

        const result = await this.callMcpTool("stopChrome", {});
        this._initialized = false;
        this.endpointRouterPort = undefined;
        this._option = null;
        this._endpointUrl = null;

        if (result.success) {
            return {
                requestId: result.requestId ?? "",
                success: true,
                data: true,
            };
        }
        return {
            requestId: result.requestId ?? "",
            success: false,
            data: false,
            errorMessage: result.errorMessage ?? "Failed to stop browser",
        };
    }

    /**
     * Takes a screenshot of the specified Playwright page with enhanced options.
     * Handles scroll-to-load for lazy content, lazy images, and viewport resizing.
     *
     * @param page - The Playwright Page object to screenshot.
     * @param fullPage - Whether to capture the full scrollable page. Defaults to false.
     * @param options - Additional screenshot options (type, quality, timeout, etc.).
     * @returns Screenshot data as Uint8Array.
     * @throws {BrowserError} If browser is not initialized.
     */
    async screenshot(
        page: unknown,
        fullPage = false,
        options: Record<string, unknown> = {},
    ): Promise<Uint8Array> {
        if (!this._initialized) {
            throw new BrowserError(
                "Browser must be initialized before calling screenshot.",
            );
        }

        if (page === null || page === undefined) {
            throw new Error("Page cannot be null or undefined");
        }

        const p = page as Record<string, (...args: unknown[]) => Promise<unknown>>;

        const enhancedOptions: Record<string, unknown> = {
            animations: "disabled",
            caret: "hide",
            scale: "css",
            timeout: (options.timeout as number) || 60000,
            fullPage,
            type: (options.type as string) || "png",
        };
        Object.assign(enhancedOptions, options);

        try {
            await p.evaluate("window.scrollTo(0, document.body.scrollHeight)");
            await p.waitForLoadState("domcontentloaded" as unknown as undefined);

            await this._scrollToLoadAllContent(p);

            await p.evaluate(`
                () => {
                    document.querySelectorAll('img[data-src]').forEach(img => {
                        if (!img.src && img.dataset.src) {
                            img.src = img.dataset.src;
                        }
                    });
                    document.querySelectorAll('[data-bg]').forEach(el => {
                        if (!el.style.backgroundImage) {
                            el.style.backgroundImage = \`url(\${el.dataset.bg})\`;
                        }
                    });
                }
            `);

            await p.waitForTimeout(1500 as unknown as undefined);
            const finalHeight = (await p.evaluate(
                "document.body.scrollHeight",
            )) as number;
            await p.setViewportSize({
                width: 1920,
                height: Math.min(finalHeight, 10000),
            } as unknown as undefined);

            const screenshotBuffer = (await p.screenshot(
                enhancedOptions as unknown as undefined,
            )) as Buffer;

            return new Uint8Array(screenshotBuffer);
        } catch (error) {
            let errorStr: string;
            try {
                errorStr = String(error);
            } catch {
                errorStr = "Unknown error occurred";
            }
            throw new Error(`Failed to capture screenshot: ${errorStr}`);
        }
    }

    private async _scrollToLoadAllContent(
        page: Record<string, (...args: unknown[]) => Promise<unknown>>,
        maxScrolls = 8,
        delayMs = 1200,
    ): Promise<void> {
        let lastHeight = 0;
        for (let i = 0; i < maxScrolls; i++) {
            await page.evaluate(
                "window.scrollTo(0, document.body.scrollHeight)",
            );
            await page.waitForTimeout(delayMs as unknown as undefined);
            const newHeight = (await page.evaluate(
                "Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)",
            )) as number;
            if (newHeight === lastHeight) break;
            lastHeight = newHeight;
        }
    }

    /**
     * Returns the CDP endpoint URL for connecting to the browser via Playwright or similar.
     * Caches the URL in _endpointUrl after the first successful getCdpLink call.
     *
     * @returns Promise resolving to the CDP endpoint URL
     * @throws {BrowserError} If browser is not initialized
     */
    async getEndpointUrl(): Promise<string> {
        if (!this._initialized) {
            throw new BrowserError(
                "Browser is not initialized. Cannot access endpoint URL.",
            );
        }

        if (this._endpointUrl != null) {
            return this._endpointUrl;
        }

        try {
            const client = (
                this.session as unknown as { getClient(): Client }
            ).getClient();

            const request = new GetCdpLinkRequest(
                `Bearer ${this.session.getApiKey()}`,
                this.session.getSessionId(),
            );
            const response = await client.getCdpLink(request);

            if (response.isSuccessful()) {
                const url = response.getUrl();
                if (url) {
                    this._endpointUrl = url;
                    return url;
                }
                throw new BrowserError(
                    "Failed to get CDP link: No URL in response",
                );
            }

            throw new BrowserError(
                `Failed to get CDP link: ${response.getErrorMessage()}`,
            );
        } catch (error) {
            if (error instanceof BrowserError) {
                throw error;
            }
            throw new BrowserError(
                `Failed to get endpoint URL from session: ${error}`,
            );
        }
    }
}
