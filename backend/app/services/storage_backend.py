"""Pluggable storage — local disk (default) or S3-compatible object storage."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO

from app.core.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class StorageBackend(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes) -> str:
        raise NotImplementedError

    @abstractmethod
    def open_path(self, key: str) -> Path | None:
        """Local path for processing (download from S3 to temp if needed)."""
        raise NotImplementedError

    @abstractmethod
    def signed_url(self, key: str, expires_seconds: int = 3600) -> str | None:
        raise NotImplementedError


class LocalStorageBackend(StorageBackend):
    def __init__(self) -> None:
        self.root = get_settings().storage_original

    def save(self, key: str, data: bytes) -> str:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return str(path)

    def open_path(self, key: str) -> Path | None:
        path = Path(key) if Path(key).is_absolute() else self.root / key
        return path if path.exists() else None

    def signed_url(self, key: str, expires_seconds: int = 3600) -> str | None:
        return None


class S3StorageBackend(StorageBackend):
    """S3-compatible backend — requires boto3 and env credentials."""

    def __init__(self) -> None:
        settings = get_settings()
        self.bucket = settings.s3_bucket
        self.prefix = settings.s3_prefix.strip("/")
        self._client = None

    def _get_client(self):
        if self._client is None:
            import boto3

            settings = get_settings()
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.s3_endpoint_url or None,
                region_name=settings.s3_region,
                aws_access_key_id=settings.s3_access_key_id or None,
                aws_secret_access_key=settings.s3_secret_access_key or None,
            )
        return self._client

    def _full_key(self, key: str) -> str:
        return f"{self.prefix}/{key}" if self.prefix else key

    def save(self, key: str, data: bytes) -> str:
        client = self._get_client()
        full = self._full_key(key)
        client.put_object(Bucket=self.bucket, Key=full, Body=data)
        logger.info("s3_upload", bucket=self.bucket, key=full)
        return f"s3://{self.bucket}/{full}"

    def open_path(self, key: str) -> Path | None:
        settings = get_settings()
        temp = settings.storage_temp / "s3_cache"
        temp.mkdir(parents=True, exist_ok=True)
        local = temp / Path(key).name
        if local.exists():
            return local
        client = self._get_client()
        full = self._full_key(key)
        client.download_file(self.bucket, full, str(local))
        return local

    def signed_url(self, key: str, expires_seconds: int = 3600) -> str | None:
        client = self._get_client()
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": self._full_key(key)},
            ExpiresIn=expires_seconds,
        )


def get_storage_backend() -> StorageBackend:
    settings = get_settings()
    if settings.storage_backend == "s3":
        return S3StorageBackend()
    return LocalStorageBackend()
