/**
 * Integration tests for browser fingerprint configuration.
 * Reference: python/tests/integration/test_agb_browser_fingerprint.py
 *
 * Tests that browser initialization accepts fingerprint options and persists them.
 */
import { createAGB, createTestSession, deleteTestSession } from "./setup";
import { FingerprintFormat } from "../../src/modules/browser/fingerprint";
import type { AGB } from "../../src/agb";
import type { Session } from "../../src/session";

jest.setTimeout(300_000);

function sleep(ms: number) {
    return new Promise((r) => setTimeout(r, ms));
}

async function initBrowserWithRetry(
    session: Session,
    options?: Record<string, unknown>,
    maxRetries = 3,
): Promise<boolean> {
    for (let i = 0; i <= maxRetries; i++) {
        const ok = await session.browser.initialize(options ?? {});
        if (ok) return true;
        await sleep(5000);
    }
    return false;
}

describe("Browser fingerprint (integration)", () => {
    let agb: AGB;
    let session: Session;

    beforeAll(async () => {
        agb = createAGB();
        session = await createTestSession(agb, "agb-browser-use-1");
    });

    afterAll(async () => {
        try { await session.browser.destroy(); } catch { /* ignore */ }
        await deleteTestSession(agb, session);
    });

    test("initialize browser with custom fingerprint", async () => {
        const ok = await initBrowserWithRetry(session, {
            fingerprint: {
                userAgent: "Mozilla/5.0 FingerprintTest",
                locale: "en-US",
                platform: "MacIntel",
            },
        });
        expect(ok).toBe(true);
    });

    test("re-initialize with different fingerprint", async () => {
        await session.browser.destroy();

        const ok = await initBrowserWithRetry(session, {
            fingerprint: {
                userAgent: "Mozilla/5.0 FingerprintTest2",
                locale: "zh-CN",
                timezone: "Asia/Shanghai",
            },
        });
        expect(ok).toBe(true);
    });

    test("FingerprintFormat load round-trip", () => {
        const sampleData = {
            fingerprint: {
                screen: {
                    availHeight: 900, availWidth: 1440,
                    availTop: 0, availLeft: 0,
                    colorDepth: 24, height: 900, pixelDepth: 24, width: 1440,
                    devicePixelRatio: 2,
                    pageXOffset: 0, pageYOffset: 0,
                    innerHeight: 800, outerHeight: 900,
                    outerWidth: 1440, innerWidth: 1440,
                    screenX: 0, clientWidth: 1440, clientHeight: 800,
                    hasHDR: false,
                },
                navigator: {
                    userAgent: "Mozilla/5.0 Test",
                    userAgentData: {
                        brands: [], mobile: false, platform: "macOS",
                        architecture: "", bitness: "", fullVersionList: [],
                        model: "", platformVersion: "", uaFullVersion: ""
                    },
                    doNotTrack: "", appCodeName: "Mozilla", appName: "Netscape",
                    appVersion: "5.0", oscpu: "", webdriver: "false",
                    language: "en-US", languages: ["en-US"],
                    platform: "MacIntel", hardwareConcurrency: 8,
                    product: "Gecko", productSub: "20030107",
                    vendor: "Google Inc.", vendorSub: "",
                    extraProperties: {
                        vendorFlavors: [], isBluetoothSupported: false,
                        pdfViewerEnabled: true, installedApps: []
                    },
                },
                videoCodecs: {}, audioCodecs: {}, pluginsData: {},
                videoCard: { renderer: "Apple", vendor: "Apple" },
                multimediaDevices: [], fonts: [], mockWebRTC: false,
            },
            headers: { "user-agent": "Mozilla/5.0 Test" },
        };

        const fp = FingerprintFormat.load(sampleData);
        expect(fp.fingerprint.screen.width).toBe(1440);

        const json = fp.toJson();
        const fp2 = FingerprintFormat.load(json);
        expect(fp2.fingerprint.navigator.userAgent).toBe("Mozilla/5.0 Test");
    });
});
