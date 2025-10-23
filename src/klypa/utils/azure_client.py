"""Azure cloud storage integration"""

import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta

from ..config import config

logger = logging.getLogger(__name__)


class AzureStorageClient:
    """Client for Azure Blob Storage"""

    def __init__(
        self,
        connection_string: Optional[str] = None,
        container_name: Optional[str] = None,
    ):
        """
        Initialize Azure Storage client

        Args:
            connection_string: Azure storage connection string
            container_name: Container name for video storage
        """
        self.connection_string = connection_string or config.azure.connection_string
        self.container_name = container_name or config.azure.container_name
        self._client = None
        self._container_client = None

    def _get_blob_service_client(self):
        """Get or create blob service client"""
        if self._client is None:
            try:
                from azure.storage.blob import BlobServiceClient

                self._client = BlobServiceClient.from_connection_string(
                    self.connection_string
                )
                logger.info("Azure Blob Service client initialized")
            except Exception as e:
                logger.error(f"Error initializing Azure client: {e}")
                raise
        return self._client

    def _get_container_client(self):
        """Get or create container client"""
        if self._container_client is None:
            blob_service = self._get_blob_service_client()
            self._container_client = blob_service.get_container_client(
                self.container_name
            )

            # Create container if it doesn't exist
            try:
                if not self._container_client.exists():
                    self._container_client.create_container()
                    logger.info(f"Created container: {self.container_name}")
            except Exception as e:
                logger.error(f"Error accessing container: {e}")

        return self._container_client

    def upload_video(self, local_path: Path, blob_name: Optional[str] = None) -> str:
        """
        Upload video to Azure Storage

        Args:
            local_path: Path to local video file
            blob_name: Optional blob name (defaults to filename)

        Returns:
            URL of uploaded blob
        """
        if not local_path.exists():
            raise FileNotFoundError(f"File not found: {local_path}")

        blob_name = blob_name or local_path.name
        logger.info(f"Uploading {local_path} to {blob_name}")

        try:
            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(blob_name)

            with open(local_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

            blob_url = blob_client.url
            logger.info(f"Upload completed: {blob_url}")
            return blob_url

        except Exception as e:
            logger.error(f"Error uploading video: {e}", exc_info=True)
            raise

    def download_video(self, blob_name: str, local_path: Path) -> Path:
        """
        Download video from Azure Storage

        Args:
            blob_name: Name of blob to download
            local_path: Path to save downloaded file

        Returns:
            Path to downloaded file
        """
        logger.info(f"Downloading {blob_name} to {local_path}")

        try:
            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(blob_name)

            local_path.parent.mkdir(parents=True, exist_ok=True)

            with open(local_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())

            logger.info(f"Download completed: {local_path}")
            return local_path

        except Exception as e:
            logger.error(f"Error downloading video: {e}", exc_info=True)
            raise

    def list_videos(self, prefix: Optional[str] = None) -> List[str]:
        """
        List videos in Azure Storage

        Args:
            prefix: Optional prefix to filter blobs

        Returns:
            List of blob names
        """
        logger.info(f"Listing videos with prefix: {prefix}")

        try:
            container_client = self._get_container_client()
            blobs = container_client.list_blobs(name_starts_with=prefix)

            blob_names = [blob.name for blob in blobs]
            logger.info(f"Found {len(blob_names)} videos")
            return blob_names

        except Exception as e:
            logger.error(f"Error listing videos: {e}", exc_info=True)
            return []

    def delete_video(self, blob_name: str):
        """
        Delete video from Azure Storage

        Args:
            blob_name: Name of blob to delete
        """
        logger.info(f"Deleting {blob_name}")

        try:
            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
            logger.info(f"Deleted: {blob_name}")

        except Exception as e:
            logger.error(f"Error deleting video: {e}", exc_info=True)
            raise

    def generate_sas_url(
        self, blob_name: str, expiry_hours: int = 24
    ) -> str:
        """
        Generate SAS URL for temporary access

        Args:
            blob_name: Name of blob
            expiry_hours: Hours until URL expires

        Returns:
            SAS URL for blob
        """
        try:
            from azure.storage.blob import generate_blob_sas, BlobSasPermissions

            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(blob_name)

            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=blob_client.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self._get_account_key(),
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours),
            )

            sas_url = f"{blob_client.url}?{sas_token}"
            logger.info(f"Generated SAS URL for {blob_name}")
            return sas_url

        except Exception as e:
            logger.error(f"Error generating SAS URL: {e}", exc_info=True)
            return blob_client.url

    def _get_account_key(self) -> str:
        """Extract account key from connection string"""
        parts = dict(item.split("=", 1) for item in self.connection_string.split(";") if "=" in item)
        return parts.get("AccountKey", "")
