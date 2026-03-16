export const VERSION = "0.10.0";
export const IS_RELEASE = false;

export function getSdkVersion(): string {
    return VERSION;
}

export function isReleaseVersion(): boolean {
    return IS_RELEASE;
}
