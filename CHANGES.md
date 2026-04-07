# Changelog

## [0.12.0] - 2026-04-07

### New Features

- **WebSocket**: New websocket client module (`ws`) with integration tests; session-level websocket client initialization and cleanup with improved logging on deletion.
- **MCP Tools**: Add support for MCP tools in session — tool list parsing, `callMcpTool` routing, session URL handling, and additional session fields.
- **Screenshot (Python)**: `beta_take_screenshot` method in Screen module with fixed import order.
- **Screenshot (TypeScript)**: Sync `betaTakeScreenshot` API with unit and integration tests.
- **Execution Context**: New documentation for execution context module.

### Enhancements

- **MCP Routing**: MCP tool invocation smart routing pushed down to `BaseService`, aligning Python and TypeScript implementations.
- **TypeScript Exceptions**: Refactor exception classes with factory functions to eliminate duplicate code.
- **TypeScript**: Remove `enableBrowserReplay` feature; add union types for tool list and improve imports handling.
- **FileSystem Monitoring**: Enhance directory monitoring logic with ready event, baseline establishment flag, and execution error handling.
- **WebSocket**: Update ws exceptions with extra params; simplify ws client logic and error creation pattern.
- **API Consistency**: Rename `run_code` to `_run_code` and update related methods and docs across modules; update method calls for consistency across Python and TypeScript.
- **MIME Handling**: Improve MIME type handling and add default stream target.
- **Data Retrieval**: Improve data retrieval logic and add helper functions for type safety.
- **Testing**: Update session creation params and image ID for testing consistency across languages.

### Bug Fixes

- **Dependencies**: `websockets` is now a required dependency (was missing from install_requires).
- **Screenshot**: Fix `screen.beta_take_screenshot` integration test error; fix unit and integration test errors in code and screenshot modules.
- **TypeScript**: Add `callMcpTool` to mock sessions for `SessionLike` interface compliance; fix API doc generation error; add ws dependency and improve logging in TypeScript modules.
- **Tool List**: Handle empty tool list and improve content check logic.
- **Timeout**: Add timeout parameters to future results in sync client; improve exception handling in TypeScript modules.
- **FileSystem**: Correct parameter name for stop event in directory monitoring example.
- **Scripts**: Remove wrong option in CI script.

### Documentation, Testing & Chore

- **Release Automation**: Add release SOP, automation scripts, unified CI release pipeline, and GitHub Actions auto-release workflow.
- **Docs**: Add real-time streaming and websocket documentation; use "remote browser" wording and document stealth option in TypeScript API.
- **Docs Fixes**: Fix documentation issues found during review (dead links, formatting).
- **Testing**: Add websockets dependency for testing.
- **API Docs**: Auto-generated API reference documentation updated.
- **CI/CD**: Add pipeline for SDK sync to GitHub; unified release pipeline, changelog generation, version bump, and doc-check automation scripts.

## [0.11.0] - 2026-03-16

### Breaking Changes

- **listMcpTools (Python)**: Explicit `imageId` is now required (no silent default). Callers must pass `imageId` when listing MCP tools.

### New Features

