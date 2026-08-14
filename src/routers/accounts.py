from fastapi import APIRouter, status, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.accounts import (
    UserModel,
    ActivationTokenModel
)
from src.schemas.accounts import (
    UserRegistrationRequestSchema,
    UserRegistrationResponseSchema
)
from src.database.dependencies import get_db
from src.crud.accounts import create_user, get_user_by_email, create_token
from src.smtp import emails


router = APIRouter()


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRegistrationResponseSchema
)
async def register_user(
    data: UserRegistrationRequestSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    user = await get_user_by_email(db, data.email)

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with this email {repr(data.email)} exists."
        )

    user = await create_user(db, data)
    activation_token = await create_token(
        db=db,
        user_id=user.id,
        token_model=ActivationTokenModel
    )
    activation_link = "http://127.0.0.1:8000/api/accounts/activate/"

    background_tasks.add_task(
        emails.send_activation_email,
        user.email,
        activation_link,
        activation_token.token
    )
    return user
