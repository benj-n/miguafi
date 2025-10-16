from __future__ import annotations
import os
import uuid
from typing import BinaryIO

from ..core.config import settings


class StorageService:
    def save(self, fileobj: BinaryIO, filename: str, content_type: str | None = None) -> str:
        raise NotImplementedError


class LocalStorage(StorageService):
    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save(self, fileobj: BinaryIO, filename: str, content_type: str | None = None) -> str:
        ext = os.path.splitext(filename)[1]
        key = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join(self.base_dir, key)
        with open(path, 'wb') as f:
            f.write(fileobj.read())
        # Expose via /static/uploads/<key>
        return f"/static/uploads/{key}"


class S3Storage(StorageService):
    def __init__(self, endpoint_url: str | None, access_key: str, secret_key: str, region: str | None, bucket: str) -> None:
        import boto3  # type: ignore

        self.bucket = bucket
        self.s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )

    def save(self, fileobj: BinaryIO, filename: str, content_type: str | None = None) -> str:
        ext = os.path.splitext(filename)[1]
        key = f"dogs/{uuid.uuid4().hex}{ext}"
        extra_args = {'ContentType': content_type} if content_type else None
        self.s3.upload_fileobj(fileobj, self.bucket, key, ExtraArgs=extra_args or {})
        # Return virtual-hosted-style URL if possible, else path style via endpoint
        endpoint = settings.s3_endpoint_url.rstrip('/') if settings.s3_endpoint_url else None
        if endpoint and endpoint.startswith('http'):
            return f"{endpoint}/{settings.s3_bucket}/{key}"
        # Fallback generic URL
        return f"s3://{settings.s3_bucket}/{key}"


def get_storage() -> StorageService:
    if settings.storage_backend == 's3':
        if not all([settings.s3_access_key, settings.s3_secret_key, settings.s3_bucket]):
            raise RuntimeError("S3 storage misconfigured: missing access/secret/bucket")
        return S3Storage(
            endpoint_url=settings.s3_endpoint_url,
            access_key=settings.s3_access_key or '',
            secret_key=settings.s3_secret_key or '',
            region=settings.s3_region,
            bucket=settings.s3_bucket or '',
        )
    # default local
    return LocalStorage(settings.storage_local_dir)
