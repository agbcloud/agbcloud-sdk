from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from agb.context_sync import ContextSync


class CreateSessionParams:
    """
    Parameters for creating a new session in the AGB cloud environment.

    Attributes:
        image_id (Optional[str]): ID of the image to use for the session.
        context_syncs (Optional[List[ContextSync]]): List of context synchronization configurations.
    """

    def __init__(
        self,
        image_id: Optional[str] = None,
        context_syncs: Optional[List["ContextSync"]] = None,
    ):
        """
        Initialize CreateSessionParams.

        Args:
            image_id (Optional[str]): ID of the image to use for the session.
                Defaults to None.
            context_syncs (Optional[List[ContextSync]]): List of context synchronization configurations.
                Defaults to None.
        """
        self.image_id = image_id
        self.context_syncs = context_syncs or []
