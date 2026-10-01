from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.services import mixins
from src.repositories.movies import MovieRepository
from src.repositories.rating import (
    MovieLikeRepository,
    MovieCommentRepository,
    CommentReplyRepository
)
from src.database.models.rating import MovieLikeModel, MovieCommentModel
from src.database.models.accounts import UserModel


class MovieLikeService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin[MovieLikeModel]
):
    def __init__(self) -> None:
        self.like_repository = MovieLikeRepository()
        self.movie_repository = MovieRepository()

    async def get_movie_like_list(
        self,
        pagination_data: dict,
        db: AsyncSession,
        current_user: UserModel
    ) -> dict:
        try:
            expressions = [
                MovieLikeModel.profile_id == current_user.profile.id
            ]
            limit, offset = self.get_limit_offset(pagination_data)
            total_likes = await self.like_repository.acount(
                db=db,
                expressions=expressions
            )
            total_pages = self.get_total_pages(
                total_items=total_likes,
                per_page=pagination_data["per_page"]
            )

            likes = await self.like_repository.aget_all(
                db=db,
                limit=limit,
                offset=offset,
                expressions=expressions,
                order_by_columns=[MovieLikeModel.profile_id]
            )
            prev_page, next_page = self.get_prev_next_urls_pages(
                url="/api/movie-likes/",
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

    async def create_movie_like(
        self,
        db: AsyncSession,
        data: dict,
        current_user: UserModel
    ) -> MovieLikeModel:
        try:
            movie = await self.movie_repository.aget_by_id(
                db=db,
                id_=data["movie_id"]
            )

            self.validate_item_by_id_not_found(movie, data["movie_id"], "Movie")

            like = await self.like_repository.aget_by(
                db=db,
                expressions=[
                    MovieLikeModel.movie_id == data["movie_id"],
                    MovieLikeModel.profile_id == current_user.profile.id
                ]
            )

            self.validate_item_by_attrs_exists(
                item=like,
                attrs=data,
                item_type="Like"
            )

            data["profile_id"] = current_user.profile.id

            like = await self.like_repository.acreate(
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

    async def delete_movie_like(
        self,
        db: AsyncSession,
        like_movie_id: int,
        current_user: UserModel
    ) -> None:
        try:
            like = await self.like_repository.adelete_by(
                db=db,
                expressions=[
                    MovieLikeModel.id == like_movie_id,
                    MovieLikeModel.profile_id == current_user.profile.id
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


class MovieCommentService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin,
    mixins.UserPermissionsMixin,
    mixins.FilterItemsMixin
):
    MODEL_TYPE = MovieCommentModel

    def __init__(self) -> None:
        self.movie_repository = MovieRepository()
        self.comment_repository = MovieCommentRepository()

    async def get_movie_comment_list(
        self,
        filter_data: dict,
        pagination_data: dict,
        db: AsyncSession,
        current_user: UserModel,
    ) -> dict:
        try:
            limit, offset = self.get_limit_offset(pagination_data)

            filter_expressions = self.get_filter_expressions(filter_data)

            if current_user.group.name == "user":
                filter_expressions.append(
                    MovieCommentModel.profile_id == current_user.profile.id
                )

            total_comments = await self.comment_repository.acount(
                db=db,
                expressions=filter_expressions
            )
            total_pages = self.get_total_pages(
                total_items=total_comments,
                per_page=pagination_data["per_page"]
            )

            self.validate_page_not_found(
                page=pagination_data["page"],
                total_pages=total_pages,
                total_items=total_comments
            )

            comments = await self.comment_repository.aget_all(
                db=db,
                limit=limit,
                offset=offset,
                expressions=filter_expressions
            )

            prev_page, next_page = self.get_prev_next_urls_pages(
                url="/api/rating/comments/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params={
                    **pagination_data,
                    **filter_data
                }
            )

            return {
                "comments": comments,
                "total_comments": total_comments,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with comments"
            )

    async def get_movie_comment_detail(
        self,
        db: AsyncSession,
        comment_id: int,
    ) -> MovieCommentModel:
        try:
            comment = await self.comment_repository.aget_by_id(
                db=db,
                id_=comment_id
            )

            self.validate_item_by_id_not_found(comment, comment_id, "Comment")
            return comment
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting comment"
            )

    async def create_movie_comment(
        self,
        db: AsyncSession,
        data: dict,
        current_user: UserModel
    ) -> MovieCommentModel:
        try:
            data["profile_id"] = current_user.profile.id
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

    async def update_movie_comment(
        self,
        db: AsyncSession,
        comment_id: int,
        data: dict,
        current_user: UserModel
    ) -> MovieCommentModel:
        try:
            comment = await self.comment_repository.aget_by_id(
                db=db,
                id_=comment_id
            )

            self.validate_item_by_id_not_found(comment, comment_id, "Comment")
            self.belongs_to_profile_or_is_admin_or_moderator(
                current_user=current_user,
                child_object=comment,
                child_object_type="Comment"
            )

            await self.comment_repository.aupdate(
                db=db,
                instance=comment,
                data=data
            )

            await db.commit()
            return comment
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating comment"
            )

    async def delete_movie_comment(
        self,
        db: AsyncSession,
        comment_id: int,
        current_user: UserModel
    ) -> None:
        try:
            comment = await self.comment_repository.aget_by_id(db, comment_id)

            self.validate_item_by_id_not_found(comment, comment_id, "Comment")
            self.belongs_to_profile_or_is_admin_or_moderator(
                current_user=current_user,
                child_object=comment,
                child_object_type="Comment"
            )

            await self.comment_repository.adelete(db, comment)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while comment deletion"
            )


class CommentReplyService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin,
    mixins.UserPermissionsMixin
):

    def __init__(self) -> None:
        self.reply_repository = CommentReplyRepository()
        self.comment_repository = MovieCommentRepository()
