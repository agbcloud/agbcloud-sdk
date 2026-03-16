import * as fs from "fs";
import { logInfo, logError, logWarn, logDebug } from "../../logger";

/* eslint-disable @typescript-eslint/no-explicit-any */

export interface ScreenFingerprint {
    availHeight: number;
    availWidth: number;
    availTop: number;
    availLeft: number;
    colorDepth: number;
    height: number;
    pixelDepth: number;
    width: number;
    devicePixelRatio: number;
    pageXOffset: number;
    pageYOffset: number;
    innerHeight: number;
    outerHeight: number;
    outerWidth: number;
    innerWidth: number;
    screenX: number;
    clientWidth: number;
    clientHeight: number;
    hasHDR: boolean;
}

export interface Brand {
    brand: string;
    version: string;
}

export interface UserAgentData {
    brands: Brand[];
    mobile: boolean;
    platform: string;
    architecture: string;
    bitness: string;
    fullVersionList: Brand[];
    model: string;
    platformVersion: string;
    uaFullVersion: string;
}

export interface ExtraProperties {
    vendorFlavors: string[];
    isBluetoothSupported: boolean;
    globalPrivacyControl?: any;
    pdfViewerEnabled: boolean;
    installedApps: any[];
}

export interface NavigatorFingerprint {
    userAgent: string;
    userAgentData: UserAgentData;
    doNotTrack: string;
    appCodeName: string;
    appName: string;
    appVersion: string;
    oscpu: string;
    webdriver: string;
    language: string;
    languages: string[];
    platform: string;
    deviceMemory?: number;
    hardwareConcurrency: number;
    product: string;
    productSub: string;
    vendor: string;
    vendorSub: string;
    maxTouchPoints?: number;
    extraProperties: ExtraProperties;
}

export interface VideoCard {
    renderer: string;
    vendor: string;
}

export interface Fingerprint {
    screen: ScreenFingerprint;
    navigator: NavigatorFingerprint;
    videoCodecs: Record<string, string>;
    audioCodecs: Record<string, string>;
    pluginsData: Record<string, string>;
    battery?: Record<string, string>;
    videoCard: VideoCard;
    multimediaDevices: string[];
    fonts: string[];
    mockWebRTC: boolean;
    slim?: boolean;
}

// ─── FingerprintFormat ──────────────────────────────────────

export class FingerprintFormat {
    fingerprint: Fingerprint;
    headers: Record<string, string>;

    constructor(fingerprint: Fingerprint, headers: Record<string, string>) {
        this.fingerprint = fingerprint;
        this.headers = headers;
    }

    /**
     * Load fingerprint format from dict or JSON string.
     *
     * Args:
     *   data: Dictionary or JSON string containing fingerprint data.
     *
     * Returns:
     *   FingerprintFormat instance.
     */
    static load(data: string | Record<string, any>): FingerprintFormat {
        if (typeof data === "string") {
            return FingerprintFormat.fromJson(data);
        }
        return FingerprintFormat.fromDict(data);
    }

    toDict(): Record<string, any> {
        return {
            fingerprint: this.fingerprint,
            headers: this.headers,
        };
    }

    toJson(indent = 2): string {
        return JSON.stringify(this.toDict(), null, indent);
    }

    static fromJson(jsonStr: string): FingerprintFormat {
        const data = JSON.parse(jsonStr);
        return FingerprintFormat.fromDict(data);
    }

