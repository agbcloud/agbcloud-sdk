"""
API response models for AGB SDK.
"""

from typing import TYPE_CHECKING, Any, List, Optional


if TYPE_CHECKING:
    from agb.session import BaseSession


class ApiResponse:
    """Base class for all API responses, containing RequestID"""

    def __init__(self, request_id: str = ""):
        """
        Initialize an ApiResponse with a request_id.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
        """
        self.request_id = request_id

    def get_request_id(self) -> str:
        """Returns the unique identifier for the API request."""
        return self.request_id


class SessionResult(ApiResponse):
    """Result of operations returning a single Session."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
        session: Optional["BaseSession"] = None,
    ):
        """
        Initialize a SessionResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            session (Optional[BaseSession], optional): The session object. Defaults to None.
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message
        self.session = session


class DeleteResult(ApiResponse):
    """Result of delete operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        error_message: str = "",
    ):
        """
        Initialize a DeleteResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the delete operation was successful.
                Defaults to False.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message


class OperationResult(ApiResponse):
    """Result of general operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        data: Any = None,
        error_message: str = "",
    ):
        """
        Initialize an OperationResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            data (Any, optional): Data returned by the operation. Defaults to None.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.data = data
        self.error_message = error_message


class BoolResult(ApiResponse):
    """Result of operations returning a boolean value."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        data: Optional[bool] = None,
        error_message: str = "",
    ):
        """
        Initialize a BoolResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            data (Optional[bool], optional): The boolean result. Defaults to None.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.data = data
        self.error_message = error_message

