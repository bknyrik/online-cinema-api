from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.repositories.movies import GenreRepository
from src.services.mixins import PaginationLimitOffsetMixin
from src.database.models.movies import GenreModel


class GenreService(PaginationLimitOffsetMixin):

    def __init__(self, genre_repository: GenreRepository) -> None:
        self.genre_repository = genre_repository

    async def get_genre_list(
        self,
        pagination_data: dict,
        db: AsyncSession
    ) -> dict:
        try:
            total_genres = await self.genre_repository.acount(db)
            total_pages = self.get_total_pages(
                total_items=total_genres,
                per_page=pagination_data["per_page"]
            )
            limit, offset = self.get_limit_offset(pagination_data)

            self.validate_page_not_found(
                page=pagination_data["page"],
                total_pages=total_pages,
                total_items=total_genres
            )

            genres = list(
                await self.genre_repository.aget_all(
                    db=db,
                    offset=offset,
                    limit=limit,
                )
            )
            count_movies = await self.genre_repository.acount_movies(db)
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with genres"
            )
        else:
            prev_page, next_page = self.get_prev_next_urls_pages(
                "/api/genres/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params=pagination_data
            )
            genres = [
                {"id": genre.id, "name": genre.name, "movies": count}
                for genre, count in zip(genres, count_movies)
            ]
            return {
                "genres": genres,
                "total_genres": total_genres,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }

    async def get_genre_detail(
        self,
        db: AsyncSession,
        genre_id: int
    ) -> GenreModel:
        try:
            genre = await self.genre_repository.aget_by_id(
                db=db,
                id_=genre_id,
                join_relationships=["movies"]
            )

            if not genre:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Genre with id {genre_id} not found"
                )

            return genre
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting the genre"
            )

    async def create_genre(
        self,
        db: AsyncSession,
        data: dict,
    ) -> GenreModel:
        try:
            genre = await self.genre_repository.aget_by(
                db=db,
                expressions=[GenreModel.name == data["name"]]
            )

            if genre:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Genre with name {repr(data["name"])} exists"
                )

            created_genre = await self.genre_repository.acreate(
                db=db,
                data=data
            )
            await db.commit()
            return created_genre
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while genre creation"
            )

    async def update_genre(
        self,
        db: AsyncSession,
        genre_id: int,
        data: dict
    ) -> GenreModel:
        try:
            genre = await self.genre_repository.aget_by_id(
                db=db,
                id_=genre_id
            )

            if not genre:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Genre with id {genre_id} not found"
                )

            another_genre = await self.genre_repository.aget_by(
                db=db,
                expressions=[GenreModel.name == data["name"]]
            )

            if another_genre and another_genre.name != genre.name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A genre with name {data['name']} exists"
                )

            await self.genre_repository.aupdate(db, genre, data)
            await db.commit()
            return genre
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERnAL_SERVER_ERROR,
                detail="An error occurred while genre updating"
            )

    async def delete_genre(
        self,
        db: AsyncSession,
        genre_id: int
    ) -> None:
        try:
            genre = await self.genre_repository.adelete_by_id(
                db=db,
                id_=genre_id
            )

            if not genre:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Genre with id {genre_id} not found"
                )

            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while genre deletion"
            )