    static fromDict(data: Record<string, any>): FingerprintFormat {
        if (!data || typeof data !== "object") {
            throw new Error("Invalid data: expected an object");
        }

        const fpDict = data.fingerprint || {};
        const headersDict = data.headers || {};

        const screenDict = fpDict.screen || {};
        const screen: ScreenFingerprint = {
            availHeight: screenDict.availHeight || 0,
            availWidth: screenDict.availWidth || 0,
            availTop: screenDict.availTop || 0,
            availLeft: screenDict.availLeft || 0,
            colorDepth: screenDict.colorDepth || 24,
            height: screenDict.height || 0,
            pixelDepth: screenDict.pixelDepth || 24,
            width: screenDict.width || 0,
            devicePixelRatio: screenDict.devicePixelRatio || 1,
            pageXOffset: screenDict.pageXOffset || 0,
            pageYOffset: screenDict.pageYOffset || 0,
            innerHeight: screenDict.innerHeight || 0,
            outerHeight: screenDict.outerHeight || 0,
            outerWidth: screenDict.outerWidth || 0,
            innerWidth: screenDict.innerWidth || 0,
            screenX: screenDict.screenX || 0,
            clientWidth: screenDict.clientWidth || 0,
            clientHeight: screenDict.clientHeight || 0,
            hasHDR: screenDict.hasHDR || false,
        };

        const navDict = fpDict.navigator || {};
        const uaDataDict = navDict.userAgentData || {};

        const brands: Brand[] = [];
        if (Array.isArray(uaDataDict.brands)) {
            for (const b of uaDataDict.brands) {
                if (b && typeof b === "object") {
                    brands.push({ brand: b.brand || "", version: b.version || "" });
                }
            }
        }

        const fullVersionList: Brand[] = [];
        if (Array.isArray(uaDataDict.fullVersionList)) {
            for (const b of uaDataDict.fullVersionList) {
                if (b && typeof b === "object") {
                    fullVersionList.push({ brand: b.brand || "", version: b.version || "" });
                }
            }
        }

        const userAgentData: UserAgentData = {
            brands,
            mobile: uaDataDict.mobile || false,
            platform: uaDataDict.platform || "",
            architecture: uaDataDict.architecture || "",
            bitness: uaDataDict.bitness || "",
            fullVersionList,
            model: uaDataDict.model || "",
            platformVersion: uaDataDict.platformVersion || "",
            uaFullVersion: uaDataDict.uaFullVersion || "",
        };

        const extraDict = navDict.extraProperties || {};
        const extraProperties: ExtraProperties = {
            vendorFlavors: extraDict.vendorFlavors || [],
            isBluetoothSupported: extraDict.isBluetoothSupported || false,
            globalPrivacyControl: extraDict.globalPrivacyControl,
            pdfViewerEnabled: extraDict.pdfViewerEnabled !== false,
            installedApps: extraDict.installedApps || [],
        };

        const navigator: NavigatorFingerprint = {
            userAgent: navDict.userAgent || "",
            userAgentData,
            doNotTrack: navDict.doNotTrack || "",
            appCodeName: navDict.appCodeName || "",
            appName: navDict.appName || "",
            appVersion: navDict.appVersion || "",
            oscpu: navDict.oscpu || "",
            webdriver: navDict.webdriver || "",
            language: navDict.language || "",
            languages: navDict.languages || [],
            platform: navDict.platform || "",
            deviceMemory: navDict.deviceMemory,
            hardwareConcurrency: navDict.hardwareConcurrency || 8,
            product: navDict.product || "",
            productSub: navDict.productSub || "",
            vendor: navDict.vendor || "",
            vendorSub: navDict.vendorSub || "",
            maxTouchPoints: navDict.maxTouchPoints,
            extraProperties,
        };

        const vcDict = fpDict.videoCard || {};
        const videoCard: VideoCard = {
            renderer: vcDict.renderer || "Unknown",
            vendor: vcDict.vendor || "Unknown",
        };

        const fingerprint: Fingerprint = {
            screen,
            navigator,
            videoCodecs: fpDict.videoCodecs || {},
            audioCodecs: fpDict.audioCodecs || {},
            pluginsData: fpDict.pluginsData || {},
            battery: fpDict.battery,
            videoCard,
            multimediaDevices: fpDict.multimediaDevices || [],
            fonts: fpDict.fonts || [],
            mockWebRTC: fpDict.mockWebRTC || false,
            slim: fpDict.slim,
        };

        return new FingerprintFormat(fingerprint, headersDict);
    }

