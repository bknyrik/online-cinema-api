from celery import shared_task

from src.database.models.accounts import ActivationTokenModel
from src.database.config import SyncSessionLocal
from src.repositories.accounts import TokenRepository
from src.repositories.celery_beat import (
    PeriodicTaskRepository,
    ClockedScheduleRepository
)


@shared_task
def delete_expired_activation_token(user_id: int, schedule_id: int) -> None:
    token_repository = TokenRepository(ActivationTokenModel)
    ptr = PeriodicTaskRepository()
    csr = ClockedScheduleRepository()

    with SyncSessionLocal() as session:
        token_repository.delete_by_user_id(
            db=session,
            user_id=user_id
        )

        ptr.delete_by_schedule_id(
            db=session,
            schedule_id=schedule_id
        )

        csr.delete_by_id(
            db=session,
            id_=schedule_id
        )

        session.commit()
