from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy_celery_beat.models import PeriodicTask, ClockedSchedule

from src.database.models.accounts import (
    UserModel,
    UserGroupModel,
    AbstractTokenModel
)
from src.schemas.accounts import UserRegistrationRequestSchema
from src.security.password import hash_password


async def get_user_by_email(
    db: AsyncSession,
    email: str
) -> UserModel | None:
    result = await db.execute(
        select(UserModel)
        .where(UserModel.email == email)
    )
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    data: UserRegistrationRequestSchema
) -> UserModel:
    group_id_result = await db.execute(
        select(UserGroupModel.id)
        .where(UserGroupModel.name == data.group.value)
    )
    group_id: int = group_id_result.scalar_one_or_none()
    user = UserModel(
        email=data.email,
        hashed_password=hash_password(data.password),
        group_id=group_id
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def create_token(
    db: AsyncSession,
    user_id: int,
    token_model: type[AbstractTokenModel]
) -> AbstractTokenModel:
    token_instance = token_model(user_id=user_id)

    db.add(token_instance)
    await db.commit()

    result = await db.execute(
        select(token_model)
        .options(joinedload(token_model.user))
        .where(token_model.user_id == user_id)
    )
    token = result.scalar_one()

    return token


async def create_periodic_task_to_delete_activation_token(
    db: AsyncSession,
    user_id: int,
    token_expired_time: datetime
) -> None:
    clocked_schedule = ClockedSchedule(
        clocked_time=token_expired_time
    )

    db.add(clocked_schedule)
    await db.flush()

    periodic_task = PeriodicTask(
        schedule_model=clocked_schedule,
        name=f"Remove expired activation token of user {user_id}",
        task="src.celery_beat.tasks.delete_expired_activation_token",
        one_off=True,
        args=f"[{user_id}]"
    )
    db.add(periodic_task)
    await db.commit()
