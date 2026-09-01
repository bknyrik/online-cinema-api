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


class UserService:

    @staticmethod
    async def register_user(
        db: AsyncSession,
        data: dict,
        pss: PasswordSecurityService,
        email_sender_service: EmailSenderService,
        token_service: TokenService,
        background_tasks: BackgroundTasks
    ) -> accounts.UserModel:
        user = await UserService.aget_user_by_email(db, data["email"])

        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with this email {repr(data["email"])} exists."
            )

        try:
            user = await UserService.acreate_user(db, data, pss)
            activation_token = await token_service.create_token(
                db=db,
                user_id=user.id,
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
        result = await db.scalar(
            select(accounts.UserGroupModel)
            .where(accounts.UserGroupModel.name == name)
        )
        return result.one_or_none()

    @staticmethod
    async def aget_user_by_email(
        db: AsyncSession,
        email: str
    ) -> accounts.UserModel | None:
        result = await db.scalar(
            select(accounts.UserModel)
            .where(accounts.UserModel.email == email)
        )
        return result.one_or_none()

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


class TokenService:

    def __init__(
        self,
        token_model: type[accounts.AbstractTokenModel]
    ) -> None:
        self.token_model = token_model

    async def get_token_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> accounts.AbstractTokenModel | None:
        token_result = await db.execute(
            select(self.token_model)
            .options(joinedload(self.token_model.user))
            .where(self.token_model.user_id == user_id)
        )
        return token_result.scalar_one_or_none()

    async def create_token(
        self,
        db: AsyncSession,
        user_id: int,
        **data
    ) -> accounts.AbstractTokenModel:
        expires_at = data.get(
            "expires_at",
            TokenService.get_expiration_date()
        )
        token = data.get(
            "token",
            TokenService.generate_secure_token()
        )
        token_instance = self.token_model(
            expires_at=expires_at,
            token=token,
            user_id=user_id
        )

        db.add(token_instance)
        await db.flush()
        return token_instance

    async def update_token(
        self,
        db: AsyncSession,
        user_id: int,
        **data
    ) -> accounts.AbstractTokenModel | None:
        token_instance = await self.get_token_by_user_id(db, user_id)

        if not token_instance:
            return None

        token_instance.expires_at = data.get(
            "expires_at",
            TokenService.get_expiration_date()
        )
        token_instance.token = data.get(
            "token",
            TokenService.generate_secure_token()
        )

        await db.flush()

        return token_instance

    def delete_token(self, db: session.Session, user_id: int) -> None:
        db.execute(
            delete(self.token_model)
            .where(self.token_model.user_id == user_id)
        )

    async def adelete_token(self, db: AsyncSession, user_id: int) -> None:
        await db.execute(
            delete(self.token_model)
            .where(self.token_model.user_id == user_id)
        )

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        return secrets.token_urlsafe(length)

    @staticmethod
    def get_expiration_date(td: timedelta = timedelta(days=1)) -> datetime:
        return datetime.now(timezone.utc) + td
