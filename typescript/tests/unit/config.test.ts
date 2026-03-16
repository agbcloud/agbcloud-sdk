import { defaultConfig, loadConfig } from "../../src/config";

describe("Config", () => {
    const originalEnv = process.env;

    beforeEach(() => {
        process.env = { ...originalEnv };
    });

    afterAll(() => {
        process.env = originalEnv;
    });

    test("defaultConfig returns expected defaults", () => {
        const config = defaultConfig();
        expect(config.endpoint).toBe("sdk-api.agb.cloud");
        expect(config.timeoutMs).toBe(60000);
    });

    test("loadConfig with custom values", () => {
        const config = loadConfig({
            endpoint: "custom.endpoint.com",
            timeoutMs: 30000,
        });
        expect(config.endpoint).toBe("custom.endpoint.com");
        expect(config.timeoutMs).toBe(30000);
    });

    test("loadConfig reads from environment variables", () => {
        process.env.AGB_ENDPOINT = "env.endpoint.com";
        process.env.AGB_TIMEOUT_MS = "45000";
        const config = loadConfig();
        expect(config.endpoint).toBe("env.endpoint.com");
        expect(config.timeoutMs).toBe(45000);
    });

    test("explicit config takes precedence over env", () => {
        process.env.AGB_ENDPOINT = "env.endpoint.com";
        const config = loadConfig({ endpoint: "explicit.endpoint.com" });
        expect(config.endpoint).toBe("explicit.endpoint.com");
    });
});
