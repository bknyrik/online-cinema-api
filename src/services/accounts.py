from __future__ import annotations
from datetime import datetime, timezone

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.database.models import accounts
from src.services.security import PasswordSecurityService, JWTAuthService
from src.services.celery_beat import CeleryBeatService
from src.services.email_sender import EmailSenderService
from src.repositories.accounts import (
    UserRepository,
    UserGroupRepository,
    TokenRepository
)


class UserService:

    def __init__(
        self,
        user_repository: UserRepository,
        user_group_repository: UserGroupRepository,
        at_repository: TokenRepository,
        rt_repository: TokenRepository,
        prt_repository: TokenRepository,
    ):
        self.user_repository = user_repository
        self.user_group_repository = user_group_repository
        self.at_repository = at_repository
        self.rt_repository = rt_repository
        self.prt_repository = prt_repository

    @staticmethod
    async def register_user(
        db: AsyncSession,
        data: dict,
        pss: PasswordSecurityService,
        email_sender_service: EmailSenderService,
        background_tasks: BackgroundTasks
    ) -> accounts.UserModel:
        user_repository = UserRepository()
        user_group_repository = UserGroupRepository()
        token_repository = TokenRepository(accounts.ActivationTokenModel)

        user = await user_repository.aget_by_email(db, data["email"])

        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with this email {repr(data["email"])} exists."
            )

        try:
            group_name = "USER"
            group = await user_group_repository.aget_by_name(db, group_name)

            if not group:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid group {repr(group_name)}"
                )

            data["group_id"] = group.id
            data["hashed_password"] = pss.hash_password(data.pop("password"))

            user = await user_repository.acreate(db, data)

            activation_token = await token_repository.acreate(
                db=db,
                data={
                    "user_id": user.id,
                    "token": token_repository.generate_token(),
                    "expires_at": token_repository.get_expiration_date()
                },
            )

            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while user registration"
            )
        else:
            activation_link = "http://127.0.0.1:8000/api/accounts/activate/"

            background_tasks.add_task(
                email_sender_service.send_activation_email,
                user.email,
                activation_link,
                activation_token.token
            )
            background_tasks.add_task(
                CeleryBeatService.create_periodic_task_to_delete_activation_token,
                user.id,
                activation_token.expires_at
            )

        return user

    @staticmethod
    async def activate_user_account(data: dict, db: AsyncSession) -> dict:
        user_repository = UserRepository()
        token_repository = TokenRepository(accounts.ActivationTokenModel)

        user = await user_repository.aget_by_email(db, data["email"])

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with the given email '{data["email"]}' not found"
            )

        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is already active."
            )

        token_instance = await token_repository.aget_by_user_id(
            db=db,
            user_id=user.id,
        )

        if (
            not token_instance
            or token_instance.token != data["activation_token"]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )

        if token_instance.has_expired:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token is expired"
            )

        try:
            await user_repository.aupdate(
                db=db,
                instance=user,
                data={
                    "is_active": True,
                    "updated_at": datetime.now(timezone.utc)
                }
            )
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while account activation"
            )

        return {"message": "Your account is activated"}

    @staticmethod
    async def reactivate_user_account(
        data: dict,
        db: AsyncSession,
        background_tasks: BackgroundTasks,
        email_sender_service: EmailSenderService
    ) -> dict:
        user_repository = UserRepository()
        token_repository = TokenRepository(accounts.ActivationTokenModel)

        user = await user_repository.aget_by_email(db, data["email"])

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with given email '{data["email"]}' not found"
            )

        try:
            token = token_repository.generate_token()
            token_expiration_date = token_repository.get_expiration_date()

            token_instance = await token_repository.aupdate_by_user_id(
                db=db,
                user_id=user.id,
                data={"token": token, "expires_at": token_expiration_date}
            )

            if not token_instance:
                token_instance = await token_repository.acreate(
                    db=db,
                    data={
                        "user_id": user.id,
                        "expires_at": token_expiration_date,
                        "token": token
                    }
                )

            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while activating account"
            )
        else:
            activation_link = "http://localhost:8000/api/accounts/activate/"

            background_tasks.add_task(
                email_sender_service.send_activation_email,
                user.email,
                activation_link,
                token_instance.token
            )

        return {"message": "An activation link is sent to your email"}

    @staticmethod
    async def login(
        data: dict,
        pss: PasswordSecurityService,
        jwt_service: JWTAuthService,
        db: AsyncSession,
    ) -> dict:
        user_repository = UserRepository()
        token_repository = TokenRepository(accounts.RefreshTokenModel)

        user = await user_repository.aget_by_email(db, data["email"])

        if (
            not user
            or not pss.verify_password(data["password"], user.hashed_password)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid account with given credentials"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is not activated"
            )

        try:
            access_token = jwt_service.encode_token(
                user_id=user.id,
                token_type="access"
            )
            refresh_token = jwt_service.encode_token(
                user_id=user.id,
                token_type="refresh"
            )
            token_instance = await token_repository.acreate(
                db=db,
                data={
                    "user_id": user.id,
                    "token": refresh_token,
                    "expires_at": token_repository.get_expiration_date()
                }
            )

            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while login"
            )

        return {
            "access_token": access_token,
            "refresh_token": token_instance.token
        }

    @staticmethod
    async def logout(
        db: AsyncSession,
        data: dict,
    ) -> None:
        token_repository = TokenRepository(accounts.RefreshTokenModel)

        try:
            token_instance = await token_repository.aget_by_token(
                db=db,
                token=data["refresh_token"]
            )

            if not token_instance:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token is invalid"
                )

            await token_repository.adelete(
                db=db,
                instance=token_instance
            )
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while logout"
            )

    @staticmethod
    async def change_user_group(
        db: AsyncSession,
        data: dict,
        user_id: int
    ) -> dict:
        user_repository = UserRepository()
        user_group_repository = UserGroupRepository()

        try:
            group = await user_group_repository.aget_by_name(
                db=db,
                name=data["group"]
            )

            if not group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Group {data["group"]} not found"
                )

            user = await user_repository.aupdate_by_id(
                db=db,
                id_=user_id,
                data={
                    "group_id": group.id,
                    "updated_at": datetime.now(timezone.utc)
                }
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while changing user group"
            )

        return {
            "id": user.id,
            "email": user.email,
            "group": group.name
        }

    @staticmethod
    async def admin_activate_user_account(
        user_id: int,
        db: AsyncSession,
    ) -> dict:
        user_repository = UserRepository()

        user = await user_repository.aget_by_id(
            db=db,
            id_=user_id
        )

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
            await user_repository.aupdate(
                db=db,
                instance=user,
                data={
                    "is_active": True,
                    "updated_at": datetime.now(timezone.utc)
                }
            )
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while account activation"
            )

        return {"message": "Account is activated successfully"}

    @staticmethod
    async def change_user_password(
        db: AsyncSession,
        data: dict,
        current_user: accounts.UserModel,
        pss: PasswordSecurityService
    ) -> dict:
        user_repository = UserRepository()
        password_is_verified = pss.verify_password(
            raw_password=data["old_password"],
            hashed_password=current_user.hashed_password
        )

        if not password_is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The old password is invalid"
            )

        try:
            await user_repository.aupdate(
                db=db,
                instance=current_user,
                data={
                    "updated_at": datetime.now(timezone.utc),
                    "hashed_password": pss.hash_password(data["new_password"])
                }
            )
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while changing user password"
            )

        return {"message": "Password is changed successfully"}

    @staticmethod
    async def refresh_access_token(
        data: dict,
        jwt_auth_service: JWTAuthService,
        db: AsyncSession
    ) -> dict:
        user_repository = UserRepository()
        token_repository = TokenRepository(accounts.RefreshTokenModel)

        user = await user_repository.aget_by_email(db, data["email"])

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        token_instance = await token_repository.aget_by_token(
            db=db,
            token=data["refresh_token"],
        )

        if (
            not token_instance
            or token_instance.token != data["refresh_token"]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token is invalid or missing"
            )

        if token_instance.has_expired:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token is expired"
            )

        return {
            "access_token": jwt_auth_service.encode_token(
                user_id=user.id,
                token_type="access"
            )
        }

    @staticmethod
    async def reset_password(
        db: AsyncSession,
        data: dict,
        ess: EmailSenderService,
        background_tasks: BackgroundTasks
    ) -> dict:
        user_repository = UserRepository()
        token_repository = TokenRepository(accounts.PasswordResetTokenModel)

        user = await user_repository.aget_by_email(db, data["email"])

        if user and user.is_active:
            try:
                reset_password_link = (
                    "http://localhost:8000/accounts/me/reset_password/complete/"
                )

                data = {
                    "token": token_repository.generate_token(),
                    "expires_at": token_repository.get_expiration_date()
                }

                token_instance = await token_repository.aupdate_by_user_id(
                    db=db,
                    user_id=user.id,
                    data=data
                )

                if not token_instance:
                    data["user_id"] = user.id
                    token_instance = await token_repository.acreate(
                        db=db,
                        data=data
                    )
                await db.commit()
            except SQLAlchemyError:
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred while resetting user password"
                )
            else:
                background_tasks.add_task(
                    ess.send_reset_password_email,
                    user.email,
                    reset_password_link,
                    token_instance.token
                )

        return {
            "message": (
                "If you are registered, "
                "you will receive an email with information"
            )
        }

    @staticmethod
    async def reset_password_complete(
        db: AsyncSession,
        data: dict,
        pss: PasswordSecurityService
    ) -> dict:
        user_repository = UserRepository()
        token_repository = TokenRepository(accounts.PasswordResetTokenModel)

        user = await user_repository.aget_by_email(db, data["email"])

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        token_instance = await token_repository.aget_by_user_id(
            db=db,
            user_id=user.id,
        )

        if not token_instance or token_instance.token != data["token"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token is invalid"
            )

        if token_instance.has_expired:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has expired"
            )

        try:
            await user_repository.aupdate(
                db=db,
                instance=user,
                data={
                    "updated_at": datetime.now(timezone.utc),
                    "hashed_password": pss.hash_password(data["password"])
                }
            )
            await token_repository.adelete(
                db=db,
                instance=token_instance
            )
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while resetting password completion"
            )

        return {"message": "Password is changed successfully"}
