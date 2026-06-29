from celery import shared_task
from .services.pipeline import run_pipeline

@shared_task(bind=True, max_retries=3)
def process_document_async(self, document_id: str):
    try:
        run_pipeline(document_id)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)