class AGBError(Exception):
    """Base exception for all AGB SDK errors."""

    def __init__(self, message=None, *args, **kwargs):
        if message is None:
            message = self.__class__.__name__
        super().__init__(message, *args)
        self.extra = kwargs


class AuthenticationError(AGBError):
    """Raised when there is an authentication error."""

    def __init__(self, message="Authentication failed", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class APIError(AGBError):
    """Raised when there is an error with the API."""

    def __init__(self, message="API error", status_code=None, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.status_code = status_code


class FileError(AGBError):
    """Raised for errors related to file operations."""

    def __init__(self, message="File operation error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class CommandError(AGBError):
    """Raised for errors related to command execution."""

    def __init__(self, message="Command execution error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class SessionError(AGBError):
    """Raised for errors related to session operations."""

    def __init__(self, message="Session error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class OssError(AGBError):
    """Raised for errors related to OSS operations."""

    def __init__(self, message="OSS operation error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class ApplicationError(AGBError):
    """Raised for errors related to application operations."""

    def __init__(self, message="Application operation error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class BrowserError(AGBError):
    """Raised for errors related to browser operations."""

    def __init__(self, message="Browser operation error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)
