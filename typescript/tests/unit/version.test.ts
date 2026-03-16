import { getSdkVersion, isReleaseVersion, VERSION } from "../../src/version";

describe("Version", () => {
    test("VERSION is a non-empty string", () => {
        expect(typeof VERSION).toBe("string");
        expect(VERSION.length).toBeGreaterThan(0);
    });

    test("getSdkVersion returns VERSION", () => {
        expect(getSdkVersion()).toBe(VERSION);
    });

    test("isReleaseVersion returns a boolean", () => {
        expect(typeof isReleaseVersion()).toBe("boolean");
    });
});
