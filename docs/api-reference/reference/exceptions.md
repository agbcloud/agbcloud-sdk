# Exceptions API Reference

## Overview

Standard exceptions raised by the AGB SDK.




## AGBError

```python
class AGBError(Exception)
```

Base exception for all AGB SDK errors.

## AuthenticationError

```python
class AuthenticationError(AGBError)
```

Raised when there is an authentication error.

## APIError

```python
class APIError(AGBError)
```

Raised when there is an error with the API.

## FileError

```python
class FileError(AGBError)
```

Raised for errors related to file operations.

## CommandError

```python
class CommandError(AGBError)
```

Raised for errors related to command execution.

## SessionError

```python
class SessionError(AGBError)
```

Raised for errors related to session operations.

## ApplicationError

```python
class ApplicationError(AGBError)
```

Raised for errors related to application operations.

## BrowserError

```python
class BrowserError(AGBError)
```

Raised for errors related to browser operations.

## ClearanceTimeoutError

```python
class ClearanceTimeoutError(AGBError)
```

Raised when the clearance task times out.

---

*Documentation generated automatically from source code using pydoc-markdown.*
