from celery import shared_task

from sqlalchemy import delete

from src.database.models.accounts import ActivationTokenModel
from src.database.config import SyncSessionLocal


@shared_task
def delete_expired_activation_token(user_id: int) -> None:
    with SyncSessionLocal as session:
        session.execute(
            delete(ActivationTokenModel)
            .where(ActivationTokenModel.user_id == user_id)
        )
        session.commit()
