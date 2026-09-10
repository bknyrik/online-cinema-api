from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import AsyncBaseRepository
from src.database.models import movies


class GenreRepository(AsyncBaseRepository[movies.GenreModel]):

    def __init__(self) -> None:
        super().__init__(movies.GenreModel)


class StarRepository(AsyncBaseRepository[movies.StarModel]):

    def __init__(self) -> None:
        super().__init__(movies.StarModel)


class DirectorRepository(AsyncBaseRepository[movies.DirectorModel]):

    def __init__(self) -> None:
        super().__init__(movies.DirectorModel)


class CertificationRepository(AsyncBaseRepository[movies.CertificationModel]):

    def __init__(self) -> None:
        super().__init__(movies.CertificationModel)


class MovieRepository(AsyncBaseRepository[movies.MovieModel]):

    def __init__(self) -> None:
        super().__init__(movies.MovieModel)

    async def aget_by_name_year_time(
        self,
        db: AsyncSession,
        name: str,
        year: int,
        time: int
    ) -> movies.MovieModel | None:
        result = await db.execute(
            select(self._model_type)
            .where(self._model_type.name == name)
            .where(self._model_type.year == year)
            .where(self._model_type.time == time)
        )
        return result.scalar_one_or_none()
