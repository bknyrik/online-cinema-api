from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.database.models.accounts import UserModel, UserProfileModel
from src.repositories.profiles import UserProfileRepository
from src.services.s3 import S3Service


class UserProfileService:

    def __init__(self, profile_repository: UserProfileRepository) -> None:
        self.profile_repository = profile_repository

    async def read_current_user_profile(
        self,
        db: AsyncSession,
        s3_service: S3Service,
        current_user: UserModel
    ) -> dict:

        profile = await self.profile_repository.aget_by_user_id(
            db=db,
            user_id=current_user.id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        return {
            "id": profile.id,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "gender": profile.gender,
            "date_of_birth": profile.date_of_birth,
            "avatar": f"{s3_service.root_image_url}{profile.avatar}",
            "info": profile.info
        }

    async def create_user_profile(
        self,
        db: AsyncSession,
        s3_service: S3Service,
        current_user: UserModel,
        data: dict
    ) -> dict:
        profile = await self.profile_repository.aget_by_user_id(
            db=db,
            user_id=current_user.id
        )

        if profile:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already has a profile"
            )
        key = s3_service.upload_image(
            user_id=current_user.id,
            image=data["avatar"]
        )
        data["avatar"] = key
        data["user_id"] = current_user.id

        try:
            profile = await self.profile_repository.acreate(
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

        return {
            "id": profile.id,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "gender": profile.gender,
            "date_of_birth": profile.date_of_birth,
            "avatar": f"{s3_service.root_image_url}{profile.avatar}",
            "info": profile.info
        }

    async def update_current_user_profile(
        self,
        db: AsyncSession,
        data: dict,
        current_user: UserModel,
        s3_service: S3Service
    ) -> dict:
        try:
            filtered_data = dict(
                filter(lambda item: item[1] is not None, data.items())
            )

            if filtered_data.get("avatar"):
                key = filtered_data["avatar"] = s3_service.upload_image(
                    user_id=current_user.id,
                    image=filtered_data["avatar"]
                )
                filtered_data["avatar"] = key

            profile = await self.profile_repository.aupdate_by_user_id(
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
            return {
                "id": profile.id,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "gender": profile.gender,
                "date_of_birth": profile.date_of_birth,
                "avatar": f"{s3_service.root_image_url}{profile.avatar}",
                "info": profile.info
            }

    async def delete_current_user_profile(
        self,
        db: AsyncSession,
        s3_service: S3Service,
        current_user: UserModel
    ) -> None:
        try:
            profile = await self.profile_repository.aget_by_user_id(
                db=db,
                user_id=current_user.id
            )

            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profile not found"
                )

            s3_service.delete_image(profile.avatar)

            await self.profile_repository.adelete(
                db=db,
                instance=profile
            )
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while profile deletion"
            )
