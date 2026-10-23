from fastapi import APIRouter, status, BackgroundTasks

from src.database.models import accounts as models
from src.schemas import accounts as schemas
from dependencies import (
    services,
    database,
    authentication
)


router = APIRouter()


@router.post(
    "/users/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserRegistrationResponseSchema
)
async def register_user(
    data: schemas.UserRegistrationRequestSchema,
    background_tasks: BackgroundTasks,
    user_service: services.UserServiceDep,
    ess: services.EmailSenderServiceDep,
    pss: services.PasswordSecurityServiceDep,
    db: database.AsyncSessionDep
) -> models.UserModel:
    return await user_service.register_user(
        db=db,
        data=data.model_dump(),
        email_sender_service=ess,
        pss=pss,
        background_tasks=background_tasks
    )


@router.post(
    "/users/activate/",
    response_model=schemas.MessageResponseSchema
)
async def activate_user_account(
    data: schemas.ActivateUserAccountRequestSchema,
    user_service: services.UserServiceDep,
    db: database.AsyncSessionDep,
) -> dict:
    return await user_service.activate_user_account(
        data=data.model_dump(),
        db=db
    )


@router.post(
    "/users/activate/new/",
    response_model=schemas.MessageResponseSchema
)
async def reactivate_user_account(
    data: schemas.ReactivateUserAccountRequestSchema,
    background_tasks: BackgroundTasks,
    user_service: services.UserServiceDep,
    ess: services.EmailSenderServiceDep,
    db: database.AsyncSessionDep,
) -> dict:
    return await user_service.reactivate_user_account(
        data=data.model_dump(),
        background_tasks=background_tasks,
        email_sender_service=ess,
        db=db
    )


@router.post("/login/", response_model=schemas.LoginResponseSchema)
async def login(
    data: schemas.LoginRequestSchema,
    user_service: services.UserServiceDep,
    pss: services.PasswordSecurityServiceDep,
    jwt_auth_service: services.JWTAuthServiceDep,
    db: database.AsyncSessionDep,
) -> dict:
    return await user_service.login(
        data=data.model_dump(),
        db=db,
        jwt_service=jwt_auth_service,
        pss=pss
    )


@router.post(
    "/logout/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def logout(
    data: schemas.LogoutRequestSchema,
    user_service: services.UserServiceDep,
    db: database.AsyncSessionDep,
    current_user: authentication.CurrentUserDep,
) -> None:
    return await user_service.logout(
        db=db,
        data=data.model_dump()
    )


@router.patch(
    "/{user_id}/change_user_group/",
    response_model=schemas.UserDetailResponseSchema
)
async def change_user_group(
    user_id: int,
    data: schemas.ChangeUserGroupRequestSchema,
    user_service: services.UserServiceDep,
    db: database.AsyncSessionDep,
    current_user: authentication.CurrentAdminDep
) -> dict:
    return await user_service.change_user_group(
        db=db,
        data=data.model_dump(),
        user_id=user_id
    )


@router.patch("/{user_id}/activate/", response_model=schemas.MessageResponseSchema)
async def admin_activate_user_account(
    user_id: int,
    user_service: services.UserServiceDep,
    db: database.AsyncSessionDep,
    current_user: authentication.CurrentAdminDep
) -> dict:
    return await user_service.admin_activate_user_account(
        user_id=user_id,
        db=db
    )


@router.patch("/me/change_password/", response_model=schemas.MessageResponseSchema)
async def change_user_password(
    data: schemas.ChangeUserPasswordRequestSchema,
    user_service: services.UserServiceDep,
    pss: services.PasswordSecurityServiceDep,
    db: database.AsyncSessionDep,
    current_user: authentication.CurrentUserDep,
) -> dict:
    return await user_service.change_user_password(
        db=db,
        current_user=current_user,
        data=data.model_dump(),
        pss=pss
    )


@router.post("/reset_password/", response_model=schemas.MessageResponseSchema)
async def reset_password(
    data: schemas.ResetUserPasswordRequestSchema,
    background_tasks: BackgroundTasks,
    user_service: services.UserServiceDep,
    ess: services.EmailSenderServiceDep,
    db: database.AsyncSessionDep,
) -> dict:
    return await user_service.reset_password(
        db=db,
        background_tasks=background_tasks,
        data=data.model_dump(),
        ess=ess
    )


@router.post(
    "/reset_password/complete/",
    response_model=schemas.MessageResponseSchema
)
async def reset_password_complete(
    data: schemas.ResetPasswordCompleteRequestSchema,
    user_service: services.UserServiceDep,
    pss: services.PasswordSecurityServiceDep,
    db: database.AsyncSessionDep,
) -> dict:
    return await user_service.reset_password_complete(
        db=db,
        data=data.model_dump(),
        pss=pss
    )


@router.post(
    "/refresh_access_token/",
    response_model=schemas.RefreshAccessTokenResponseSchema
)
async def refresh_access_token(
    data: schemas.RefreshAccessTokenRequestSchema,
    user_service: services.UserServiceDep,
    jwt_auth_service: services.JWTAuthServiceDep,
    db: database.AsyncSessionDep,
) -> dict:
    return await user_service.refresh_access_token(
        db=db,
        data=data.model_dump(),
        jwt_auth_service=jwt_auth_service
    )


@router.get("/users/me/", response_model=schemas.UserDetailResponseSchema)
async def get_current_user(
    current_user: authentication.CurrentUserDep
) -> models.UserModel:
    return current_user


@router.get("/profiles/me/", response_model=schemas.UserProfileDetailResponseSchema)
async def get_current_user_profile(
    s3_service: services.S3ServiceDep,
    user_profile_service: services.UserProfileServiceDep,
    current_user: authentication.CurrentUserDep
) -> models.UserProfileModel:
    return await user_profile_service.get_current_user_profile(
        current_user=current_user,
        s3_service=s3_service
    )


@router.post(
    "/profiles/",
    response_model=schemas.UserProfileDetailResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_user_profile(
    data: schemas.UserProfileForm,
    s3_service: services.S3ServiceDep,
    user_profile_service: services.UserProfileServiceDep,
    db: database.AsyncSessionDep,
    current_user: authentication.CurrentUserDep,
) -> models.UserProfileModel:
    return await user_profile_service.create_user_profile(
        db=db,
        data=data.model_dump(),
        s3_service=s3_service,
        current_user=current_user
    )


@router.patch("/profiles/me/", response_model=schemas.UserProfileDetailResponseSchema)
async def update_current_user_profile(
    data: schemas.UserProfileForm,
    s3_service: services.S3ServiceDep,
    user_profile_service: services.UserProfileServiceDep,
    db: database.AsyncSessionDep,
    current_user: authentication.CurrentUserDep
) -> models.UserProfileModel:
    return await user_profile_service.update_current_user_profile(
        db=db,
        data=data.model_dump(exclude_none=True),
        current_user=current_user,
        s3_service=s3_service
    )


@router.delete(
    "/profiles/me/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_current_user_profile(
    s3_service: services.S3ServiceDep,
    user_profile_service: services.UserProfileServiceDep,
    db: database.AsyncSessionDep,
    current_user: authentication.CurrentUserDep
) -> None:
    return await user_profile_service.delete_current_user_profile(
        db=db,
        s3_service=s3_service,
        current_user=current_user
    )