- **TypeScript SDK**: Full TypeScript SDK for AGB (client, Session, Config, API layer, Command, Code, FileSystem, Browser, Computer, Extension, Context, exceptions, logger). API models split into 51 separate files.
- **getCdpLink**: New API in Python and TypeScript; sessionId as query parameter. Browser `get_endpoint_url` uses getCdpLink in Python.
- **BrowserAgent (TypeScript)**: `act`, `observe`, `extract`, `navigate`; async variants with time-based timeout; BrowserFingerprintGenerator and FingerprintFormat.
- **Session lifecycle**: Idle release timeout (configurable); refresh session idle time API (keep-alive). Docs for lifecycle, keep-alive, and resource_url validity (30 min).
- **Python**: `call_mcp_tool` delegated to BaseService to remove duplication; Session uses `_base_service`.
- **Module parity (TypeScript)**: FileSystem upload/download via pre-signed URLs, `transferPath`, `watchDir`; Computer.Window fullscreen/focusMode; Computer.App `stopByCmd`/`getVisible`; Browser `getOption`/`isInitialized`; Session `getAgb()`; new file-transfer module for OSS and context sync.
- **CI/CD**: TypeScript official release pipeline and script; npm build/publish pipeline; internal tnpm test publish; publish npm test to tnpm when patch is merged.
- **Documentation**: Single root README (Python + TypeScript quick start, docs, development); website and Discord URLs; TypeScript code examples in VitePress code-group tabs; API reference merged into `docs/api-reference` with python/ and typescript/; Session docs split (lifecycle, info, labels, list, mcp-tools); Context expanded (concepts, best practices, FAQ); call-for-use and captcha docs.

### Enhancements

- **Filesystem (Python)**: FileInfo type; FileChangeEvent eventType/pathType; readFile with `{ format: "bytes" }`; writeFile `create_new` mode; watchDirectory with AbortSignal; sync fallback (awaitSync); waitForTask uses `res.items ?? res.contextStatusData`; OSS cleanup after upload/download. Unit tests aligned to DEFAULT_CHUNK_SIZE 50KB.
- **Computer (Python/TS)**: MouseButton.DOUBLE_LEFT, drag(button); getPosition/getSize return CursorPosition/ScreenSize; get_installed_apps uses `ignore_system_app`. Browser: BrowserProxy managed type (user_id, isp, country, province, city).
- **TypeScript**: Response models gained requestId and field parsing; getters (getTotalCount, getExpireTime, etc.); `toJSON()` on Session, AGB, BaseService, ContextService, ContextManager, Computer to avoid circular serialization; Browser screenshot Playwright-only (MCP screenshot removed); interface signatures aligned with Python (Keyboard press/release, App start/listInstalled, FileSystem progressCallback, Extension cleanup). `AGB.get()` returns `session: null` when session is deleted or missing (typed as `Session | null`).
- **Project structure**: Python SDK moved under `python/` (agb/, tests/, pyproject.toml, etc.); CI, scripts, root README updated.

### Bug Fixes

- **MCP screenshot**: CallMcpToolResponse now extracts `type="image"` content when no text (screenshot tool returns image).
- **Extension upload (TS)**: Use `fetch` instead of axios to fix 403 OSS upload.
- **getCdpLink**: TypeScript sends empty JSON body and capitalized Authorization header; Python/TS tests fail explicitly instead of silent skip.
- **Extension upload message (TS)**: Use `errorMessage` instead of `url` on failure.
- **tsup (TS)**: Externalize playwright to fix ESM/CJS build (optional runtime dependency).
- **Docs**: VitePress angle bracket escaping for TS generics; dead links fixed (tutorial depth, Related Resources, quickstart, browser links); tutorial link path generation for absolute-style paths; CI copy logic so api-reference/python/ does not get nested subdirs.
- **Python**: mypy fixes (GetCdpLinkResponse, Browser/FileSystem __init__, Optional dicts, FileError duplicate, logging params, browser agent extract return types).
- **CI**: Subshell `(cd python && ...)` to prevent path duplication; job outputs for pass/fail; summary decoupled from test jobs; correct image ID and AGB_ENDPOINT for TS integration tests; continue-on-error to avoid fast-fail cascade; clone retries and git HTTP tuning for push-docs-to-github.

### Documentation, Testing & Chore

