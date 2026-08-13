from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

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
