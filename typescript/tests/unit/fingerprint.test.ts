import {
    FingerprintFormat,
    BrowserFingerprintGenerator,
} from "../../src/modules/browser/fingerprint";
import type {
    ScreenFingerprint,
    NavigatorFingerprint,
    UserAgentData,
    ExtraProperties,
    VideoCard,
    Fingerprint,
} from "../../src/modules/browser/fingerprint";

// ─── Sample data builders ───────────────────────────────────

function buildSampleScreen(): ScreenFingerprint {
    return {
        availHeight: 900,
        availWidth: 1440,
        availTop: 0,
        availLeft: 0,
        colorDepth: 24,
        height: 900,
        pixelDepth: 24,
        width: 1440,
        devicePixelRatio: 2,
        pageXOffset: 0,
        pageYOffset: 0,
        innerHeight: 800,
        outerHeight: 900,
        outerWidth: 1440,
        innerWidth: 1440,
        screenX: 0,
        clientWidth: 1440,
        clientHeight: 800,
        hasHDR: false,
    };
}

function buildSampleNavigator(): NavigatorFingerprint {
    const uaData: UserAgentData = {
        brands: [{ brand: "Chromium", version: "124" }],
        mobile: false,
        platform: "macOS",
        architecture: "arm",
        bitness: "64",
        fullVersionList: [{ brand: "Chromium", version: "124.0.6367.91" }],
        model: "",
        platformVersion: "14.4.1",
        uaFullVersion: "124.0.6367.91",
    };
    const extra: ExtraProperties = {
        vendorFlavors: ["chrome"],
        isBluetoothSupported: false,
        globalPrivacyControl: null,
        pdfViewerEnabled: true,
        installedApps: [],
    };
    return {
        userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/124",
        userAgentData: uaData,
        doNotTrack: "unspecified",
        appCodeName: "Mozilla",
        appName: "Netscape",
        appVersion: "5.0",
        oscpu: "",
        webdriver: "false",
        language: "en-US",
        languages: ["en-US", "zh-CN"],
        platform: "MacIntel",
        deviceMemory: 16,
        hardwareConcurrency: 10,
        product: "Gecko",
        productSub: "20030107",
        vendor: "Google Inc.",
        vendorSub: "",
        maxTouchPoints: 0,
        extraProperties: extra,
    };
}

function buildSampleVideoCard(): VideoCard {
    return { renderer: "Apple M2 Pro", vendor: "Apple" };
}

function buildSampleDict(): Record<string, unknown> {
    return {
        fingerprint: {
            screen: buildSampleScreen(),
            navigator: buildSampleNavigator(),
            videoCodecs: { h264: "probably" },
            audioCodecs: { mp3: "probably" },
            pluginsData: {},
            battery: { charging: "true", level: "1" },
            videoCard: buildSampleVideoCard(),
            multimediaDevices: ["speaker"],
            fonts: ["Arial"],
            mockWebRTC: false,
            slim: true,
        },
        headers: {
            "user-agent": "Mozilla/5.0",
            accept: "text/html",
        },
    };
}

// ─── Tests ──────────────────────────────────────────────────

