/** @type {import('jest').Config} */
module.exports = {
    preset: "ts-jest",
    testEnvironment: "node",
    setupFiles: ["<rootDir>/tests/loadEnv.js"],
    roots: ["<rootDir>/tests"],
    moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json"],
    testMatch: ["**/*.test.ts"],
    transform: {
        "^.+\\.ts$": "ts-jest",
    },
};
