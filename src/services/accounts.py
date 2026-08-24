import secrets
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import accounts


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
        data: dict,
        user_id: int,
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
        data: dict,
        user_id: int,
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
