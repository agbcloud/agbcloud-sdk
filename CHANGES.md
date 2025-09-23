# Changelog

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