- **Docs**: TypeScript API docs auto-generation in pipeline (TypeDoc); doc-metadata and computer overview generation (sub-modules before container, exclude_methods). Removed session best-practices.md, troubleshooting.md; keep-alive folded into lifecycle.
- **Testing**: TypeScript unit tests (session, base-service, logger, api-response, command, code, filesystem, computer, browser, extension, context, context-manager, api models, http-client, client, file-transfer, agb, BrowserAgent, fingerprint); integration tests (all modules, browser, computer, file transfer, watchDir, MCP, advanced suites). Python unit coverage to ~83% (logger, code, computer submodules, file_system, context_manager); getCdpLink integration tests. Pre env uses agb-code-space-2; CICD script names optimized.
- **Chore**: Removed unused session management methods and models; trimmed keep-alive use-case examples; docs/dev/ in .gitignore; code formatting (agb, browser). Pause and resume was added then removed in this cycle and is not part of the release.

## [0.10.0] - 2026-02-09

This release focuses on **API Naming Simplification Phase 2** in the Computer module, the new **policy_id** parameter for session creation, and **OpenClaw examples** for Slack, Discord, and Telegram.

### Breaking Changes

- **API Naming Simplification Phase 2 (Computer Module)**: Interfaces previously flat in `session.computer` are now organized by sub-module (`mouse`, `keyboard`, `screen`, `window`, `app`). The legacy single `computer.py` has been removed. API mapping:
  - `session.computer.click_mouse(x, y)` → `session.computer.mouse.click(x, y)`
  - `session.computer.move_mouse(x, y)` → `session.computer.mouse.move(x, y)`
  - `session.computer.drag_mouse(x1, y1, x2, y2)` → `session.computer.mouse.drag(x1, y1, x2, y2)`
  - `session.computer.scroll(x, y, direction, amount)` → `session.computer.mouse.scroll(x, y, direction, amount)`
  - `session.computer.get_cursor_position()` → `session.computer.mouse.get_position()`
  - `session.computer.input_text(text)` → `session.computer.keyboard.type(text)`
  - `session.computer.press_keys(keys)` → `session.computer.keyboard.press(keys)`
  - `session.computer.release_keys(keys)` → `session.computer.keyboard.release(keys)`
  - `session.computer.list_root_windows()` → `session.computer.window.list_root_windows()`
  - `session.computer.get_active_window()` → `session.computer.window.get_active_window()`
  - `session.computer.activate_window(window_id)` → `session.computer.window.activate(window_id)`
  - `session.computer.close_window(window_id)` → `session.computer.window.close(window_id)`
  - `session.computer.maximize_window(window_id)` → `session.computer.window.maximize(window_id)`
  - `session.computer.minimize_window(window_id)` → `session.computer.window.minimize(window_id)`
  - `session.computer.restore_window(window_id)` → `session.computer.window.restore(window_id)`
  - `session.computer.resize_window(window_id, w, h)` → `session.computer.window.resize(window_id, w, h)`
  - `session.computer.fullscreen_window(window_id)` → `session.computer.window.fullscreen(window_id)`
  - `session.computer.focus_mode(on=True)` → `session.computer.window.focus_mode(on=True)`
  - `session.computer.get_installed_apps()` → `session.computer.app.list_installed()`
  - `session.computer.list_visible_apps()` → `session.computer.app.get_visible()`
  - `session.computer.start_app(name)` → `session.computer.app.start(name)`
  - `session.computer.stop_app_by_pname(pname)` → `session.computer.app.stop_by_pname(pname)`
  - `session.computer.stop_app_by_pid(pid)` → `session.computer.app.stop_by_pid(pid)`
  - `session.computer.stop_app_by_cmd(stop_cmd)` → `session.computer.app.stop_by_cmd(stop_cmd)`
  - `session.computer.get_screen_size()` → `session.computer.screen.get_size()`
  - `session.computer.screenshot()` → `session.computer.screen.capture()`
- Implementation aligned with original behavior: unified log operation names, restored return types, and corrected mouse button validation and screen capture return types.

### New Features

- **policy_id**: `CreateSessionParams` adds `policy_id`; the create-session request supports `mcpPolicyId` for policy-scoped sessions.
- **OpenClaw examples**: Three example configurations for IM integrations:
  - **Slack** – configuration and usage with OpenClaw
  - **Discord** – configuration and usage with OpenClaw
  - **Telegram** – configuration and usage with OpenClaw (including README mention)

