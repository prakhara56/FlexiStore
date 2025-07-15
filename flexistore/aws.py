import os
from typing import List
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from .manager import StorageManager

class AWSStorageManager(StorageManager):
    def __init__(
        self,
        bucket: str,
        region: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        *,
        verify_ssl: bool = False
    ):
        try:
            session = boto3.session.Session(
                aws_access_key_id=aws_access_key_id or None,
                aws_secret_access_key=aws_secret_access_key or None,
                region_name=region or None,
            )
            self.s3 = session.resource("s3", verify=verify_ssl)
            self.bucket = self.s3.Bucket(bucket)
            # Verify bucket exists
            self.s3.meta.client.head_bucket(Bucket=bucket)
            print(f"Connected to AWS bucket '{bucket}' successfully. \nVerify_ssl={verify_ssl}")
        except (BotoCoreError, ClientError) as e:
            print(f"Failed to connect to AWS S3: {e}")
            raise

    def upload_file(self, local_path: str, remote_path: str) -> None:
        try:
            self.bucket.upload_file(local_path, remote_path)
            print(f"Upload succeeded: '{local_path}' → '{remote_path}'")
        except (BotoCoreError, ClientError, IOError) as e:
            print(f"Upload failed: {e}")
            raise

    def download_file(self, remote_path: str, local_path: str) -> None:
        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            self.bucket.download_file(remote_path, local_path)
            print(f"Download succeeded: '{remote_path}' → '{local_path}'")
        except (BotoCoreError, ClientError, IOError) as e:
            print(f"Download failed: {e}")
            raise

    def list_files(self, remote_prefix: str) -> List[str]:
        try:
            objs = [obj.key for obj in self.bucket.objects.filter(Prefix=remote_prefix)]
            print(f"Listed {len(objs)} objects under prefix '{remote_prefix}'.")
            return objs
        except (BotoCoreError, ClientError) as e:
            print(f"List operation failed: {e}")
            raise

    def download_folder(self, remote_prefix: str, local_dir: str) -> None:
        try:
            objs = self.list_files(remote_prefix)
            for key in objs:
                dest = os.path.join(local_dir, os.path.relpath(key, remote_prefix))
                self.download_file(key, dest)
            print(f"Folder download succeeded: '{remote_prefix}' → '{local_dir}'")
        except Exception as e:
            print(f"Folder download failed: {e}")
            raise

    def delete_file(self, remote_path: str) -> None:
        try:
            self.bucket.Object(remote_path).delete()
            print(f"Deletion succeeded: '{remote_path}'")
        except (BotoCoreError, ClientError) as e:
            print(f"Deletion failed: {e}")
            raise
