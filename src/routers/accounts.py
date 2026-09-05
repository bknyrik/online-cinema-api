from fastapi import APIRouter, status, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.database.models.accounts import (
    UserModel,
    RefreshTokenModel,
    PasswordResetTokenModel
)
from src.schemas.accounts import (
    UserRegistrationRequestSchema,
    UserRegistrationResponseSchema,
    LoginRequestSchema,
    LoginResponseSchema,
    UserDetailResponseSchema,
    ChangeUserGroupRequestSchema,
    ChangeUserPasswordRequestSchema,
    ResetUserPasswordRequestSchema,
    ResetPasswordCompleteRequestSchema,
    RefreshAccessTokenRequestSchema,
    RefreshAccessTokenResponseSchema,
    ActivateUserAccountRequestSchema,
    MessageResponseSchema,
    ReactivateUserAccountRequestSchema
)
from src.security.password import verify_password
from src.security.auth import create_access_token
from src.security.dependencies import get_current_user, require_admin_user
from dependencies.database import get_db
from src.crud.accounts import (
    update_user,
    get_user_by_email,
    get_user_by_id,
    get_token_by_user_id,
    create_token,
    update_token,
    delete_token
)
from src.services.accounts import UserService
from src.services.security import PasswordSecurityService, JWTAuthService
from src.services.email_sender import EmailSenderService
from src.services import dependencies


router = APIRouter()


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRegistrationResponseSchema
)
async def register_user(
    data: UserRegistrationRequestSchema,
    background_tasks: BackgroundTasks,
    ess: EmailSenderService = Depends(dependencies.get_email_sender_service),
    pss: PasswordSecurityService = Depends(dependencies.get_password_secure_service),
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    return await UserService.register_user(
        db=db,
        data=data.model_dump(),
        email_sender_service=ess,
        pss=pss,
        background_tasks=background_tasks
    )


@router.post("/activate/", response_model=MessageResponseSchema)
async def activate_user_account(
    data: ActivateUserAccountRequestSchema,
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await UserService.activate_user_account(
        data=data.model_dump(),
        db=db
    )


@router.post("/activate/new/", response_model=MessageResponseSchema)
async def reactivate_user_account(
    data: ReactivateUserAccountRequestSchema,
    background_tasks: BackgroundTasks,
    ess: EmailSenderService = Depends(dependencies.get_email_sender_service),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await UserService.reactivate_user_account(
        data=data.model_dump(),
        background_tasks=background_tasks,
        email_sender_service=ess,
        db=db
    )


@router.post("/login/", response_model=LoginResponseSchema)
async def login(
    data: LoginRequestSchema,
    pss: PasswordSecurityService = Depends(dependencies.get_password_secure_service),
    jwt_service: JWTAuthService = Depends(dependencies.get_jwt_auth_service),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await UserService.login(
        data=data.model_dump(),
        db=db,
        jwt_service=jwt_service,
        pss=pss
    )


@router.post("/logout/")
async def logout(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> None:
    try:
        await delete_token(db, current_user.id, RefreshTokenModel)
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while logout"
        )


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
    try:
        user = await update_user(
            db=db,
            user_id=user_id,
            data={"group": data.group}
        )
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while changing user group"
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
async def admin_activate_user_account(
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

    try:
        await update_user(db, user.id, {"is_active": True})
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while account activation"
        )

    return {"message": "Account is activated successfully"}


@router.patch("/me/change_password/", response_model=MessageResponseSchema)
async def change_user_password(
    data: ChangeUserPasswordRequestSchema,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> dict:
    if not verify_password(current_user.hashed_password, data.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The old password is invalid"
        )

    try:
        await update_user(
            db=db,
            user_id=current_user.id,
            data={"password": data.new_password}
        )
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while changing user password"
        )

    return {"message": "Password is changed successfully"}


@router.post("/reset_password/", response_model=MessageResponseSchema)
async def reset_password(
    data: ResetUserPasswordRequestSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await get_user_by_email(db, data.email)

    if user and user.is_active:
        reset_password_link = (
            "http://localhost:8000/accounts/me/"
            "reset_password/complete/"
        )

        reset_password_token_instance = await get_token_by_user_id(
            db=db,
            user_id=user.id,
            token_model=PasswordResetTokenModel
        )
        try:
            if reset_password_token_instance:
                reset_password_token_instance = await update_token(
                    db=db,
                    user_id=user.id,
                    token_model=PasswordResetTokenModel
                )
            else:
                reset_password_token_instance = await create_token(
                    db=db,
                    user_id=user.id,
                    token_model=PasswordResetTokenModel
                )
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while resetting user password"
            )
        else:
            pass

    return {
        "message": (
            "If you are registered, "
            "you will receive an email with information"
        )
    }


@router.post(
    "/reset_password/complete/",
    response_model=MessageResponseSchema
)
async def reset_password_complete(
    data: ResetPasswordCompleteRequestSchema,
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await get_user_by_email(db, data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    reset_password_token_instance = await get_token_by_user_id(
        db=db,
        user_id=user.id,
        token_model=PasswordResetTokenModel
    )

    if not reset_password_token_instance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is invalid"
        )

    if reset_password_token_instance.has_expired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired"
        )

    try:
        await update_user(db, user.id, {"password": data.password})
        await delete_token(db, user.id, PasswordResetTokenModel)
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting password completion"
        )

    return {"message": "Password is changed successfully"}


@router.post(
    "/refresh_access_token/",
    response_model=RefreshAccessTokenResponseSchema
)
async def refresh_access_token(
    data: RefreshAccessTokenRequestSchema,
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await get_user_by_email(db, data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    refresh_token_instance = await get_token_by_user_id(
        db=db,
        user_id=user.id,
        token_model=RefreshTokenModel
    )

    if (
        not refresh_token_instance
        or refresh_token_instance.token != data.refresh_token
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is invalid or missing"
        )

    if refresh_token_instance.has_expired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is expired"
        )

    return {"access_token": create_access_token(data.email)}


@router.get("/me/", response_model=UserDetailResponseSchema)
async def read_current_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserDetailResponseSchema:
    return UserDetailResponseSchema(
        id=current_user.id,
        email=current_user.email,
        group=current_user.group.name
    )
