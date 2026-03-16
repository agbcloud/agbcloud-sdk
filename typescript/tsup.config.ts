import { defineConfig } from "tsup";

export default defineConfig({
    entry: ["src/index.ts"],
    format: ["cjs", "esm"],
    external: ["playwright", "playwright-core"],
    dts: true,
    sourcemap: true,
    clean: true,
    target: "es2020",
    outDir: "dist",
    outExtension({ format }) {
        return {
            js: format === "cjs" ? ".cjs" : ".mjs",
        };
    },
});
