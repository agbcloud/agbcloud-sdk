/** Load typescript/.env so AGB_API_KEY, AGB_ENDPOINT etc. are available when running Jest (e.g. from VS Code Test Explorer). */
require("dotenv").config({ path: require("path").join(__dirname, "..", ".env") });