### Other Enhancements

- API call log level changed from info to debug
- aiohttp uses certifi for SSL context (macOS/Windows)
- Screenshot examples add retry and better SSL error handling
- Screen module: improved `result.data` parsing for string and dict
- App/window error handling improved; `get_active_window` raises `RuntimeError` on failure; window JSON errors return None

### Bug Fixes

- Added missing `request_id` on `AppOperationResult` / `ApplicationManager`
- Fixed example indentation and return types (`app.start()`, `screen.capture()`)
- Keyboard `combo` letter keys normalized to lowercase
- Fixed pytest imports (pythonpath, project root, `functional_helpers`)
- Integration test fixes for `list_installed`, cursor validation, scroll API, and `window_operations.py` app selection

### Documentation, Testing & Chore

- Docs auto-generated and aligned with 26 API specification; example formatting and comments updated.
- Browser fingerprint and computer integration tests improved; timeout test for 1s minimum; added Playwright connect test.
- Website host changed to agb.cloud.

## [0.9.0] - 2026-01-23

### Breaking Changes
- **API Naming Simplification**: Major API renaming for consistency and simplicity:
  - `session.code.run_code()` → `session.code.run()`
  - `session.command.execute_command()` → `session.command.execute()`
  - `session.file_system` → `session.file`
  - `session.file.watch()` → `session.file.watch_dir()`
  - `session.file.get_file_transfer_context_path()` → `session.file.transfer_path()`
  - File system methods simplified: `read_file()` → `read()`, `write_file()` → `write()`, `delete_file()` → `remove()`, `list_directory()` → `list()`, `get_file_info()` → `info()`, `create_directory()` → `mkdir()`, `move_file()` → `move()`, `edit_file()` → `edit()`, `read_multiple_files()` → `read_batch()`, `search_files()` → `search()`

### New Features
- **Session Metrics**: Added session metrics tracking functionality to retrieve resource usage and performance metrics
- **MCP Tool Calling**: Added MCP (Model Context Protocol) tool calling methods to Session class for direct tool invocation
- **Multiple Results Support**: Enhanced code execution to support multiple result types with comprehensive documentation

### Enhancements
- **Error Handling**: Improved error handling for file transfer operations:
  - Specific handling for `httpx.ConnectError` (network connection issues)
  - Specific handling for `httpx.TimeoutException` (timeout issues)
  - Clearer error messages for network-related failures
- **File Transfer**: Improved error handling in `transfer_path()` method with better context initialization checks
- **Documentation**:
  - Added comprehensive MCP tool calling documentation and examples
  - Updated API documentation to reflect new simplified method names
  - Added session metrics documentation and examples
  - Fixed code execution result field usage in documentation
  - Updated MCP guide URLs to v2

### Refactoring
- **Session Class**: Removed unnecessary `BaseService` inheritance from Session class
- **Test Infrastructure**: Optimized session creation in integration tests
- **Code Cleanup**: Removed temporary API rename verification scripts

### Testing & CI/CD
- **Test Coverage**: Reached 80% unit test coverage gate
- **Integration Tests**:
  - Enhanced integration test infrastructure and reliability
  - Added CI skip logic for integration tests
  - Fixed false-pass tests and improved test stability
  - Added integration test for session metrics retrieval
  - Refactored filesystem integration tests
- **Test Compatibility**: Made version_utils tests Python 3.10-compatible
- **CI Improvements**: Improved CI skip logic for browser fingerprint tests

### Bug Fixes
- Fixed output log source to match result object structure in main.py
- Fixed Java result output log variable reference errors
- Fixed JavaScript execution result output logic errors
- Fixed default `image_id` value for `list_mcp_tools` (now uses `agb-code-space-1`)
- Fixed `conftest.py` being run as a test file
- Fixed write_file on deleted session test and integration test issues
- Optimized docstring and fixed default value of `list_mcp_tools`

