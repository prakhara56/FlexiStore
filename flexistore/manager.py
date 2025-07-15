import os
from abc import ABC, abstractmethod
from typing import List

class StorageManager(ABC):
    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> None:
        """Upload a file from local_path to remote_path."""
        pass

    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> None:
        """Download a file from remote_path to local_path."""
        pass

    @abstractmethod
    def list_files(self, remote_prefix: str) -> List[str]:
        """List all blob/object names under the given prefix."""
        pass

    @abstractmethod
    def download_folder(self, remote_prefix: str, local_dir: str) -> None:
        """Download all files under the given remote prefix into local_dir."""
        pass

    @abstractmethod
    def delete_file(self, remote_path: str) -> None:
        """Delete the blob at the given remote path."""
        pass
