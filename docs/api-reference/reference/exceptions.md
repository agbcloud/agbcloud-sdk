# Exceptions

This section lists the exceptions raised by the AGB SDK. All exceptions inherit from `AGBError`.

## AGBError
Base exception for all AGB SDK errors.

## AuthenticationError
Raised when there is an authentication error (e.g., invalid API key).

## APIError
Raised when there is an error with the AGB API (e.g., network issues, 5xx errors).

**Attributes:**
- `status_code`: HTTP status code of the response (if applicable).

## FileError
Raised for errors related to file operations (e.g., file not found, permission denied).

## CommandError
Raised for errors related to command execution.

## SessionError
Raised for errors related to session operations (e.g., creation failure, session lost).

## ApplicationError
Raised for errors related to application operations.

## BrowserError
Raised for errors related to browser operations (e.g., navigation failed, element not found).

## ClearanceTimeoutError
Raised when the clearance task times out.

