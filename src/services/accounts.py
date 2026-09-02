from __future__ import annotations
import secrets
from datetime import datetime, timezone, timedelta

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload, session
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
        user_repository = UserRepository(pss)
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

            user = await user_repository.acreate(db, data)
            activation_token = await token_repository.acreate(
                db=db,
                data=data,
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
    async def aget_user_group_by_name(
        db: AsyncSession,
        name: str
    ) -> accounts.UserGroupModel | None:
        result = await db.execute(
            select(accounts.UserGroupModel)
            .where(accounts.UserGroupModel.name == name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def aget_user_by_email(
        db: AsyncSession,
        email: str
    ) -> accounts.UserModel | None:
        result = await db.execute(
            select(accounts.UserModel)
            .where(accounts.UserModel.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def aget_user_by_id(
        db: AsyncSession,
        id_: int
    ) -> accounts.UserModel | None:
        result = await db.scalar(
            select(accounts.UserModel)
            .where(accounts.UserModel.id == id_)
        )
        return result.one_or_none()

    @staticmethod
    async def acreate_user(
        db: AsyncSession,
        data: dict,
        pss: PasswordSecurityService
    ) -> accounts.UserModel:
        password = pss.hash_password(data.pop("password"))
        user = accounts.UserModel(**data, hashed_password=password)

        db.add(user)
        await db.flush()

        return user

    @staticmethod
    async def aupdate_user_by_id(
        db: AsyncSession,
        id_: int,
        data: dict,
        pss: PasswordSecurityService
    ) -> accounts.UserModel | None:
        user = await UserService.aget_user_by_id(db, id_)

        if not user:
            return None

        user.email = data.get("email", user.email)
        user.is_active = data.get("is_active", user.is_active)

        if data.get("password"):
            user.hashed_password = pss.hash_password(data["password"])

        if data.get("group"):
            group = await UserService.aget_user_group_by_name(db, data["group"])
            user.group_id = group.id

        if data:
            user.updated_at = datetime.now(timezone.utc)

        await db.flush()

        return user

    @staticmethod
    async def adelete_user_by_id(
        db: AsyncSession,
        id_: int
    ) -> None:
        db.execute(
            delete(accounts.UserModel)
            .where(accounts.UserModel.id == id_)
        )
