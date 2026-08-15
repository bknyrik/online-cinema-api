from celery import Celery

from src.settings import settings
from src.database.config import SQLALCHEMY_DATABASE_CELERY_BEAT_URL


app = Celery(
    "online_cinema",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)


app.conf.beat_dburi = SQLALCHEMY_DATABASE_CELERY_BEAT_URL
app.conf.beat_scheduler = "sqlalchemy_celery_beat.schedulers:DatabaseScheduler"
