from celery import shared_task

from src.database.models.accounts import ActivationTokenModel
from src.database.config import SyncSessionLocal
from src.services.accounts import TokenService
from src.services.celery_beat import CeleryBeatService

@shared_task
def delete_expired_activation_token(user_id: int, schedule_id: int) -> None:
    token_service = TokenService(ActivationTokenModel)

    with SyncSessionLocal() as session:
        token_service.delete_token(
            db=session,
            user_id=user_id
        )
        CeleryBeatService.delete_periodic_task_by_schedule_id(
            db=session,
            schedule_id=schedule_id
        )
        CeleryBeatService.delete_clocked_schedule(
            db=session,
            id_=schedule_id
        )
        session.commit()
