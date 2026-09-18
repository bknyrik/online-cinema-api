from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.repositories.base import AsyncBaseRepository
from src.database.models import movies


class GenreRepository(AsyncBaseRepository[movies.GenreModel]):

    def __init__(self) -> None:
        super().__init__(movies.GenreModel)

    async def acount_movies(self, db: AsyncSession) -> Sequence[int]:
        result = await db.execute(
            select(func.count(movies.MoviesGenresModel.c.movie_id))
            .join_from(
                self._model_type,
                movies.MoviesGenresModel,
                isouter=True
            )
            .group_by(self._model_type.id)
            .order_by(self._model_type.id)
        )
        return result.scalars().all()


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