## [0.8.0] - 2026-01-08

### New Features
- **Code Execution**: Added Jupyter-style rich outputs support for `run_code()` (e.g., images/HTML/Markdown/LaTeX/JSON).
- **File System**: Added `delete_file()` support with tests and documentation.
- **File System**: Added support for returning binary file content (bytes) for read operations.
- **Command Execution**: Added `cwd` and `envs` parameters, plus richer `CommandResult` fields for better diagnostics.

### Enhancements
- **Documentation**: Added/updated capability docs for binary reads, file deletion, and `run_code` rich outputs.
- **Documentation**: Split large pages into focused sub-pages (browser, computer, context) and standardized the overview template.
- **Documentation**: Removed source file names from headings for cleaner, goal-oriented titles.

### Refactoring
- **AGB Core**: Extracted context synchronization waiting/polling logic into a helper and removed an unused in-memory session cache.
- **File System**: Removed a debug log line to reduce noise.

### Testing & CI/CD
- **CI/CD**: Skipped pipeline execution for docs-only changes to speed up iteration.
- **CI/CD**: Improved docs sync behavior to preserve `public/` and `terms-of-service/` in the target docs repository.
- **Tests**: Normalized line endings in file transfer tests for better cross-platform stability.

## [0.7.1] - 2025-12-22

### Enhancements
- **Default Parameters**: Adjusted default parameter values for improved usability and performance
- **API Documentation**: Updated API documentation to reflect current functionality

### Refactoring
- **Code Cleanup**: Removed deprecated session management methods and simplified API surface
- **Documentation Updates**: Cleaned up documentation references to align with current API

### Testing & CI/CD
- **Test Adjustments**: Updated test cases to match current API behavior and improve test reliability

## [0.7.0] - 2025-12-18

### New Features
- **Browser Fingerprint Enhancement**: Comprehensive browser fingerprint management with persistence, local sync, and advanced configuration options
- **Computer Automation Module**: Full desktop automation capabilities including:
  - Screenshot capture support for AGB sessions
  - Keyboard input functionality with comprehensive key support
  - Mouse operations with button and scroll direction enums
  - Window listing and management functionality
  - Application operations support
- **File Transfer Function**: Complete file transfer functionality for moving files between local and remote environments
- **Async Session Deletion**: Migrated session deletion API from `release_mcp_session` to `delete_session_async` with polling support
- **Browser Type Configuration**: Support for browser type and command arguments settings for enhanced browser control
- **MCP Access Documentation**: Comprehensive guide for MCP (Model Context Protocol) access and configuration

### Enhancements
- **Context Manager**: Improved error handling by returning error results instead of raising exceptions in context sync validation
- **Browser Agent**: Enhanced browser agent with improved integration tests and better error handling
- **API Documentation**: Added fingerprint module to API documentation generation
- **Code Examples**: Optimized and improved code examples throughout documentation

### Documentation
- Added MCP access guide with comprehensive configuration instructions
- Added examples for application and window operations
- Updated text input examples in documentation
- Corrected documentation regarding command execution instructions
- Standardized guides structure to match template
- Removed example code from ContextManager docstring
- Added file transfer guide markdown

### Refactoring
- Removed unused `http_port` and `token` fields from session response models
- Improved context sync validation to return error results instead of exceptions
- Cleaned up unrelated files and code

### Testing & CI/CD
- Optimized CI/CD pipeline summary with switch state for better visibility
- Enhanced test coverage for computer module, file transfer, and browser fingerprint features
- Fixed context manager sync tests to match new validation logic

## [0.6.0] - 2025-12-04

### New Features
- **Context Sync Mapping Policy**: Added `MappingPolicy` support for cross-platform data persistence between Browser and Code sessions
- **API Documentation Generation**: Automated API reference documentation generation with Google-style docstrings and GitHub Pages sync
- **Integration Testing Infrastructure**: Enhanced CI/CD pipeline with dedicated integration test job and dynamic endpoint resolution