    /**
     * Create FingerprintFormat directly using component interfaces.
     */
    static create(
        screen: ScreenFingerprint,
        navigator: NavigatorFingerprint,
        videoCard: VideoCard,
        headers: Record<string, string>,
        videoCodecs?: Record<string, string>,
        audioCodecs?: Record<string, string>,
        pluginsData?: Record<string, string>,
        battery?: Record<string, string>,
        multimediaDevices?: string[],
        fonts?: string[],
        mockWebRTC = false,
        slim?: boolean,
    ): FingerprintFormat {
        const fingerprint: Fingerprint = {
            screen,
            navigator,
            videoCodecs: videoCodecs || {},
            audioCodecs: audioCodecs || {},
            pluginsData: pluginsData || {},
            battery,
            videoCard,
            multimediaDevices: multimediaDevices || [],
            fonts: fonts || [],
            mockWebRTC,
            slim,
        };
        return new FingerprintFormat(fingerprint, headers);
    }
}

// ─── BrowserFingerprintGenerator ────────────────────────────

/**
 * Fingerprint extraction JS snippet executed in the browser page context.
 * Kept as a plain string to avoid bundler issues with `page.evaluate`.
 */
const FINGERPRINT_EXTRACTION_JS = `
async function() {
    function getAudioCodecs() {
        const audio = document.createElement('audio');
        return {
            ogg: audio.canPlayType('audio/ogg; codecs="vorbis"') || '',
            mp3: audio.canPlayType('audio/mpeg') || '',
            wav: audio.canPlayType('audio/wav; codecs="1"') || '',
            m4a: audio.canPlayType('audio/x-m4a') || '',
            aac: audio.canPlayType('audio/aac') || ''
        };
    }
    function getVideoCodecs() {
        const video = document.createElement('video');
        return {
            ogg: video.canPlayType('video/ogg; codecs="theora"') || '',
            h264: video.canPlayType('video/mp4; codecs="avc1.42E01E"') || '',
            webm: video.canPlayType('video/webm; codecs="vp8, vorbis"') || ''
        };
    }
    function getPluginsData() {
        const plugins = []; const mimeTypes = [];
        for (let i = 0; i < navigator.plugins.length; i++) {
            const p = navigator.plugins[i];
            const pd = { name: p.name, description: p.description, filename: p.filename, mimeTypes: [] };
            for (let j = 0; j < p.length; j++) {
                const m = p[j];
                pd.mimeTypes.push({ type: m.type, suffixes: m.suffixes, description: m.description, enabledPlugin: p.name });
                mimeTypes.push(m.description + '~~' + m.type + '~~' + m.suffixes);
            }
            plugins.push(pd);
        }
        return { plugins, mimeTypes };
    }
    async function getBatteryInfo() {
        try { if ('getBattery' in navigator) { const b = await navigator.getBattery(); return { charging: b.charging, chargingTime: b.chargingTime, dischargingTime: b.dischargingTime, level: b.level }; } } catch(e) {}
        return { charging: true, chargingTime: 0, dischargingTime: null, level: 1 };
    }
    function getWebGLInfo() {
        try { const c = document.createElement('canvas'); const gl = c.getContext('webgl') || c.getContext('experimental-webgl'); if (gl) { const d = gl.getExtension('WEBGL_debug_renderer_info'); return { renderer: d ? gl.getParameter(d.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER), vendor: d ? gl.getParameter(d.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR) }; } } catch(e) {}
        return { renderer: 'Adreno (TM) 735', vendor: 'Qualcomm' };
    }
    async function getMultimediaDevices() {
        try { if ('mediaDevices' in navigator && 'enumerateDevices' in navigator.mediaDevices) { const devs = await navigator.mediaDevices.enumerateDevices(); const sp = [], mi = [], wc = []; devs.forEach(function(d) { const di = { deviceId: d.deviceId||'', kind: d.kind, label: d.label||'', groupId: d.groupId||'' }; if (d.kind==='audiooutput') sp.push(di); else if (d.kind==='audioinput') mi.push(di); else if (d.kind==='videoinput') wc.push(di); }); return { speakers: sp, micros: mi, webcams: wc }; } } catch(e) {}
        return { speakers: [{ deviceId:'', kind:'audiooutput', label:'', groupId:'' }], micros: [{ deviceId:'', kind:'audioinput', label:'', groupId:'' }], webcams: [] };
    }
    function getFonts() {
        const tf = ['Arial','Helvetica','Times New Roman','Courier New','Verdana','Georgia','Palatino','Garamond','Bookman','Comic Sans MS','Trebuchet MS','Arial Black','Impact'];
        const af = []; const ts = 'mmmmmmmmmmlli'; const sz = '72px'; const bw = {}; const bh = {};
        const cv = document.createElement('canvas'); const ctx = cv.getContext('2d'); if (!ctx) return af;
        const df = ['monospace','sans-serif','serif'];
        df.forEach(function(f) { ctx.font = sz + ' ' + f; const m = ctx.measureText(ts); bw[f] = m.width; bh[f] = m.actualBoundingBoxAscent + m.actualBoundingBoxDescent; });
        tf.forEach(function(f) { let det = false; df.forEach(function(bf) { ctx.font = sz + ' ' + f + ', ' + bf; const m = ctx.measureText(ts); if (m.width !== bw[bf] || (m.actualBoundingBoxAscent + m.actualBoundingBoxDescent) !== bh[bf]) det = true; }); if (det) af.push(f); });
        return af;
    }
    const batteryInfo = await getBatteryInfo();
    const multimediaDevices = await getMultimediaDevices();
    return {
        screen: { availTop: screen.availTop, availLeft: screen.availLeft, pageXOffset: window.pageXOffset, pageYOffset: window.pageYOffset, screenX: window.screenX, hasHDR: screen.colorDepth > 24, width: screen.width, height: screen.height, availWidth: screen.availWidth, availHeight: screen.availHeight, clientWidth: document.documentElement.clientWidth, clientHeight: document.documentElement.clientHeight, innerWidth: window.innerWidth, innerHeight: window.innerHeight, outerWidth: window.outerWidth, outerHeight: window.outerHeight, colorDepth: screen.colorDepth, pixelDepth: screen.pixelDepth, devicePixelRatio: window.devicePixelRatio },
        navigator: { userAgent: navigator.userAgent, userAgentData: navigator.userAgentData ? { brands: navigator.userAgentData.brands||[], mobile: navigator.userAgentData.mobile||false, platform: navigator.userAgentData.platform||'' } : null, language: navigator.language, languages: navigator.languages||[], platform: navigator.platform, deviceMemory: navigator.deviceMemory||8, hardwareConcurrency: navigator.hardwareConcurrency||8, maxTouchPoints: navigator.maxTouchPoints||0, product: navigator.product, productSub: navigator.productSub, vendor: navigator.vendor, vendorSub: navigator.vendorSub, doNotTrack: navigator.doNotTrack, appCodeName: navigator.appCodeName, appName: navigator.appName, appVersion: navigator.appVersion, oscpu: navigator.oscpu, extraProperties: { vendorFlavors: ['chrome'], globalPrivacyControl: navigator.globalPrivacyControl||null, pdfViewerEnabled: navigator.pdfViewerEnabled||true, installedApps: [] }, webdriver: false },
        audioCodecs: getAudioCodecs(), videoCodecs: getVideoCodecs(), pluginsData: getPluginsData(), battery: batteryInfo, videoCard: getWebGLInfo(), multimediaDevices: multimediaDevices, fonts: getFonts(), mockWebRTC: false, slim: false
    };
}
`;

