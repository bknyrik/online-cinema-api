from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.models.accounts import UserModel, UserGroupModel
from src.schemas.accounts import UserRegistrationRequestSchema
from src.security.password import hash_password


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
