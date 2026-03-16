import {
    Browser,
    BrowserOptionClass,
    BrowserProxyClass,
    BrowserFingerprintContext,
} from "../../src/modules/browser/browser";
import type { BrowserOption, BrowserProxy } from "../../src/modules/browser/browser";
import { BrowserError } from "../../src/exceptions";

const mockInitBrowserResponse = (success: boolean, port?: number, errMsg?: string) => ({
    isSuccessful: () => success,
    getPort: () => port,
    getErrorMessage: () => errMsg ?? "",
    requestId: "req-init",
});

const mockCdpLinkResponse = (success: boolean, url?: string, errMsg?: string) => ({
    isSuccessful: () => success,
    getUrl: () => url,
    getErrorMessage: () => errMsg ?? "Unknown error",
});

function createMockSession(initResult?: ReturnType<typeof mockInitBrowserResponse>) {
    const client = {
        initBrowser: jest.fn().mockResolvedValue(
            initResult ?? mockInitBrowserResponse(true, 9222)
        ),
        getCdpLink: jest.fn().mockResolvedValue(
            mockCdpLinkResponse(true, "ws://localhost:9222/devtools/browser/abc")
        ),
    };
    return {
        getApiKey: () => "test-key",
        getSessionId: () => "test-session",
        getClient: () => client,
        enableBrowserReplay: false,
    };
}

describe("BrowserProxyClass", () => {
    test("custom proxy requires server", () => {
        expect(() => new BrowserProxyClass("custom")).toThrow("server is required");
    });

    test("custom proxy creates correctly", () => {
        const proxy = new BrowserProxyClass("custom", "http://proxy:8080", "user", "pass");
        expect(proxy.type).toBe("custom");
        const map = proxy.toMap();
        expect(map.type).toBe("custom");
        expect(map.server).toBe("http://proxy:8080");
        expect(map.username).toBe("user");
        expect(map.password).toBe("pass");
    });

    test("built-in proxy requires strategy", () => {
        expect(() => new BrowserProxyClass("built-in")).toThrow("strategy is required");
    });

    test("built-in proxy restricted strategy", () => {
        const proxy = new BrowserProxyClass("built-in", undefined, undefined, undefined, "restricted");
        expect(proxy.type).toBe("built-in");
        const map = proxy.toMap();
        expect(map.strategy).toBe("restricted");
    });

    test("built-in polling with invalid pollsize", () => {
        expect(
            () => new BrowserProxyClass("built-in", undefined, undefined, undefined, "polling", 0),
        ).toThrow("pollsize must be greater than 0");
    });

    test("managed proxy requires userId", () => {
        expect(
            () => new BrowserProxyClass("managed", undefined, undefined, undefined, "polling"),
        ).toThrow("userId is required");
    });

    test("managed proxy matched strategy requires geo info", () => {
        expect(
            () => new BrowserProxyClass("managed", undefined, undefined, undefined, "matched", undefined, "user1"),
        ).toThrow("at least one of isp, country, province, or city");
    });

    test("managed proxy creates correctly", () => {
        const proxy = new BrowserProxyClass(
            "managed", undefined, undefined, undefined,
            "sticky", undefined, "user1",
        );
        expect(proxy.type).toBe("managed");
        const map = proxy.toMap();
        expect(map.strategy).toBe("sticky");
        expect(map.userId).toBe("user1");
    });

    test("fromMap custom", () => {
        const proxy = BrowserProxyClass.fromMap({ type: "custom", server: "http://x" });
        expect(proxy).not.toBeNull();
        expect(proxy!.type).toBe("custom");
        expect(proxy!.server).toBe("http://x");
    });

    test("fromMap built-in", () => {
        const proxy = BrowserProxyClass.fromMap({ type: "built-in", strategy: "restricted" });
        expect(proxy).not.toBeNull();
        expect(proxy!.type).toBe("built-in");
    });

    test("fromMap null returns null", () => {
        expect(BrowserProxyClass.fromMap(null)).toBeNull();
        expect(BrowserProxyClass.fromMap(undefined)).toBeNull();
        expect(BrowserProxyClass.fromMap({})).toBeNull();
    });
});

