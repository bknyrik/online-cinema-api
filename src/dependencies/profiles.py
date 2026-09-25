from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.authentication import get_current_user
from dependencies.database import get_db
from src.database.models.accounts import UserProfileModel, UserModel
from src.repositories.profiles import UserProfileRepository


async def get_current_user_profile(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> UserProfileModel:
    repository = UserProfileRepository()

    profile = await repository.aget_by(
        db=db,
        expressions=[UserProfileModel.user_id == current_user.id]
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return profile
