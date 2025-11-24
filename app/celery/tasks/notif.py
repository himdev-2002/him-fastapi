import time
from app.core.celery import celery

@celery.task
def send_notification_email(recipient, subject, body):
    """Tugas pengiriman email."""
    print(f"[{celery.current_task.request.hostname}] Menjalankan tugas 'send_notification_email' ke {recipient}")
    time.sleep(2) # Simulasikan pengiriman email
    result = f"Email to {recipient} with subject '{subject}' sent."
    print(f"[{celery.current_task.request.hostname}] Tugas 'send_notification_email' selesai: {result}")
    return result