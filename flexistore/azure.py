import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import AzureError
from azure.core.pipeline.transport import RequestsTransport
from typing import List
from .manager import StorageManager

class AzureStorageManager(StorageManager):
    def __init__(self, conn_str: str, container: str, verify_ssl: bool = True):
        if not BlobServiceClient:
            raise ImportError("azure-storage-blob is required")
        try:
            client = BlobServiceClient.from_connection_string(
                conn_str,
                transport=RequestsTransport(connection_verify=verify_ssl)
            )
            self.container: ContainerClient = client.get_container_client(container)
            print(f"Connected to Azure container '{container}' successfully.")
        except AzureError as e:
            print(f"Failed to connect to Azure Blob Storage: {e}")
            raise

    def upload_file(self, local_path: str, remote_path: str) -> None:
        try:
            with open(local_path, "rb") as f:
                self.container.upload_blob(name=remote_path, data=f, overwrite=True)
            print(f"Upload succeeded: '{local_path}' → '{remote_path}'")
        except (AzureError, IOError) as e:
            print(f"Upload failed: {e}")
            raise

    def download_file(self, remote_path: str, local_path: str) -> None:
        try:
            blob: BlobClient = self.container.get_blob_client(remote_path)
            data = blob.download_blob().readall()
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(data)
            print(f"Download succeeded: '{remote_path}' → '{local_path}'")
        except (AzureError, IOError) as e:
            print(f"Download failed: {e}")
            raise

    def list_files(self, remote_prefix: str) -> List[str]:
        try:
            blobs = [blob.name for blob in self.container.list_blobs(name_starts_with=remote_prefix)]
            print(f"Listed {len(blobs)} blobs under prefix '{remote_prefix}'.")
            return blobs
        except AzureError as e:
            print(f"List operation failed: {e}")
            raise

    def download_folder(self, remote_prefix: str, local_dir: str) -> None:
        try:
            blobs = self.list_files(remote_prefix)
            for blob_name in blobs:
                dest = os.path.join(local_dir, os.path.relpath(blob_name, remote_prefix))
                self.download_file(blob_name, dest)
            print(f"Folder download succeeded: '{remote_prefix}' → '{local_dir}'")
        except Exception as e:
            print(f"Folder download failed: {e}")
            raise

    def delete_file(self, remote_path: str) -> None:
        try:
            self.container.delete_blob(remote_path)
            print(f"Deletion succeeded: '{remote_path}'")
        except AzureError as e:
            print(f"Deletion failed: {e}")
            raise