### Breaking Changes
- **Session Class Refactoring**: Removed `BaseSession` class and merged functionality into `Session` class. Removed deprecated `find_server_for_tool` method.

### Enhancements
- **Documentation**: Complete restructuring of API reference, examples, and guides. Added cross-platform persistence guide and embedded code snippets for VitePress
- **Code Quality**: Unified all docstrings to Google style format with type annotations throughout codebase
- **API Improvements**: Added timeout configuration and improved argument filtering for MCP tool calls

### Bug Fixes
- **Integration Tests**: Fixed exit code reporting to correctly indicate test failures in CI/CD pipelines
- **Context Service**: Added null checks to prevent exceptions in context operations
- **Documentation**: Fixed broken links and incorrect references throughout documentation
- **Test Infrastructure**: Enhanced test stability and reliability, added special handling for CEASED account status

### Testing & CI/CD
- Added integration test job to CI/CD pipeline with comprehensive test coverage
- Improved test stability with proper wait times and resource cleanup
- Added CI bot guard to prevent infinite loops and enhanced error detection
- Fixed documentation pipeline configuration and optimized documentation workflow

## [0.5.0] - 2025-11-20

### New Features
- **Context Clear API**: Added `clear_async`, `get_clear_status`, and synchronous `clear` with
  configurable timeout, poll interval, and explicit state tracking.
- **SDK Telemetry**: Session creation now records SDK version and release status, with explicit
  release flagging injected during the official build process.
- **Context Sync Enhancements**: Introduced `UploadMode` and lifecycle enums for more flexible
  synchronization policies.
- **Session Parameters**: Enforced `image_id` as a required field in `CreateSessionParams`,
  improving validation and error messaging.
- **Testing Framework**: Expanded unit tests to cover Code, Command, FileSystem, ContextManager,
  SessionParams, response models, and context clear flows.

### Bug Fixes
- Added `error_message` propagation to `ContextSyncResult`, ensuring API failures surface in sync
  results.
- Aligned sample code and tests to use valid `image_id` values and consistent data paths, fixing
  persistence-related flakes.

### Documentation
- Updated context usage guide, sync policy docs, API references, and data persistence examples to
  reflect the new features.

### Testing & CI
- Added a RecyclePolicy integration test and tightened context sync test coverage, including path
  uniqueness checks.
- CI now runs unit tests by default, installs pytest automatically, and includes pipeline
  optimizations plus master-branch triggers.


## [0.4.0] - 2025-10-31

### New Features
- **Session Management Enhancements**: Complete session lifecycle management with listing, retrieval, and labeling
  - `list()` method for retrieving all sessions with pagination support
  - `get()` method for retrieving individual session details by session ID
  - Session labels support for better session organization and management
- **Browser Module Enhancements**:
  - Captcha solving support for browser automation
  - Extension support for AGB browser operations
- **Context API Improvements**:
  - Enhanced parameter validation for all context operations
  - Improved error messages for missing or invalid parameters
  - `list_files()` now supports optional `parent_folder_path` parameter

### Bug Fixes
- **Context Validation**: Fixed missing parameter validation in context operations
  - Added null and empty string checks for all required parameters
  - Improved error handling and user feedback
- **Browser Module**: Fixed API parameter mismatch (`schema` renamed to `field_schema`) to align with MCP field validation
- **Testing**: Fixed httpx connection error in integration tests for context file URLs
- **Context Manager**: Optimized documentation notes in `context_manager.sync()` function

### Documentation & Testing
- **Session Management**:
  - Comprehensive documentation for session listing, retrieval, and label management
  - Updated session management guide with new features
  - New examples for session label operations
- **Testing Coverage**:
  - Integration tests for session labels functionality
  - Unit tests for AGB and session modules
  - Comprehensive validation tests for context operations (18 new test cases)
  - Enhanced test coverage for file operations with parameter validation


