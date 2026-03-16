import * as path from "path";
import * as fs from "fs";

export interface Config {
    endpoint: string;
    timeoutMs: number;
}

export interface ConfigOptions {
    endpoint?: string;
    timeoutMs?: number;
}

export function defaultConfig(): Config {
    return {
        endpoint: "sdk-api.agb.cloud",
        timeoutMs: 60000,
    };
}

function findDotEnvFile(startPath?: string): string | null {
    let currentDir = startPath || process.cwd();
    const root = path.parse(currentDir).root;

    while (currentDir !== root) {
        const envPath = path.join(currentDir, ".env");
        if (fs.existsSync(envPath)) {
            return envPath;
        }
        currentDir = path.dirname(currentDir);
    }
    return null;
}

export function loadDotEnvWithFallback(customEnvPath?: string): void {
    try {
        const dotenv = require("dotenv");
        if (customEnvPath && fs.existsSync(customEnvPath)) {
            dotenv.config({ path: customEnvPath });
            return;
        }
        const envFile = findDotEnvFile();
        if (envFile) {
            dotenv.config({ path: envFile });
        }
    } catch {
        // dotenv not available or failed to load
    }
}

/**
 * Load configuration with precedence:
 * 1. Explicit config in code
 * 2. Environment variables (AGB_ENDPOINT, AGB_TIMEOUT_MS)
 * 3. .env file
 * 4. Default configuration
 */
export function loadConfig(
    customConfig?: ConfigOptions,
    customEnvPath?: string,
): Config {
    loadDotEnvWithFallback(customEnvPath);

    const config = defaultConfig();

    if (customConfig?.endpoint) {
        config.endpoint = customConfig.endpoint;
    } else if (process.env.AGB_ENDPOINT) {
        config.endpoint = process.env.AGB_ENDPOINT;
    }

    if (customConfig?.timeoutMs) {
        config.timeoutMs = customConfig.timeoutMs;
    } else if (process.env.AGB_TIMEOUT_MS) {
        config.timeoutMs = parseInt(process.env.AGB_TIMEOUT_MS, 10);
    }

    return config;
}
