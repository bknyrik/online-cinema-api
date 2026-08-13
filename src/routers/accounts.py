from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.accounts import UserModel
from src.schemas.accounts import (
    UserRegistrationRequestSchema,
    UserRegistrationResponseSchema
)
from src.database.dependencies import get_db
from src.crud.accounts import create_user, get_user_by_email


router = APIRouter()


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRegistrationResponseSchema
)
async def register_user(
    data: UserRegistrationRequestSchema,
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    user = await get_user_by_email(db, data.email)

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with this email {repr(data.email)} exists."
        )

    user = await create_user(db, data)
    return user
