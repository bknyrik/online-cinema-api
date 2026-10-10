from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.repositories.base import AsyncBaseRepository
from src.database.models import cinema


class GenreRepository(AsyncBaseRepository[cinema.GenreModel]):

    def __init__(self) -> None:
        super().__init__(cinema.GenreModel)

    async def acount_movies(self, db: AsyncSession) -> Sequence[int]:
        result = await db.execute(
            select(func.count(cinema.MoviesGenresModel.c.movie_id))
            .join_from(
                self._model_type,
                cinema.MoviesGenresModel,
                isouter=True
            )
            .group_by(self._model_type.id)
            .order_by(self._model_type.id)
        )
        return result.scalars().all()


class StarRepository(AsyncBaseRepository[cinema.StarModel]):

    def __init__(self) -> None:
        super().__init__(cinema.StarModel)


class DirectorRepository(AsyncBaseRepository[cinema.DirectorModel]):

    def __init__(self) -> None:
        super().__init__(cinema.DirectorModel)


class CertificationRepository(AsyncBaseRepository[cinema.CertificationModel]):

    def __init__(self) -> None:
        super().__init__(cinema.CertificationModel)


class MovieRepository(AsyncBaseRepository[cinema.MovieModel]):

    def __init__(self) -> None:
        super().__init__(cinema.MovieModel)
