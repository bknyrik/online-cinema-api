from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.services import mixins
from src.repositories.movies import MovieRepository
from src.repositories.rating import LikeMovieRepository, CommentMovieRepository
from src.database.models.rating import LikeMovieModel, CommentMovieModel
from src.database.models.accounts import UserProfileModel


class LikeMovieService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin[LikeMovieModel]
):
    def __init__(self) -> None:
        self.like_movie_repository = LikeMovieRepository()
        self.movie_repository = MovieRepository()

    async def get_like_movie_list(
        self,
        pagination_data: dict,
        db: AsyncSession,
        current_user_profile: UserProfileModel
    ) -> dict:
        try:
            expressions = [
                LikeMovieModel.profile_id == current_user_profile.id
            ]
            limit, offset = self.get_limit_offset(pagination_data)
            total_likes = await self.like_movie_repository.acount(
                db=db,
                expressions=expressions
            )
            total_pages = self.get_total_pages(
                total_items=total_likes,
                per_page=pagination_data["per_page"]
            )

            likes = await self.like_movie_repository.aget_all(
                db=db,
                limit=limit,
                offset=offset,
                expressions=expressions,
                order_by_columns=[LikeMovieModel.profile_id]
            )
            prev_page, next_page = self.get_prev_next_urls_pages(
                url="/api/likes-movies/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params=pagination_data
            )

            return {
                "likes": likes,
                "total_likes": total_likes,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with movie likes"
            )

    async def create_like_movie(
        self,
        db: AsyncSession,
        data: dict,
        current_user_profile: UserProfileModel
    ) -> LikeMovieModel:
        try:
            movie = await self.movie_repository.aget_by_id(
                db=db,
                id_=data["movie_id"]
            )

            self.validate_item_by_id_not_found(movie, data["movie_id"], "Movie")

            like = await self.like_movie_repository.aget_by(
                db=db,
                expressions=[
                    LikeMovieModel.movie_id == data["movie_id"],
                    LikeMovieModel.profile_id == current_user_profile.id
                ]
            )

            self.validate_item_by_attrs_exists(
                item=like,
                attrs=data,
                item_type="Like"
            )

            data["profile_id"] = current_user_profile.id

            like = await self.like_movie_repository.acreate(
                db=db,
                data=data,
            )

            await db.commit()
            return like
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while like movie creation"
            )

    async def delete_like_movie(
        self,
        db: AsyncSession,
        like_movie_id: int,
        current_user_profile: UserProfileModel
    ) -> None:
        try:
            like = await self.like_movie_repository.adelete_by(
                db=db,
                expressions=[
                    LikeMovieModel.id == like_movie_id,
                    LikeMovieModel.profile_id == current_user_profile.id
                ]
            )

            self.validate_item_by_id_not_found(like, like_movie_id, "Like")

            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while like movie deletion"
            )


class CommentMovieService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin
):

    def __init__(self) -> None:
        self.movie_repository = MovieRepository()
        self.comment_repository = CommentMovieRepository()

    async def create_comment(
        self,
        db: AsyncSession,
        data: dict
    ) -> CommentMovieModel:
        try:
            comment = await self.comment_repository.acreate(
                db=db,
                data=data
            )
            await db.commit()
            return comment
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while comment creation"
            )
