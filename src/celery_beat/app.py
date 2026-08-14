from celery import Celery

from src.settings import settings


app = Celery(
    "online_cinema",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)