const KEY_HEADERS = [
    "sec-ch-ua", "sec-ch-ua-mobile", "sec-ch-ua-platform",
    "upgrade-insecure-requests", "user-agent", "accept",
    "sec-fetch-site", "sec-fetch-mode", "sec-fetch-user",
    "sec-fetch-dest", "accept-encoding", "accept-language",
];

/**
 * Browser fingerprint generator.
 * Uses Playwright to launch a local browser and collect fingerprint information
 * including screen properties, navigator data, codecs, plugins, WebGL info,
 * and HTTP headers.
 *
 * Requires `playwright` as a peer dependency.
 */
export class BrowserFingerprintGenerator {
    private headless: boolean;
    private useChromeChannel: boolean;

    constructor(options: { headless?: boolean; useChromeChannel?: boolean } = {}) {
        this.headless = options.headless ?? false;
        this.useChromeChannel = options.useChromeChannel ?? true;
    }

    /**
     * Extract comprehensive browser fingerprint using Playwright.
     *
     * Returns:
     *   FingerprintFormat or null if generation failed.
     */
    async generateFingerprint(): Promise<FingerprintFormat | null> {
        try {
            logInfo("Starting fingerprint generation");

            // Dynamic import so playwright is an optional peer dependency
            const { chromium } = await import("playwright");

            const launchOptions: Record<string, unknown> = {
                headless: this.headless,
                args: ["--start-maximized"],
            };
            if (this.useChromeChannel) {
                launchOptions.channel = "chrome";
            }

            const browser = await chromium.launch(launchOptions as any);
            const context = await browser.newContext({ viewport: null });
            const page = await context.newPage();

            await page.goto("about:blank");
            logInfo("Extracting comprehensive browser fingerprint...");

            const fingerprintData = await this.extractFingerprintData(page);
            const headersData = await this.extractHeadersData(page);

            await browser.close();

            const fingerprintFormat = FingerprintFormat.fromDict({
                fingerprint: fingerprintData,
                headers: headersData,
            });

            logInfo("Fingerprint generation completed successfully!");
            return fingerprintFormat;
        } catch (e) {
            logError(`Error generating fingerprint: ${e}`);
            return null;
        }
    }

