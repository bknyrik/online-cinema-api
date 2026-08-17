from fastapi import APIRouter, status, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.accounts import (
    UserModel,
    ActivationTokenModel,
    RefreshTokenModel,
)
from src.schemas.accounts import (
    UserRegistrationRequestSchema,
    UserRegistrationResponseSchema,
    LoginRequestSchema,
    LoginResponseSchema,
    UserDetailResponseSchema,
    ChangeUserGroupRequestSchema,
    MessageResponseSchema
)
from src.security.password import verify_password
from src.security.auth import create_access_token
from src.security.dependencies import get_current_user, require_admin_user
from src.database.dependencies import get_db
from src.crud.accounts import (
    create_user,
    update_user,
    get_user_by_email,
    get_user_by_id,
    create_token,
    update_token,
    delete_token,
    create_periodic_task_to_delete_activation_token
)
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
    background_tasks.add_task(
        create_periodic_task_to_delete_activation_token,
        db,
        user.id,
        activation_token.expires_at
    )
    return user


@router.post("/login/", response_model=LoginResponseSchema)
async def login(
    data: LoginRequestSchema,
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await get_user_by_email(db, data.email)

    if not user or not verify_password(user.hashed_password, data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid account with given credentials"
        )

    access_token = create_access_token(email=user.email)
    refresh_token_instance = await update_token(
        db=db,
        user_id=user.id,
        token_model=RefreshTokenModel
    )

    if not refresh_token_instance:
        refresh_token_instance = await create_token(
            db=db,
            user_id=user.id,
            token_model=RefreshTokenModel
        )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_instance.token
    }


@router.post("/logout/")
async def logout(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> None:
    await delete_token(db, current_user.id, RefreshTokenModel)


@router.patch(
    "/{user_id}/change_user_group/",
    response_model=UserDetailResponseSchema
)
async def change_user_group(
    user_id: int,
    data: ChangeUserGroupRequestSchema,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(require_admin_user)
) -> UserDetailResponseSchema:
    user = await update_user(
        db=db,
        user_id=user_id,
        data={"group": data.group}
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserDetailResponseSchema(
        id=user.id,
        email=user.email,
        group=user.group.name
    )


@router.patch("/{user_id}/activate/", response_model=MessageResponseSchema)
async def activate_user_account(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin_user)
) -> dict:
    user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already active."
        )

    await update_user(db, user.id, {"is_active": True})
    return {"message": "Account is activated successfully"}


@router.get("/me/", response_model=UserDetailResponseSchema)
async def read_current_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserDetailResponseSchema:
    return UserDetailResponseSchema(
        id=current_user.id,
        email=current_user.email,
        group=current_user.group.name
    )