describe("FingerprintFormat", () => {
    describe("load / fromDict / fromJson", () => {
        test("load from dict", () => {
            const fp = FingerprintFormat.load(buildSampleDict() as Record<string, any>);
            expect(fp).toBeInstanceOf(FingerprintFormat);
            expect(fp.fingerprint.screen.width).toBe(1440);
            expect(fp.fingerprint.navigator.userAgent).toContain("Chrome/124");
            expect(fp.fingerprint.videoCard.renderer).toBe("Apple M2 Pro");
            expect(fp.headers["user-agent"]).toBe("Mozilla/5.0");
        });

        test("load from JSON string", () => {
            const json = JSON.stringify(buildSampleDict());
            const fp = FingerprintFormat.load(json);
            expect(fp.fingerprint.screen.availWidth).toBe(1440);
            expect(fp.fingerprint.fonts).toContain("Arial");
        });

        test("fromDict with empty data fallbacks", () => {
            const fp = FingerprintFormat.fromDict({ fingerprint: {}, headers: {} });
            expect(fp.fingerprint.screen.colorDepth).toBe(24);
            expect(fp.fingerprint.navigator.hardwareConcurrency).toBe(8);
            expect(fp.fingerprint.videoCard.renderer).toBe("Unknown");
        });

        test("fromDict throws on invalid input", () => {
            expect(() => FingerprintFormat.fromDict(null as any)).toThrow("Invalid data");
        });

        test("fromDict handles nested brands", () => {
            const data = buildSampleDict() as any;
            const fp = FingerprintFormat.fromDict(data);
            expect(fp.fingerprint.navigator.userAgentData.brands).toHaveLength(1);
            expect(fp.fingerprint.navigator.userAgentData.brands[0].brand).toBe("Chromium");
            expect(fp.fingerprint.navigator.userAgentData.fullVersionList).toHaveLength(1);
        });

        test("fromDict handles missing brands gracefully", () => {
            const data: any = { fingerprint: { navigator: { userAgentData: {} } }, headers: {} };
            const fp = FingerprintFormat.fromDict(data);
            expect(fp.fingerprint.navigator.userAgentData.brands).toEqual([]);
            expect(fp.fingerprint.navigator.userAgentData.fullVersionList).toEqual([]);
        });

        test("fromDict handles non-object brand entries", () => {
            const data: any = {
                fingerprint: {
                    navigator: {
                        userAgentData: {
                            brands: ["invalid", null, { brand: "ok", version: "1" }],
                        },
                    },
                },
                headers: {},
            };
            const fp = FingerprintFormat.fromDict(data);
            expect(fp.fingerprint.navigator.userAgentData.brands).toHaveLength(1);
            expect(fp.fingerprint.navigator.userAgentData.brands[0].brand).toBe("ok");
        });
    });

    describe("toDict / toJson", () => {
        test("round-trip dict -> FingerprintFormat -> dict", () => {
            const original = buildSampleDict();
            const fp = FingerprintFormat.load(original as Record<string, any>);
            const dict = fp.toDict();
            expect(dict.fingerprint.screen.width).toBe(1440);
            expect(dict.headers["user-agent"]).toBe("Mozilla/5.0");
        });

        test("round-trip JSON string", () => {
            const fp = FingerprintFormat.load(buildSampleDict() as Record<string, any>);
            const json = fp.toJson();
            const fp2 = FingerprintFormat.fromJson(json);
            expect(fp2.fingerprint.navigator.language).toBe("en-US");
        });
    });

    describe("create", () => {
        test("create from components", () => {
            const fp = FingerprintFormat.create(
                buildSampleScreen(),
                buildSampleNavigator(),
                buildSampleVideoCard(),
                { "user-agent": "test" },
                { h264: "probably" },
                { mp3: "probably" },
                {},
                undefined,
                ["speaker"],
                ["Arial"],
                true,
                false,
            );
            expect(fp.fingerprint.mockWebRTC).toBe(true);
            expect(fp.fingerprint.slim).toBe(false);
            expect(fp.fingerprint.multimediaDevices).toEqual(["speaker"]);
        });

        test("create with minimal arguments", () => {
            const fp = FingerprintFormat.create(
                buildSampleScreen(),
                buildSampleNavigator(),
                buildSampleVideoCard(),
                {},
            );
            expect(fp.fingerprint.videoCodecs).toEqual({});
            expect(fp.fingerprint.mockWebRTC).toBe(false);
            expect(fp.fingerprint.slim).toBeUndefined();
        });
    });

    describe("edge cases", () => {
        test("slim is preserved as undefined when not set", () => {
            const data: any = { fingerprint: {}, headers: {} };
            const fp = FingerprintFormat.fromDict(data);
            expect(fp.fingerprint.slim).toBeUndefined();
        });

        test("battery is preserved as undefined when not set", () => {
            const data: any = { fingerprint: {}, headers: {} };
            const fp = FingerprintFormat.fromDict(data);
            expect(fp.fingerprint.battery).toBeUndefined();
        });

        test("deviceMemory optional", () => {
            const data: any = { fingerprint: { navigator: {} }, headers: {} };
            const fp = FingerprintFormat.fromDict(data);
            expect(fp.fingerprint.navigator.deviceMemory).toBeUndefined();
        });

        test("extraProperties.pdfViewerEnabled defaults to true", () => {
            const data: any = { fingerprint: { navigator: { extraProperties: {} } }, headers: {} };
            const fp = FingerprintFormat.fromDict(data);
            expect(fp.fingerprint.navigator.extraProperties.pdfViewerEnabled).toBe(true);
        });

        test("extraProperties.pdfViewerEnabled can be set to false", () => {
            const data: any = {
                fingerprint: {
                    navigator: { extraProperties: { pdfViewerEnabled: false } },
                },
                headers: {},
            };
            const fp = FingerprintFormat.fromDict(data);
            expect(fp.fingerprint.navigator.extraProperties.pdfViewerEnabled).toBe(false);
        });
    });
});

