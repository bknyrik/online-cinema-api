from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.database.models.accounts import UserModel, UserProfileModel
from src.repositories.profiles import UserProfileRepository
from src.services.s3 import S3Service


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

    @staticmethod
    async def create_user_profile(
        db: AsyncSession,
        s3_service: S3Service,
        current_user: UserModel,
        data: dict
    ) -> UserProfileModel:
        user_profile_repository = UserProfileRepository()

        profile = await user_profile_repository.aget_by_user_id(
            db=db,
            user_id=current_user.id
        )

        if profile:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already has a profile"
            )

        data["avatar"] = s3_service.upload_image(
            user_id=current_user.id,
            image=data["avatar"]
        )
        data["user_id"] = current_user.id

        try:
            profile = await user_profile_repository.acreate(
                db=db,
                data=data
            )
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating profile"
            )

        return profile

    @staticmethod
    async def update_current_user_profile(
        db: AsyncSession,
        data: dict,
        current_user: UserModel,
        s3_service: S3Service
    ) -> UserProfileModel:
        user_profile_repository = UserProfileRepository()

        try:
            filtered_data = dict(
                filter(lambda item: item[1], data.items())
            )

            if filtered_data.get("avatar"):
                filtered_data["avatar"] = s3_service.upload_image(
                    user_id=current_user.id,
                    image=filtered_data["avatar"]
                )

            profile = await user_profile_repository.aupdate_by_user_id(
                db=db,
                user_id=current_user.id,
                data=filtered_data
            )

            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profile not found"
                )

            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating profile"
            )
        else:
            return profile

    @staticmethod
    async def delete_current_user_profile(
        db: AsyncSession,
        current_user: UserModel
    ) -> None:
        user_profile_repository = UserProfileRepository()

        try:
            profile = await user_profile_repository.adelete_by_user_id(
                db=db,
                user_id=current_user.id
            )

            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profile not found"
                )
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while profile deletion"
            )
