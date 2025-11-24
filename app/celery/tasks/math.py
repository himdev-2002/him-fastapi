import time
from app.core.celery import celery

@celery.task
def add(x, y):
    """Tugas ringan: menjumlahkan dua angka."""
    print(f"[{celery.current_task.request.hostname}] Menjalankan tugas 'add' ({x} + {y})")
    time.sleep(1) # Simulasikan sedikit delay
    result = x + y
    print(f"[{celery.current_task.request.hostname}] Tugas 'add' selesai: {result}")
    return result