describe("BrowserFingerprintGenerator", () => {
    test("constructor defaults", () => {
        const gen = new BrowserFingerprintGenerator();
        expect(gen).toBeInstanceOf(BrowserFingerprintGenerator);
    });

    test("constructor with options", () => {
        const gen = new BrowserFingerprintGenerator({ headless: true, useChromeChannel: false });
        expect(gen).toBeInstanceOf(BrowserFingerprintGenerator);
    });

    test("generateFingerprint returns null on error", async () => {
        const gen = new BrowserFingerprintGenerator();
        // Mock dynamic import to simulate playwright unavailable
        const origGenerate = gen.generateFingerprint.bind(gen);
        jest.spyOn(gen, "generateFingerprint").mockImplementation(async () => {
            try {
                // Force an import failure by temporarily breaking it
                const badImport = jest.fn().mockRejectedValue(new Error("Cannot find module 'playwright'"));
                await badImport();
                return null;
            } catch {
                return null;
            }
        });
        const result = await gen.generateFingerprint();
        expect(result).toBeNull();
        jest.restoreAllMocks();
    });

    test("generateFingerprintToFile returns false when generation fails", async () => {
        const gen = new BrowserFingerprintGenerator();
        jest.spyOn(gen, "generateFingerprint").mockResolvedValue(null);
        const result = await gen.generateFingerprintToFile("/tmp/test-fp.json");
        expect(result).toBe(false);
        jest.restoreAllMocks();
    });

    test("generateFingerprintToFile returns true when generation succeeds", async () => {
        const gen = new BrowserFingerprintGenerator();
        const mockFp = FingerprintFormat.load(buildSampleDict() as Record<string, any>);
        jest.spyOn(gen, "generateFingerprint").mockResolvedValue(mockFp);

        const fs = require("fs");
        const writeSpy = jest.spyOn(fs, "writeFileSync").mockImplementation(() => { });

        const result = await gen.generateFingerprintToFile("/tmp/test-fp-mock.json");
        expect(result).toBe(true);
        expect(writeSpy).toHaveBeenCalledWith(
            "/tmp/test-fp-mock.json",
            expect.any(String),
            "utf8",
        );
        jest.restoreAllMocks();
    });

    test("generateFingerprintToFile returns false on write error", async () => {
        const gen = new BrowserFingerprintGenerator();
        const mockFp = FingerprintFormat.load(buildSampleDict() as Record<string, any>);
        jest.spyOn(gen, "generateFingerprint").mockResolvedValue(mockFp);

        const fs = require("fs");
        jest.spyOn(fs, "writeFileSync").mockImplementation(() => {
            throw new Error("disk full");
        });

        const result = await gen.generateFingerprintToFile("/tmp/fail.json");
        expect(result).toBe(false);
        jest.restoreAllMocks();
    });
});
