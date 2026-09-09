from fastapi import APIRouter, status, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.accounts import UserModel
from src.schemas.accounts import (
    UserRegistrationRequestSchema,
    UserRegistrationResponseSchema,
    LoginRequestSchema,
    LoginResponseSchema,
    LogoutRequestSchema,
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
from dependencies.authentication import get_current_user, get_current_admin_user
from dependencies.database import get_db
from src.services.accounts import UserService
from src.services.security import PasswordSecurityService, JWTAuthService
from src.services.email_sender import EmailSenderService
from dependencies import services

router = APIRouter()


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRegistrationResponseSchema
)
async def register_user(
    data: UserRegistrationRequestSchema,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(services.get_user_service),
    ess: EmailSenderService = Depends(services.get_email_sender_service),
    pss: PasswordSecurityService = Depends(services.get_password_secure_service),
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    return await user_service.register_user(
        db=db,
        data=data.model_dump(),
        email_sender_service=ess,
        pss=pss,
        background_tasks=background_tasks
    )


@router.post("/activate/", response_model=MessageResponseSchema)
async def activate_user_account(
    data: ActivateUserAccountRequestSchema,
    user_service: UserService = Depends(services.get_user_service),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await user_service.activate_user_account(
        data=data.model_dump(),
        db=db
    )


@router.post("/activate/new/", response_model=MessageResponseSchema)
async def reactivate_user_account(
    data: ReactivateUserAccountRequestSchema,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(services.get_user_service),
    ess: EmailSenderService = Depends(services.get_email_sender_service),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await user_service.reactivate_user_account(
        data=data.model_dump(),
        background_tasks=background_tasks,
        email_sender_service=ess,
        db=db
    )


@router.post("/login/", response_model=LoginResponseSchema)
async def login(
    data: LoginRequestSchema,
    user_service: UserService = Depends(services.get_user_service),
    pss: PasswordSecurityService = Depends(services.get_password_secure_service),
    jwt_service: JWTAuthService = Depends(services.get_jwt_auth_service),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await user_service.login(
        data=data.model_dump(),
        db=db,
        jwt_service=jwt_service,
        pss=pss
    )


@router.post("/logout/")
async def logout(
    data: LogoutRequestSchema,
    user_service: UserService = Depends(services.get_user_service),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> None:
    return await user_service.logout(
        db=db,
        data=data.model_dump()
    )


@router.patch(
    "/{user_id}/change_user_group/",
    response_model=UserDetailResponseSchema
)
async def change_user_group(
    user_id: int,
    data: ChangeUserGroupRequestSchema,
    user_service: UserService = Depends(services.get_user_service),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
) -> dict:
    return await user_service.change_user_group(
        db=db,
        data=data.model_dump(),
        user_id=user_id
    )


@router.patch("/{user_id}/activate/", response_model=MessageResponseSchema)
async def admin_activate_user_account(
    user_id: int,
    user_service: UserService = Depends(services.get_user_service),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin_user)
) -> dict:
    return await user_service.admin_activate_user_account(
        user_id=user_id,
        db=db
    )


@router.patch("/me/change_password/", response_model=MessageResponseSchema)
async def change_user_password(
    data: ChangeUserPasswordRequestSchema,
    user_service: UserService = Depends(services.get_user_service),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    pss: PasswordSecurityService = Depends(services.get_password_secure_service)
) -> dict:
    return await user_service.change_user_password(
        db=db,
        current_user=current_user,
        data=data.model_dump(),
        pss=pss
    )


@router.post("/reset_password/", response_model=MessageResponseSchema)
async def reset_password(
    data: ResetUserPasswordRequestSchema,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(services.get_user_service),
    ess: EmailSenderService = Depends(services.get_email_sender_service),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await user_service.reset_password(
        db=db,
        background_tasks=background_tasks,
        data=data.model_dump(),
        ess=ess
    )


@router.post(
    "/reset_password/complete/",
    response_model=MessageResponseSchema
)
async def reset_password_complete(
    data: ResetPasswordCompleteRequestSchema,
    db: AsyncSession = Depends(get_db),
    pss: PasswordSecurityService = Depends(services.get_password_secure_service)
) -> dict:
    return await UserService.reset_password_complete(
        db=db,
        data=data.model_dump(),
        pss=pss
    )


@router.post(
    "/refresh_access_token/",
    response_model=RefreshAccessTokenResponseSchema
)
async def refresh_access_token(
    data: RefreshAccessTokenRequestSchema,
    jwt_auth_service: JWTAuthService = Depends(services.get_jwt_auth_service),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await UserService.refresh_access_token(
        db=db,
        data=data.model_dump(),
        jwt_auth_service=jwt_auth_service
    )


@router.get("/me/", response_model=UserDetailResponseSchema)
async def read_current_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserDetailResponseSchema:
    return UserDetailResponseSchema(
        id=current_user.id,
        email=current_user.email,
        group=current_user.group.name
    )
