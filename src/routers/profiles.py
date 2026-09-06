from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from src.database.models.accounts import UserModel, UserProfileModel
from dependencies.authentication import get_current_user
from src.schemas.profiles import ProfileDetailResponseSchema


router = APIRouter()


@router.get("/me/", response_model=ProfileDetailResponseSchema)
async def read_current_user_profile(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> UserProfileModel:
    pass