## [0.3.0] - 2025-10-15

### New Features
- **Context Management System**: Complete context management with persistent data storage, file operations, and synchronization
- **Enhanced Logging**: Integrated Loguru for better log formatting and structured logging across all modules

### API Enhancements
- **Context API**: New context endpoints for CRUD operations, file management, and synchronization with region support
- **Session Integration**: Enhanced session management with context synchronization during lifecycle

### Documentation & Testing
- **Context Documentation**: Comprehensive usage guides, API reference, and response type documentation
- **Testing**: Complete test coverage for context operations, file management, and synchronization features

### Bug Fixes
- **API & HTTP**: Fixed parameter validation, async request issues, and data serialization problems
- **Infrastructure**: Updated dependencies, improved CI/CD, and resolved type checking issues

## [0.2.2] - 2025-09-23
### Bug Fixes
- remove oss related code and docs
- fix async http request bug
- Updated testing and documentation improvements


## [0.2.1] - 2025-09-10

### Bug Fixes
- **Directory Monitoring**: Fixed deduplication issue in watch directory functionality
  - Removed unnecessary event deduplication that was causing missed file changes
  - Improved callback handling to ensure all file events are properly reported
  - Enhanced error handling in directory monitoring callbacks

### Testing
- Enhanced test coverage for directory monitoring functionality
- Added comprehensive file modification monitoring tests
- Improved integration test reliability

## [0.2.0] - 2025-09-08

### New Features
- **Directory Monitoring API**: Added comprehensive directory watching functionality
  - `watch_directory()` method for real-time file system monitoring
  - Support for recursive directory watching
  - File change event handling (create, modify, delete, move)
  - Configurable watch patterns and filters
  - Async support for directory monitoring operations

### Infrastructure Improvements
- **CI/CD Pipeline**: Complete GitHub Actions workflow setup
  - Automated testing across multiple Python versions (3.10, 3.11, 3.12)
  - Cross-platform testing (Ubuntu, macOS, Windows)
  - Code quality checks with Black, isort, Flake8, and MyPy
  - Security scanning with Bandit, Safety, and CodeQL
  - Automated dependency updates with Dependabot
  - Release automation with PyPI publishing
- **Pre-commit Configuration**: Standardized code quality enforcement
  - Python code formatting with Black
  - Import sorting with isort
  - Linting with Flake8 and security checks with Bandit
  - YAML, TOML, and JSON validation
  - Type checking with MyPy

### Documentation
- **Enhanced API Reference**: Updated filesystem module documentation
- **New Examples**: Directory monitoring examples and usage patterns
- **File Operations Guide**: Comprehensive guide for file system operations

### Technical Improvements
- Updated API client architecture for better extensibility
- Enhanced error handling for directory monitoring operations
- Comprehensive test coverage for new functionality

## [0.1.0] - 2025-08-30

### Initial Release

This is the first official release of the AGB SDK, providing a comprehensive Python SDK for AI-powered code execution and management.

#### New Features
- **Core SDK**: Complete Python SDK for AGB platform
- **Session Management**: Create and manage execution sessions
- **Code Execution**: Execute Python code in isolated environments
- **Command Execution**: Run shell commands and scripts
- **File System Operations**: Manage files and directories

#### Core Modules
- **Code Module**: Execute Python code with full environment access
- **Command Module**: Run shell commands and system operations
- **File System Module**: File and directory management operations

#### Technical Features
- **Session-based Architecture**: Secure, isolated execution environments
- **RESTful API**: Clean HTTP-based communication
- **Error Handling**: Comprehensive exception handling and error reporting
- **Authentication**: API key-based authentication
- **Async Support**: Asynchronous operation support

#### Documentation
- Complete API reference documentation
- Usage examples and tutorials
- Best practices guide
- Quick start guide

#### Requirements
- Python 3.10+
- Required packages: requests, typing-extensions
- Environment variable: AGB_API_KEY

#### License
- Apache License 2.0