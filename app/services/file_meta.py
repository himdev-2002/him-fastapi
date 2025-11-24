"""
file_meta.py

Service layer for file metadata CRUD operations.
Handles business logic for file metadata management.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import delete, insert, update
from app.models.file_meta import FileMeta, FileStore
from app.schemas.file_meta import FileMetaCreateDB, FileMetaUpdate, FullFileMetaResponse
from app.utils.database import map_to_pydantic
from app.utils.logger import log_api
from app.utils.helpers import model_to_dict


def get_file_meta_by_rustfs_key(db: Session, rustfs_key: str) -> FileMeta | None:
    """
    Retrieve a file metadata record by rustfs_key.

    Args:
        db (Session): Database session.
        rustfs_key (str): Rustfs storage key.

    Returns:
        FileMeta | None: File metadata object or None if not found.

    Raises:
        Exception: Logged and returns None on any database error.
    """
    log_api(f"Calling services::file_meta::get_file_meta_by_rustfs_key", level="DEBUG")
    try:
        file_meta = db.query(FileMeta).filter(FileMeta.rustfs_key == rustfs_key).first()
        if file_meta:
            log_api(f"File metadata found", level="DEBUG")
            return file_meta
        else:
            log_api(f"File metadata not found", level="ERROR")
            return None
    except Exception as e:
        log_api(f"Error during file metadata retrieval: {e}", level="ERROR")
        return None


def get_file_meta_by_minio_key(db: Session, minio_key: str) -> FileMeta | None:
    """
    Retrieve a file metadata record by minio_key.

    Args:
        db (Session): Database session.
        minio_key (str): Minio storage key.

    Returns:
        FileMeta | None: File metadata object or None if not found.

    Raises:
        Exception: Logged and returns None on any database error.
    """
    log_api(f"Calling services::file_meta::get_file_meta_by_minio_key", level="DEBUG")
    try:
        file_meta = db.query(FileMeta).filter(FileMeta.minio_key == minio_key).first()
        if file_meta:
            log_api(f"File metadata found", minio_key=minio_key, level="DEBUG")
            return file_meta
        else:
            log_api(f"File metadata not found", minio_key=minio_key, level="ERROR")
            return None
    except Exception as e:
        log_api(f"Error during file metadata retrieval: {e}", level="ERROR")
        return None


def create_file_meta(
    db_write: Session,
    db_read: Session,
    file_meta: FileMetaCreateDB,
    current_user_id: int
) -> FileMeta | None:
    """
    Create a new file metadata record.

    Args:
        db_write (Session): Database session for write operations.
        db_read (Session): Database session for read operations.
        file_meta (FileMetaCreateDB): File metadata creation data.
        current_user_id (int): ID of the user creating the file metadata.

    Returns:
        FileMeta | None: Created file metadata object or None if creation fails.

    Raises:
        Exception: Logged and returns None on any database error.
    """
    log_api(f"Calling services::file_meta::create_file_meta", level="INFO")
    try:
        new_file_meta = FileMeta(
            file_type=file_meta.file_type,
            name=file_meta.name,
            size=file_meta.size or None,
            store_type=file_meta.store_type or FileStore.RUSTFS,
            content_type=file_meta.content_type or "application/octet-stream",
            rustfs_key=file_meta.rustfs_key or None,
            minio_key=file_meta.minio_key or None,
            uploaded_at=datetime.now(),
            uploaded_by=current_user_id
        )
        stmt = insert(FileMeta).values(
            model_to_dict(new_file_meta, exclude=["id"])
        ).returning(None)
        db_write.execute(stmt)
        db_write.flush()
        db_write.commit()
        # Retrieve the created file metadata by unique key
        created_file_meta = None
        if file_meta.rustfs_key:
            created_file_meta = get_file_meta_by_rustfs_key(db_read, file_meta.rustfs_key)
        elif file_meta.minio_key:
            created_file_meta = get_file_meta_by_minio_key(db_read, file_meta.minio_key)
        else:
            # Fallback: query by name and uploaded_by (should be unique enough)
            created_file_meta = db_read.query(FileMeta).filter(
                FileMeta.name == file_meta.name,
                FileMeta.uploaded_by == current_user_id
            ).order_by(FileMeta.uploaded_at.desc()).first()
        print("D")
        if created_file_meta:
            log_api(
                f"File metadata created successfully",
                level="INFO"
            )
        return created_file_meta
    except Exception as e:
        log_api(f"Error during file metadata creation: {e}", level="ERROR")
        return None


def update_file_meta(
    db_write: Session,
    db_read: Session,
    file_meta: FileMeta,
    file_meta_update: FileMetaUpdate
) -> FileMeta | None:
    """
    Update an existing file metadata record.

    Args:
        db_write (Session): Database session for write operations.
        db_read (Session): Database session for read operations.
        file_meta (FileMeta): Existing file metadata object to update.
        file_meta_update (FileMetaUpdate): Updated file metadata data.

    Returns:
        FileMeta | None: Updated file metadata object or None if update fails.

    Raises:
        Exception: Logged and returns None on any database error.
    """
    log_api(f"Calling services::file_meta::update_file_meta", level="INFO")
    try:
        if file_meta:
            # Update only provided fields
            if file_meta_update.file_type is not None:
                file_meta.file_type = file_meta_update.file_type
            if file_meta_update.name is not None:
                file_meta.name = file_meta_update.name
            if file_meta_update.size is not None:
                file_meta.size = file_meta_update.size
            if file_meta_update.store_type is not None:
                file_meta.store_type = file_meta_update.store_type
            if file_meta_update.content_type is not None:
                file_meta.content_type = file_meta_update.content_type
            if file_meta_update.rustfs_key is not None:
                file_meta.rustfs_key = file_meta_update.rustfs_key
            if file_meta_update.minio_key is not None:
                file_meta.minio_key = file_meta_update.minio_key

            stmt = update(FileMeta).where(
                FileMeta.id == file_meta.id
            ).values(
                model_to_dict(file_meta, exclude=["id"])
            ).returning(None)
            db_write.execute(stmt)
            db_write.flush()
            db_write.commit()
            
            updated_file_meta = get_file_meta(db_read, file_meta.id)
            if updated_file_meta:
                log_api(
                    f"File metadata updated successfully",
                    file_meta_id=str(updated_file_meta.id),
                    level="INFO"
                )
            return updated_file_meta
        return None
    except Exception as e:
        log_api(f"Error during file metadata update: {e}", level="ERROR")
        return None


def delete_file_meta(db_write: Session, file_meta_id: int) -> bool:
    """
    Delete a file metadata record by ID.

    Args:
        db_write (Session): Database session for write operations.
        file_meta_id (int): ID of the file metadata to delete.

    Returns:
        bool: True if deletion succeeds, False otherwise.

    Raises:
        Exception: Logged and returns False on any database error.
    """
    log_api(f"Calling services::file_meta::delete_file_meta", level="INFO")
    try:
        stmt = delete(FileMeta).where(FileMeta.id == file_meta_id).returning(None)
        db_write.execute(stmt)
        db_write.flush()
        db_write.commit()
        log_api(
            f"File metadata deleted successfully",
            file_meta_id=str(file_meta_id),
            level="INFO"
        )
        return True
    except Exception as e:
        log_api(f"Error during file metadata deletion: {e}", level="ERROR")
        return False


def get_file_meta(db: Session, file_meta_id: int) -> FileMeta | None:
    """
    Retrieve a file metadata record by ID.

    Args:
        db (Session): Database session.
        file_meta_id (int): ID of the file metadata to retrieve.

    Returns:
        FileMeta | None: File metadata object or None if not found.

    Raises:
        Exception: Logged and returns None on any database error.
    """
    log_api(f"Calling services::file_meta::get_file_meta", level="DEBUG")
    try:
        file_meta = db.query(FileMeta).filter(FileMeta.id == file_meta_id).first()
        if file_meta:
            log_api(f"File metadata found", file_meta_id=str(file_meta_id), level="DEBUG")
            return file_meta
        else:
            log_api(f"File metadata not found", file_meta_id=str(file_meta_id), level="ERROR")
            return None
    except Exception as e:
        log_api(f"Error during file metadata retrieval: {e}", level="ERROR")
        return None

def get_file_metas(db: Session) -> list[FullFileMetaResponse] | None:
    """
    Retrieve all file metadata records.

    Args:
        db (Session): Database session.

    Returns:
        list[FullFileMetaResponse] | None: List of file metadata objects or None on error.

    Raises:
        Exception: Logged and returns None on any database error.
    """
    log_api(f"Calling services::file_meta::get_file_metas", level="INFO")
    try:
        file_metas = db.query(FileMeta).all()
        return map_to_pydantic(file_metas, FullFileMetaResponse)
    except Exception as e:
        log_api(f"Error during call services::file_meta::get_file_metas: {e}", level="ERROR")
        return None

