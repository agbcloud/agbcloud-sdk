from typing import Optional


class CreateSessionParams:
    """
    Parameters for creating a new session in the AGB cloud environment.

    Attributes:
        image_id (Optional[str]): ID of the image to use for the session.
    """

    def __init__(
        self,
        image_id: Optional[str] = None,
    ):
        """
        Initialize CreateSessionParams.

        Args:
            image_id (Optional[str]): ID of the image to use for the session.
                Defaults to None.
        """
        self.image_id = image_id
