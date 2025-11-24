from celery import group
from app.core.celery import celery
from app.models.user import User
from app.services.file_meta import create_file_meta
from app.core.database import get_db_txonly_async, get_db_async
from app.schemas.file_meta import FileMetaCreateDB
from app.utils.logger import log_api

ACT = "celery-file"

@celery.task(bind=True, acks_late=True)
async def insert_metadata(self, meta: FileMetaCreateDB, current_user: User):
    log_api(f"Calling celery::file::insert_metadata, retries: {self.request.retries}", level="INFO", act=ACT)
    db_write = await get_db_txonly_async()
    db_read = await get_db_async()
    try:
        file_meta = create_file_meta(db_write, db_read, meta, current_user.id)
        log_api(f"File metadata created successfully", file_meta_id=str(file_meta.id), level="INFO", act=ACT)
        return file_meta
    except Exception as e:
        log_api(f"Error during file metadata creation: {e}", level="ERROR", act=ACT)
        self.retry(countdown=2**self.request.retries, max_retries=3)
        return None
        