    /**
     * Extract fingerprint data from a Playwright page (screen, navigator, codecs, etc.).
     *
     * @param page - Playwright Page instance (e.g. from context.newPage()).
     * @returns The raw fingerprint object (compatible with FingerprintFormat.fromDict).
     */
    async extractFingerprintData(page: any): Promise<Record<string, unknown>> {
        return (await page.evaluate(FINGERPRINT_EXTRACTION_JS)) as Record<string, unknown>;
    }

    /**
     * Extract browser fingerprint and save to a JSON file.
     *
     * Args:
     *   outputFilename: Output file path (default: "fingerprint_output.json").
     *
     * Returns:
     *   true if succeeded, false otherwise.
     */
    async generateFingerprintToFile(
        outputFilename = "fingerprint_output.json",
    ): Promise<boolean> {
        try {
            logInfo(`Starting fingerprint generation, output file: ${outputFilename}`);

            const fpFormat = await this.generateFingerprint();
            if (!fpFormat) {
                logError("Failed to generate fingerprint data");
                return false;
            }

            const json = fpFormat.toJson(2);
            fs.writeFileSync(outputFilename, json, "utf8");
            logInfo(`Fingerprint data saved to ${outputFilename}`);
            return true;
        } catch (e) {
            logError(`Error generating fingerprint to file: ${e}`);
            return false;
        }
    }

    /**
     * Extract request headers from the page via https://httpbin.org/headers.
     * Returns only the key headers used for fingerprinting.
     *
     * @param page - Playwright Page instance.
     * @returns Record of header name -> value (key headers only).
     */
    async extractHeadersData(page: any): Promise<Record<string, string>> {
        try {
            logDebug("Getting request headers...");
            await page.goto("https://httpbin.org/headers", { waitUntil: "networkidle" });

            const allHeaders: Record<string, string> = await page.evaluate(`
                (function() {
                    try {
                        const preElement = document.querySelector('pre');
                        if (preElement) {
                            const data = JSON.parse(preElement.textContent || '{}');
                            return data.headers || {};
                        }
                    } catch (e) {}
                    return {};
                })()
            `);

            const allHeadersLower: Record<string, string> = {};
            for (const [k, v] of Object.entries(allHeaders)) {
                allHeadersLower[k.toLowerCase()] = v;
            }

            const result: Record<string, string> = {};
            for (const header of KEY_HEADERS) {
                const headerLower = header.toLowerCase();
                if (headerLower in allHeadersLower) {
                    result[header] = allHeadersLower[headerLower];
                }
            }
            return result;
        } catch (e) {
            logWarn(`Failed to extract headers: ${e}`);
            return {};
        }
    }
}
