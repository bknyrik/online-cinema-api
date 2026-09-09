from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from src.database.models.accounts import UserModel, UserProfileModel
from dependencies.authentication import get_current_user
from dependencies.services import get_s3_service, get_profile_service
from src.schemas.profiles import (
    ProfileDetailResponseSchema,
    ProfileFormSchema,
    ProfileUpdateFormSchema
)
from src.services.profiles import UserProfileService
from src.services.s3 import S3Service


router = APIRouter()


@router.get("/me/", response_model=ProfileDetailResponseSchema)
async def read_current_user_profile(
    db: AsyncSession = Depends(get_db),
    user_profile_service: UserProfileService = Depends(get_profile_service),
    current_user: UserModel = Depends(get_current_user)
) -> UserProfileModel:
    return await user_profile_service.read_current_user_profile(
        db=db,
        current_user=current_user
    )


@router.post("/", response_model=ProfileDetailResponseSchema)
async def create_user_profile(
    db: AsyncSession = Depends(get_db),
    user_profile_service: UserProfileService = Depends(get_profile_service),
    s3_service: S3Service = Depends(get_s3_service),
    current_user: UserModel = Depends(get_current_user),
    data: ProfileFormSchema = Depends(ProfileFormSchema.as_form)
) -> UserProfileModel:
    return await user_profile_service.create_user_profile(
        db=db,
        data=data.model_dump(),
        s3_service=s3_service,
        current_user=current_user
    )


@router.patch("/me/", response_model=ProfileDetailResponseSchema)
async def update_current_user_profile(
    db: AsyncSession = Depends(get_db),
    user_profile_service: UserProfileService = Depends(get_profile_service),
    s3_service: S3Service = Depends(get_s3_service),
    data: ProfileUpdateFormSchema = Depends(ProfileUpdateFormSchema.as_form),
    current_user: UserModel = Depends(get_current_user)
) -> UserProfileModel:
    return await user_profile_service.update_current_user_profile(
        db=db,
        data=data.model_dump(),
        current_user=current_user,
        s3_service=s3_service
    )


@router.delete("/me/")
async def delete_current_user_profile(
    db: AsyncSession = Depends(get_db),
    user_profile_service: UserProfileService = Depends(get_profile_service),
    current_user: UserModel = Depends(get_current_user)
) -> None:
    return await user_profile_service.delete_current_user_profile(
        db=db,
        current_user=current_user
    )
