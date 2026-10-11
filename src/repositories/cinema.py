from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, ColumnElement, UnaryExpression, Row
from sqlalchemy.orm import joinedload, InstrumentedAttribute

from src.repositories.base import AsyncBaseRepository
from src.database.models import cinema
from src.database.models.rating import FavoriteMovieModel


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

    async def aget_all_with_movie_count(
        self,
        db: AsyncSession,
        limit: int,
        offset: int
    ) -> Sequence[Row]:
        result = await db.execute(
            select(
                self._model_type.id,
                self._model_type.name,
                func.count(cinema.MoviesGenresModel.c.movie_id)
                .label("movies")
            )
            .join(cinema.MoviesGenresModel, isouter=True)
            .group_by(cinema.GenreModel.id)
            .order_by(cinema.GenreModel.id)
            .limit(limit)
            .offset(offset)
        )

        return result.all()


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

    async def aget_all_by_profile_favorites(
        self,
        db: AsyncSession,
        profile_id: int,
        expressions: list[ColumnElement[bool]],
        join_relationships: list[str],
        order_by_columns: list[UnaryExpression | InstrumentedAttribute],
        limit: int,
        offset: int
    ) -> Sequence[cinema.MovieModel]:
        stmt = (
            select(self._model_type)
            .join_from(
                self._model_type,
                FavoriteMovieModel
            )
            .where(FavoriteMovieModel.profile_id == profile_id)
        )
        for relationship in join_relationships:
            stmt = stmt.options(
                joinedload(getattr(self._model_type, relationship))
            )

        stmt = stmt.where(*expressions)
        stmt = stmt.order_by(*order_by_columns)

        stmt = stmt.limit(limit)
        stmt = stmt.offset(offset)

        result = await db.execute(stmt)
        return result.unique().scalars().all()

