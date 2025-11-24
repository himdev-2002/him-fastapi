"""
file_meta.py

Pydantic schemas for file metadata operations.
Provides validation and serialization for file metadata CRUD operations.
"""

from datetime import datetime
import io
from typing import Any, Optional, Union
from fastapi import File, UploadFile
from pydantic import BaseModel, ConfigDict, Field
from app.models.file_meta import FileStore
from app.schemas.response import SingleDataResponse, MultiDataResponse


class FileMetaBase(BaseModel):
    """Base schema for file metadata with common fields."""
    file_type: Optional[str] = Field(None, description="Type/category of the file", example="image")
    name: Optional[str] = Field(None, description="Original filename", example="photo.jpg")
    store_type: FileStore = Field(
        default=FileStore.RUSTFS,
        description="Storage backend type",
        example=FileStore.RUSTFS
    )


class FileMetaCreate(FileMetaBase):
    """Schema for creating new file metadata."""
    # file: Union[UploadFile, None] = None
    pass


class FileMetaUpdate(FileMetaBase):
    """Schema for updating file metadata."""
    # file: Union[UploadFile, None] = None
    pass

class FileMetaCreateDB(FileMetaBase):
    """Schema for file metadata response."""
    size: Optional[int] = Field(None, description="File size in bytes", example=1024000, gt=0)
    content_type: Optional[str] = Field(None, description="MIME type of the file", example="image/jpeg")
    rustfs_key: Optional[str] = Field(
        None,
        description="Unique key for rustfs storage",
        example="abc123def456"
    )
    minio_key: Optional[str] = Field(
        None,
        description="Unique key for minio storage",
        example="xyz789uvw012"
    )

    model_config = ConfigDict(from_attributes=True)

class FileMetaResponse(FileMetaBase):
    """Schema for file metadata response."""
    id: int = Field(..., description="Unique file metadata ID")
    size: Optional[int] = Field(None, description="File size in bytes", example=1024000, gt=0)
    content_type: Optional[str] = Field(None, description="MIME type of the file", example="image/jpeg")
    rustfs_key: Optional[str] = Field(
        None,
        description="Unique key for rustfs storage",
        example="abc123def456"
    )
    minio_key: Optional[str] = Field(
        None,
        description="Unique key for minio storage",
        example="xyz789uvw012"
    )
    uploaded_at: datetime = Field(..., description="Timestamp when file was uploaded")
    uploaded_by: int = Field(..., description="ID of user who uploaded the file")

    model_config = ConfigDict(from_attributes=True)


class FullFileMetaResponse(FileMetaResponse):
    """Full file metadata response with all fields."""
    model_config = ConfigDict(from_attributes=True)


class PublicFileMetaResponse(FullFileMetaResponse):
    """Public file metadata response with sensitive fields excluded."""
    uploaded_by: Optional[int] = Field(None, exclude=True)

    model_config = ConfigDict(from_attributes=True)


class JsonFileMetaResponse(SingleDataResponse):
    """JSON response wrapper for single file metadata."""
    dt: FileMetaResponse | None = None


class JsonFullFileMetaResponse(SingleDataResponse):
    """JSON response wrapper for full file metadata."""
    dt: FullFileMetaResponse | None = None


class JsonMultiFileMetaResponse(MultiDataResponse):
    """JSON response wrapper for multiple file metadata."""
    dtmap: dict[str, int] | None = Field(
        None,
        example={
            "id": 0,
            "file_type": 1,
            "name": 2,
            "size": 3,
            "store_type": 4,
            "content_type": 5,
            "uploaded_at": 6,
        }
    )
    dt: list[list[Any]] | None = Field(None)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tx": "get_file_metas-abc123def456-7890",
                "req": "req-xyz789uvw012-3456",
                "stat": True,
                "msg": "OK",
                "code": 600200,
                "dtmap": {
                    "id": 0,
                    "file_type": 1,
                    "name": 2,
                    "size": 3,
                    "store_type": 4,
                    "content_type": 5,
                    "uploaded_at": 6,
                },
                "dt": [
                    [1, "image", "photo.jpg", 1024000, "rustfs", "image/jpeg", "2025-01-01T12:00:00"],
                    [2, "document", "report.pdf", 2048000, "minio", "application/pdf", "2025-01-02T12:00:00"],
                ],
            }
        }
    )

