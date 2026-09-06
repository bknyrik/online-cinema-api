from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.accounts import UserModel, UserProfileModel
from src.repositories.profiles import UserProfileRepository


class UserProfileService:

    @staticmethod
    async def read_current_user_profile(
        db: AsyncSession,
        current_user: UserModel
    ) -> UserProfileModel:
        user_profile_repository = UserProfileRepository()

        profile = await user_profile_repository.aget_by_user_id(
            db=db,
            user_id=current_user.id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        return profile
