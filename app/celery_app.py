from celery import Celery
from app.config import get


celery_app = Celery(
    'async_worker',
    broker=get("CELERY_BROKER_URL"),
    backend=get("CELERY_RESULT_BACKEND")
)