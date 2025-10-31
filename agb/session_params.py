from typing import Optional, List, Dict, TYPE_CHECKING
from agb.logger import get_logger
from agb.context_sync import ContextSync, DeletePolicy, SyncPolicy, UploadPolicy, ExtractPolicy, BWList, WhiteList

if TYPE_CHECKING:
    from agb.extension import ExtensionOption

# Initialize logger for this module
logger = get_logger("session_params")
class BrowserContext:
    """
    Browser context configuration for session with optional extension support.

    This class provides browser context configuration for cloud sessions and supports
    automatic extension synchronization when ExtensionOption is provided.

    Key Features:
    - Browser context binding for sessions
    - Automatic browser data upload on session end
    - Optional extension integration with automatic context sync generation
    - Clean API with ExtensionOption encapsulation

    Attributes:
        context_id (str): ID of the browser context to bind to the session
        auto_upload (bool): Whether to automatically upload browser data when session ends
        extension_option (Optional[ExtensionOption]): Extension configuration object containing
                                                     context_id and extension_ids.
        extension_context_id (Optional[str]): ID of the extension context for browser extensions.
                                             Set automatically from extension_option.
        extension_ids (Optional[List[str]]): List of extension IDs to synchronize.
                                           Set automatically from extension_option.
        extension_context_syncs (Optional[List[ContextSync]]): Auto-generated context syncs for extensions.
                                                              None if no extension configuration provided,
                                                              or List[ContextSync] if extensions are configured.

    Extension Configuration:
    - **ExtensionOption**: Pass an ExtensionOption object with context_id and extension_ids
    - **No Extensions**: Don't provide extension_option parameter (extension_context_syncs will be None)

    Usage Examples:
        ```python
        # With extensions using ExtensionOption
        from agb.extension import ExtensionOption

        ext_option = ExtensionOption(
            context_id="my_extensions",
            extension_ids=["ext1", "ext2"]
        )

        browser_context = BrowserContext(
            context_id="browser_session",
            auto_upload=True,
            extension_option=ext_option
        )

        # Without extensions (minimal configuration)
        browser_context = BrowserContext(
            context_id="browser_session",
            auto_upload=True
        )
        # extension_context_syncs will be None
        ```
    """

    def __init__(self, context_id: str, auto_upload: bool = True,
                 extension_option: Optional["ExtensionOption"] = None):
        """
        Initialize BrowserContext with optional extension support.

        Args:
            context_id (str): ID of the browser context to bind to the session.
                             This identifies the browser instance for the session.

            auto_upload (bool, optional): Whether to automatically upload browser data
                                        when the session ends. Defaults to True.

            extension_option (Optional[ExtensionOption], optional): Extension configuration object containing
                                                                   context_id and extension_ids. This encapsulates
                                                                   all extension-related configuration.
                                                                   Defaults to None.

        Extension Configuration:
            - **ExtensionOption**: Use extension_option parameter with an ExtensionOption object
            - **No Extensions**: Don't provide extension_option parameter

        Auto-generation:
            - extension_context_syncs is automatically generated when extension_option is provided
            - extension_context_syncs will be None if no extension_option is provided
            - extension_context_syncs will be a List[ContextSync] if extension_option is valid

        Examples:
            ```python
            # With extensions using ExtensionOption
            from agb.extension import ExtensionOption

            ext_option = ExtensionOption(
                context_id="my_extensions",
                extension_ids=["ext1", "ext2"]
            )

            browser_context = BrowserContext(
                context_id="browser_session",
                auto_upload=True,
                extension_option=ext_option
            )

            # Without extensions (minimal configuration)
            browser_context = BrowserContext(
                context_id="browser_session",
                auto_upload=True
            )
            # extension_context_syncs will be None
            ```
        """
        self.context_id = context_id
        self.auto_upload = auto_upload
        self.extension_option = extension_option

        # Handle extension configuration from ExtensionOption
        if extension_option:
            # Extract extension information from ExtensionOption
            self.extension_context_id = extension_option.context_id
            self.extension_ids = extension_option.extension_ids
            # Auto-generate extension context syncs
            self.extension_context_syncs = self._create_extension_context_syncs()
        else:
            # No extension configuration provided
            self.extension_context_id = None
            self.extension_ids = []
            self.extension_context_syncs = None

    def _create_extension_context_syncs(self) -> List[ContextSync]:
        """
        Create ContextSync configurations for browser extensions.

        This method is called only when extension_option is provided and contains
        valid extension configuration (context_id and extension_ids).

        Returns:
            List[ContextSync]: List of context sync configurations for extensions.
                              Returns empty list if extension configuration is invalid.
        """
        if not self.extension_ids or not self.extension_context_id:
            return []

        # Create whitelist for each extension ID
        white_lists = [WhiteList(path=f"{ext_id}", exclude_paths=[]) for ext_id in self.extension_ids]

        # Create sync policy for extensions
        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy(auto_upload=False),
            delete_policy=DeletePolicy(sync_local_file=False),
            extract_policy=ExtractPolicy(extract=True, delete_src_file=True),
            bw_list=BWList(white_lists=white_lists)
        )

        # Create context sync for extensions
        extension_sync = ContextSync(
            context_id=self.extension_context_id,
            path="/tmp/extensions/",
            policy=sync_policy
        )

        return [extension_sync]

    def get_all_context_syncs(self) -> List[ContextSync]:
        """
        Get all context syncs including extension syncs.

        Returns:
            List[ContextSync]: All context sync configurations. Returns empty list if no extensions configured.
        """
        return self.extension_context_syncs or []

class CreateSessionParams:
    """
    Parameters for creating a new session in the AGB cloud environment.

    Attributes:
        labels (Optional[Dict[str, str]]): Custom labels for the Session. These can be
            used for organizing and filtering sessions.
        image_id (Optional[str]): ID of the image to use for the session.
        context_syncs (Optional[List[ContextSync]]): List of context synchronization configurations.
    """

    def __init__(
        self,
        labels: Optional[Dict[str, str]] = None,
        image_id: Optional[str] = None,
        context_syncs: Optional[List["ContextSync"]] = None,
        browser_context: Optional[BrowserContext] = None,
    ):
        """
        Initialize CreateSessionParams.

        Args:
            labels (Optional[Dict[str, str]]): Custom labels for the Session.
                Defaults to None.
            image_id (Optional[str]): ID of the image to use for the session.
                Defaults to None.
            context_syncs (Optional[List[ContextSync]]): List of context synchronization configurations.
                Defaults to None.
        """
        self.labels = labels or {}
        self.image_id = image_id
        # Start with provided context_syncs
        all_context_syncs = list(context_syncs or [])
        # Add extension context syncs from browser_context if available
        if browser_context and browser_context.extension_context_syncs:
            all_context_syncs.extend(browser_context.extension_context_syncs)
            logger.info(f"Added {len(browser_context.extension_context_syncs)} extension context sync(s) from BrowserContext")

        self.context_syncs = all_context_syncs
        self.browser_context = browser_context
