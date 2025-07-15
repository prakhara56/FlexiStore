import os
from azure.storage.blob import BlobServiceClient
from azure.core.pipeline.transport import RequestsTransport
from typing import List
from .manager import StorageManager

class AzureStorageManager(StorageManager):
    def __init__(self, conn_str: str, container: str):
        if not BlobServiceClient:
            raise ImportError("azure-storage-blob is required")
        client = BlobServiceClient.from_connection_string(
            conn_str,
            transport=RequestsTransport(connection_verify=False)
        )
        self.container = client.get_container_client(container)

    def upload_file(self, local_path: str, remote_path: str) -> None:
        with open(local_path, "rb") as f:
            self.container.upload_blob(name=remote_path, data=f, overwrite=True)

    def download_file(self, remote_path: str, local_path: str) -> None:
        blob = self.container.download_blob(remote_path)
        data = blob.readall()
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(data)

    def list_files(self, remote_prefix: str) -> List[str]:
        return [blob.name for blob in self.container.list_blobs(name_starts_with=remote_prefix)]

    def download_folder(self, remote_prefix: str, local_dir: str) -> None:
        for blob_name in self.list_files(remote_prefix):
            dest = os.path.join(local_dir, os.path.relpath(blob_name, remote_prefix))
            self.download_file(blob_name, dest)

    def delete_file(self, remote_path: str) -> None:
        self.container.delete_blob(remote_path)
