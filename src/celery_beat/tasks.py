from celery import shared_task

from sqlalchemy import delete

from src.database.config import SessionLocal
from src.database.models.accounts import ActivationTokenModel


@shared_task
async def delete_expired_activation_token(user_id: int) -> None:
    async with SessionLocal() as session:
        await session.execute(
            delete(ActivationTokenModel)
            .where(ActivationTokenModel.user_id == user_id)
        )
        await session.commit()
