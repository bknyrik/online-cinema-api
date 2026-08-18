from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.dependencies import get_db
from src.database.models.accounts import UserModel, UserProfileModel
from src.security.dependencies import get_current_user
from src.schemas.profiles import ProfileDetailResponseSchema
from src.crud.profiles import get_profile_by_user_id


router = APIRouter()


@router.get("/me/", response_model=ProfileDetailResponseSchema)
async def read_current_user_profile(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> UserProfileModel:
    profile = await get_profile_by_user_id(
        db=db,
        user_id=current_user.id
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account doesn't have a profile"
        )

    return profile
