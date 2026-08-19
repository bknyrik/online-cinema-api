import boto3
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.settings import settings
from src.database.models.accounts import UserProfileModel
from src.schemas.profiles import ProfileFormSchema


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


async def create_profile(
    db: AsyncSession,
    user_id: int,
    data: dict
) -> UserProfileModel:
    profile = UserProfileModel(**data, user_id=user_id)

    db.add(profile)
    await db.flush()

    return profile
