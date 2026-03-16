import pytest

from agb.exceptions import (
    AGBError,
    APIError,
    AuthenticationError,
    ApplicationError,
    BrowserError,
    CommandError,
    FileError,
    SessionError,
)


def test_agb_error_default_message_and_extra():
    err = AGBError(None, foo="bar")
    assert str(err) == "AGBError"
    assert err.extra["foo"] == "bar"


def test_exception_default_messages():
    assert str(AuthenticationError()) == "Authentication failed"
    assert str(CommandError()) == "Command execution error"
    assert str(SessionError()) == "Session error"


def test_api_error_status_code():
    err = APIError("nope", status_code=401)
    assert str(err) == "nope"
    assert err.status_code == 401


def test_more_default_exceptions():
    assert str(FileError()) == "File operation error"
    assert str(ApplicationError()) == "Application operation error"
    assert str(BrowserError()) == "Browser operation error"