describe("BrowserFingerprintContext", () => {
    test("requires non-empty contextId", () => {
        expect(() => new BrowserFingerprintContext("")).toThrow("cannot be empty");
        expect(() => new BrowserFingerprintContext("  ")).toThrow("cannot be empty");
    });

    test("stores contextId", () => {
        const ctx = new BrowserFingerprintContext("fp-ctx-1");
        expect(ctx.fingerprintContextId).toBe("fp-ctx-1");
    });
});

describe("BrowserOptionClass", () => {
    test("defaults", () => {
        const opt = new BrowserOptionClass();
        expect(opt.useStealth).toBe(false);
        expect(opt.solveCaptchas).toBe(false);
        expect(opt.extensionPath).toBe("/tmp/extensions/");
        expect(opt.fingerprintPersistent).toBe(false);
    });

    test("with proxies", () => {
        const proxy = new BrowserProxyClass("custom", "http://proxy:8080");
        const opt = new BrowserOptionClass({ proxies: [proxy] });
        expect(opt.proxies).toHaveLength(1);
    });

    test("rejects more than 1 proxy", () => {
        const p1 = new BrowserProxyClass("custom", "http://a:8080");
        const p2 = new BrowserProxyClass("custom", "http://b:8080");
        expect(() => new BrowserOptionClass({ proxies: [p1, p2] })).toThrow("limited to 1");
    });

    test("invalid browserType", () => {
        expect(() => new BrowserOptionClass({ browserType: "firefox" as any })).toThrow(
            "must be 'chrome' or 'chromium'",
        );
    });

    test("toMap with full options", () => {
        const proxy = new BrowserProxyClass("custom", "http://proxy:8080");
        const opt = new BrowserOptionClass({
            useStealth: true,
            userAgent: "MyAgent",
            viewport: { width: 1920, height: 1080 },
            screen: { width: 1920, height: 1080 },
            fingerprint: { devices: ["desktop"], operatingSystems: ["windows"], locales: ["en-US"] },
            solveCaptchas: true,
            proxies: [proxy],
            cmdArgs: ["--no-sandbox"],
            defaultNavigateUrl: "https://example.com",
            browserType: "chrome",
        });
        const map = opt.toMap();
        expect(map.useStealth).toBe(true);
        expect(map.userAgent).toBe("MyAgent");
        expect(map.viewport).toEqual({ width: 1920, height: 1080 });
        expect(map.screen).toEqual({ width: 1920, height: 1080 });
        expect(map.fingerprint).toEqual({
            devices: ["desktop"],
            operatingSystems: ["windows"],
            locales: ["en-US"],
        });
        expect(map.solveCaptchas).toBe(true);
        expect(map.proxies).toHaveLength(1);
        expect(map.cmdArgs).toEqual(["--no-sandbox"]);
        expect(map.defaultNavigateUrl).toBe("https://example.com");
        expect(map.browserType).toBe("chrome");
    });

    test("toMap empty options", () => {
        const opt = new BrowserOptionClass();
        const map = opt.toMap();
        expect(map.useStealth).toBe(false);
        expect(map.solveCaptchas).toBe(false);
        expect(map.extensionPath).toBe("/tmp/extensions/");
    });

    test("fromMap populates fields", () => {
        const opt = new BrowserOptionClass();
        opt.fromMap({
            useStealth: true,
            userAgent: "TestAgent",
            viewport: { width: 800, height: 600 },
            fingerprint: { devices: ["mobile"], locales: ["zh-CN"] },
            browserType: "chromium",
        });
        expect(opt.useStealth).toBe(true);
        expect(opt.userAgent).toBe("TestAgent");
        expect(opt.viewport).toEqual({ width: 800, height: 600 });
        expect(opt.fingerprint?.devices).toEqual(["mobile"]);
        expect(opt.browserType).toBe("chromium");
    });

    test("fingerprintPersistent sets persistPath", () => {
        const opt = new BrowserOptionClass({ fingerprintPersistent: true });
        expect(opt.fingerprintPersistent).toBe(true);
        expect(opt.fingerprintPersistPath).toContain("fingerprint.json");
        const map = opt.toMap();
        expect(map.fingerprintPersistPath).toContain("fingerprint.json");
    });
});

