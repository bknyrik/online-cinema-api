from __future__ import annotations

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.database.models import accounts
from src.services.security import PasswordSecurityService
from src.services.celery_beat import CeleryBeatService
from src.services.email_sender import EmailSenderService
from src.repositories.accounts import (
    UserRepository,
    UserGroupRepository,
    TokenRepository
)


class UserService:

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
            group_name = data.pop("group")
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
                data={"user_id": user.id},
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
            await user_repository.aupdate_by_id(
                db=db,
                id_=user.id,
                data={"is_active": True}
            )
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while account activation"
            )
        else:
            await db.commit()

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
            token_instance = await token_repository.aget_by_user_id(
                db=db,
                user_id=user.id,
            )

            if not token_instance:
                token_instance = await token_repository.acreate(
                    db=db,
                    data=data
                )
            else:
                token_instance = await token_repository.aupdate_by_id(
                    db=db,
                    id_=token_instance.id,
                    data={"user_id": user.id}
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
