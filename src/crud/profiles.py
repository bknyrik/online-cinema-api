from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database.models.accounts import UserProfileModel


async def get_profile_by_user_id(
    db: AsyncSession,
    user_id: int
) -> UserProfileModel | None:
    result = await db.execute(
        select(UserProfileModel)
        .options(joinedload(UserProfileModel.user))
        .where(UserProfileModel.user_id == user_id)
    )
    return result.scalar_one_or_none()
