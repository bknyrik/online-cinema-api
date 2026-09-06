from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repositories.base import BaseRepository
from src.database.models.accounts import UserProfileModel


class UserProfileRepository(BaseRepository[UserProfileModel]):

    def __init__(self) -> None:
        super().__init__(UserProfileModel)

    async def aget_by_user_id(
        self,
        db: AsyncSession,
        user_id: int
    ) -> UserProfileModel | None:
        result = await db.execute(
            select(self._model_type)
            .where(self._model_type.user_id == user_id)
        )
        return result.scalar_one_or_none()
