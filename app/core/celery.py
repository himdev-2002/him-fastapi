from celery import Celery
from app.core.config import settings

celery = Celery(
    "him_fastapi", 
    broker=settings.CELERY_BROKER_URL, 
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.celery.tasks.math', 'app.celery.tasks.notif', 'app.celery.tasks.file']
)

# Optional: configure some defaults
celery.conf.task_routes = {
    "app.celery.tasks.math.*": {"queue": "math"},
    "app.celery.tasks.notif.*": {"queue": "notif"},
    "app.celery.tasks.file.*": {"queue": "file"},
}
celery.conf.worker_prefetch_multiplier = 1

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Jakarta',
    enable_utc=True,
)