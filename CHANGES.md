# Changelog

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