describe("Browser", () => {
    test("initial state", () => {
        const session = createMockSession();
        const browser = new Browser(session);
        expect(browser.isInitialized()).toBe(false);
        expect(browser.getOption()).toBeNull();
    });

    test("initialize returns true on success", async () => {
        const session = createMockSession();
        const browser = new Browser(session);
        const ok = await browser.initialize({});
        expect(ok).toBe(true);
        expect(browser.isInitialized()).toBe(true);
        expect(browser.getOption()).not.toBeNull();
    });

    test("initialize with plain option", async () => {
        const session = createMockSession();
        const browser = new Browser(session);
        const opt: BrowserOption = {
            useStealth: true,
            proxies: [
                new BrowserProxyClass("custom", "http://proxy:8080"),
            ],
        };
        const ok = await browser.initialize(opt);
        expect(ok).toBe(true);
        expect(browser.getOption()).not.toBeNull();
        expect(browser.getOption()!.useStealth).toBe(true);
        expect(browser.isInitialized()).toBe(true);
    });

    test("initialize with BrowserOptionClass", async () => {
        const session = createMockSession();
        const browser = new Browser(session);
        const opt = new BrowserOptionClass({
            useStealth: true,
            browserType: "chrome",
        });
        const ok = await browser.initialize(opt);
        expect(ok).toBe(true);
        expect(browser.isInitialized()).toBe(true);
    });

    test("initializeAsync returns boolean (alias for initialize)", async () => {
        const session = createMockSession();
        const browser = new Browser(session);
        const ok = await browser.initializeAsync({});
        expect(ok).toBe(true);
        expect(browser.isInitialized()).toBe(true);
    });

    test("initialize already initialized returns true early", async () => {
        const session = createMockSession();
        const browser = new Browser(session);
        await browser.initialize({});
        const ok = await browser.initialize({});
        expect(ok).toBe(true);
        expect(session.getClient().initBrowser).toHaveBeenCalledTimes(1);
    });

    test("initialize failure - API error returns false", async () => {
        const session = createMockSession(
            mockInitBrowserResponse(false, undefined, "Server error")
        );
        const browser = new Browser(session);
        const ok = await browser.initialize({});
        expect(ok).toBe(false);
        expect(browser.isInitialized()).toBe(false);
    });

    test("initialize failure - no port returns false", async () => {
        const session = createMockSession(
            mockInitBrowserResponse(true, undefined)
        );
        const browser = new Browser(session);
        const ok = await browser.initialize({});
        expect(ok).toBe(false);
        expect(browser.isInitialized()).toBe(false);
    });

    test("initialize failure - exception returns false", async () => {
        const session = createMockSession();
        session.getClient().initBrowser = jest.fn().mockRejectedValue(new Error("Network error"));
        const browser = new Browser(session);
        const ok = await browser.initialize({});
        expect(ok).toBe(false);
        expect(browser.isInitialized()).toBe(false);
    });

    test("destroy when not initialized throws BrowserError", async () => {
        const session = createMockSession();
        const browser = new Browser(session);
        await expect(browser.destroy()).rejects.toThrow(BrowserError);
        await expect(browser.destroy()).rejects.toThrow("not initialized");
    });

    test("destroy success resets all state", async () => {
        const session = createMockSession();
        const browser = new Browser(session);
        await browser.initialize({});
        const spy = jest.spyOn(browser as any, "callMcpTool").mockResolvedValue({
            requestId: "req-stop", success: true, data: "true",
        });
        const r = await browser.destroy();
        expect(r.success).toBe(true);
        expect(r.data).toBe(true);
        expect(browser.isInitialized()).toBe(false);
        expect(browser.getOption()).toBeNull();
        expect(spy).toHaveBeenCalledWith("stopChrome", {});
        spy.mockRestore();
    });

    test("destroy failure", async () => {
        const session = createMockSession();
        const browser = new Browser(session);
        await browser.initialize({});
        jest.spyOn(browser as any, "callMcpTool").mockResolvedValue({
            requestId: "req-stopf", success: false, errorMessage: "Stop failed",
        });
        const r = await browser.destroy();
        expect(r.success).toBe(false);
        expect(r.data).toBe(false);
        expect(r.errorMessage).toBe("Stop failed");
    });

    test("getEndpointUrl when not initialized throws BrowserError", async () => {
        const session = createMockSession();
        const browser = new Browser(session);
        await expect(browser.getEndpointUrl()).rejects.toThrow(BrowserError);
        await expect(browser.getEndpointUrl()).rejects.toThrow("not initialized");
    });

    test("getEndpointUrl success via getCdpLink", async () => {
        const session = createMockSession();
        const browser = new Browser(session);
        await browser.initialize({});
        const url = await browser.getEndpointUrl();
        expect(url).toBe("ws://localhost:9222/devtools/browser/abc");
        expect(session.getClient().getCdpLink).toHaveBeenCalledTimes(1);
    });

    test("getEndpointUrl caches result and does not call getCdpLink twice", async () => {
        const session = createMockSession();
        const browser = new Browser(session);
        await browser.initialize({});
        const url1 = await browser.getEndpointUrl();
        const url2 = await browser.getEndpointUrl();
        expect(url1).toBe("ws://localhost:9222/devtools/browser/abc");
        expect(url2).toBe(url1);
        expect(session.getClient().getCdpLink).toHaveBeenCalledTimes(1);
    });

    test("getEndpointUrl getCdpLink API failure throws BrowserError", async () => {
        const session = createMockSession();
        session.getClient().getCdpLink = jest.fn().mockResolvedValue(
            mockCdpLinkResponse(false, undefined, "Service unavailable"),
        );
        const browser = new Browser(session);
        await browser.initialize({});
        await expect(browser.getEndpointUrl()).rejects.toThrow(BrowserError);
        await expect(browser.getEndpointUrl()).rejects.toThrow("Service unavailable");
    });

    test("getEndpointUrl getCdpLink no URL throws BrowserError", async () => {
        const session = createMockSession();
        session.getClient().getCdpLink = jest.fn().mockResolvedValue(
            mockCdpLinkResponse(true, undefined),
        );
        const browser = new Browser(session);
        await browser.initialize({});
        await expect(browser.getEndpointUrl()).rejects.toThrow(BrowserError);
        await expect(browser.getEndpointUrl()).rejects.toThrow("No URL");
    });

    test("getEndpointUrl getCdpLink network error wraps as BrowserError", async () => {
        const session = createMockSession();
        session.getClient().getCdpLink = jest.fn().mockRejectedValue(new Error("Network down"));
        const browser = new Browser(session);
        await browser.initialize({});
        await expect(browser.getEndpointUrl()).rejects.toThrow(BrowserError);
        await expect(browser.getEndpointUrl()).rejects.toThrow("Network down");
    });

    test("screenshot(page) when not initialized throws BrowserError", async () => {
        const session = createMockSession();
        const browser = new Browser(session);
        await expect(browser.screenshot({} as any)).rejects.toThrow(BrowserError);
    });

    test("screenshot(null) throws Error", async () => {
        const session = createMockSession();
        const browser = new Browser(session);
        await browser.initialize({});
        await expect(browser.screenshot(null as any)).rejects.toThrow("cannot be null");
    });

    test("enableBrowserReplay is passed as enableRecord", async () => {
        const session = createMockSession();
        session.enableBrowserReplay = true;
        const browser = new Browser(session);
        await browser.initialize({});
        const call = session.getClient().initBrowser.mock.calls[0][0];
        expect(call.browserOption?.enableRecord).toBe(true);
    });
});
