from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class UploadStrategy(Enum):
    """Upload strategy for context synchronization"""

    UPLOAD_BEFORE_RESOURCE_RELEASE = "UploadBeforeResourceRelease"


class DownloadStrategy(Enum):
    """Download strategy for context synchronization"""

    DOWNLOAD_ASYNC = "DownloadAsync"


@dataclass
class UploadPolicy:
    """
    Defines the upload policy for context synchronization

    Attributes:
        auto_upload: Enables automatic upload
        upload_strategy: Defines the upload strategy
    """

    auto_upload: bool = True
    upload_strategy: UploadStrategy = UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE


    def to_dict(self):
        return {
            "autoUpload": self.auto_upload,
            "uploadStrategy": (
                self.upload_strategy.value if self.upload_strategy else None
            ),
        }


@dataclass
class DownloadPolicy:
    """
    Defines the download policy for context synchronization

    Attributes:
        auto_download: Enables automatic download
        download_strategy: Defines the download strategy
    """

    auto_download: bool = True
    download_strategy: DownloadStrategy = DownloadStrategy.DOWNLOAD_ASYNC


    def to_dict(self):
        return {
            "autoDownload": self.auto_download,
            "downloadStrategy": (
                self.download_strategy.value if self.download_strategy else None
            ),
        }


@dataclass
class DeletePolicy:
    """
    Defines the delete policy for context synchronization

    Attributes:
        sync_local_file: Enables synchronization of local file deletions
    """

    sync_local_file: bool = True


    def to_dict(self):
        return {"syncLocalFile": self.sync_local_file}


@dataclass
class ExtractPolicy:
    """
    Defines the extract policy for context synchronization

    Attributes:
        extract: Enables file extraction
        delete_src_file: Enables deletion of source file after extraction
    """

    extract: bool = True
    delete_src_file: bool = True
    extract_current_folder: bool = False


    def to_dict(self):
        return {"extract": self.extract, "deleteSrcFile": self.delete_src_file, "extractToCurrentFolder": self.extract_current_folder}


@dataclass
class WhiteList:
    """
    Defines the white list configuration

    Attributes:
        path: Path to include in the white list
        exclude_paths: Paths to exclude from the white list
    """

    path: str = ""
    exclude_paths: List[str] = field(default_factory=list)

    def to_dict(self):
        return {"path": self.path, "excludePaths": self.exclude_paths}


@dataclass
class BWList:
    """
    Defines the black and white list configuration

    Attributes:
        white_lists: Defines the white lists
    """

    white_lists: List[WhiteList] = field(default_factory=list)

    def to_dict(self):
        return {
            "whiteLists": (
                [wl.to_dict() for wl in self.white_lists] if self.white_lists else []
            )
        }


@dataclass
class SyncPolicy:
    """
    Defines the synchronization policy

    Attributes:
        upload_policy: Defines the upload policy
        download_policy: Defines the download policy
        delete_policy: Defines the delete policy
        extract_policy: Defines the extract policy
        bw_list: Defines the black and white list
    """

    upload_policy: Optional[UploadPolicy] = None
    download_policy: Optional[DownloadPolicy] = None
    delete_policy: Optional[DeletePolicy] = None
    extract_policy: Optional[ExtractPolicy] = None
    bw_list: Optional[BWList] = None

    def __post_init__(self):
        """Post-initialization to ensure all policies have default values if not provided"""
        if self.upload_policy is None:
            self.upload_policy = UploadPolicy()
        if self.download_policy is None:
            self.download_policy = DownloadPolicy()
        if self.delete_policy is None:
            self.delete_policy = DeletePolicy()
        if self.extract_policy is None:
            self.extract_policy = ExtractPolicy()
        if self.bw_list is None:
            self.bw_list = BWList()


    def to_dict(self):
        result = {}
        if self.upload_policy:
            result["uploadPolicy"] = self.upload_policy.to_dict()
        if self.download_policy:
            result["downloadPolicy"] = self.download_policy.to_dict()
        if self.delete_policy:
            result["deletePolicy"] = self.delete_policy.to_dict()
        if self.extract_policy:
            result["extractPolicy"] = self.extract_policy.to_dict()
        if self.bw_list:
            result["bwList"] = self.bw_list.to_dict()
        return result


@dataclass
class ContextSync:
    """
    Defines the context synchronization configuration

    Attributes:
        context_id: ID of the context to synchronize
        path: Path where the context should be mounted
        policy: Defines the synchronization policy
    """

    context_id: str
    path: str
    policy: Optional[SyncPolicy] = None

    @classmethod
    def new(cls, context_id: str, path: str, policy: Optional[SyncPolicy] = None):
        """Creates a new context sync configuration"""
        return cls(context_id=context_id, path=path, policy=policy)

    def with_policy(self, policy: SyncPolicy):
        """Sets the policy"""
        self.policy = policy
        return self
