from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.services import mixins
from src.repositories.cinema import MovieRepository
from src.repositories import rating as repositories
from src.repositories.notifications import NotificationRepository
from src.database.models.cinema import MovieModel
from src.database.models import rating as models
from src.database.models.accounts import UserModel


class MovieLikeService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin,
    mixins.UserPermissionsMixin
):
    def __init__(self) -> None:
        self.model_type = models.MovieLikeModel
        self.like_repository = repositories.MovieLikeRepository()
        self.movie_repository = MovieRepository()

    async def get_movie_like_list(
        self,
        pagination_data: dict,
        db: AsyncSession,
        current_user: UserModel
    ) -> dict:
        try:
            self.has_profile(current_user)

            expressions = [
                self.model_type.profile_id == current_user.profile.id
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
                order_by_columns=[self.model_type.id]
            )
            prev_page, next_page = self.get_prev_next_urls_pages(
                url="/api/rating/movie-likes/",
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
    ) -> models.MovieLikeModel:
        try:
            self.has_profile(current_user)

            movie = await self.movie_repository.aget_by_id(
                db=db,
                id_=data["movie_id"]
            )

            self.validate_item_by_id_not_found(movie, data["movie_id"], "Movie")

            like = await self.like_repository.aget_by(
                db=db,
                expressions=[
                    self.model_type.movie_id == data["movie_id"],
                    self.model_type.profile_id == current_user.profile.id
                ]
            )

            self.validate_item_by_attrs_exists(
                item=like,
                attrs=data,
                item_type="Movie like"
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
                detail="An error occurred while movie like creation"
            )

    async def delete_movie_like(
        self,
        db: AsyncSession,
        like_movie_id: int,
        current_user: UserModel
    ) -> None:
        try:
            self.has_profile(current_user)

            like = await self.like_repository.aget_by_id(
                db=db,
                id_=like_movie_id
            )

            self.validate_item_by_id_not_found(
                item=like,
                id_=like_movie_id,
                item_type="Movie like"
            )
            self.belongs_to_profile_or_is_admin_or_moderator(
                current_user=current_user,
                child_object=like,
                child_object_type="Movie like"
            )

            await self.like_repository.adelete(db, like)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while movie like deletion"
            )


class MovieCommentService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin,
    mixins.UserPermissionsMixin,
    mixins.FilterItemsMixin
):

    def __init__(self) -> None:
        self.model_type = models.MovieCommentModel
        self.movie_repository = MovieRepository()
        self.comment_repository = repositories.MovieCommentRepository()

    async def get_movie_comment_list(
        self,
        filter_data: dict,
        pagination_data: dict,
        db: AsyncSession,
        current_user: UserModel,
    ) -> dict:
        try:
            self.has_profile_or_is_admin_or_moderator(current_user)

            limit, offset = self.get_limit_offset(pagination_data)

            filter_expressions = self.get_filter_expressions(filter_data)

            if current_user.group.name == "user":
                filter_expressions.append(
                    self.model_type.profile_id == current_user.profile.id
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
                expressions=filter_expressions,
                order_by_columns=[self.model_type.id]
            )

            prev_page, next_page = self.get_prev_next_urls_pages(
                url="/api/rating/movie-comments/",
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
                detail=(
                    "An error occurred while getting list "
                    "with movie comments"
                )
            )

    async def get_movie_comment_detail(
        self,
        db: AsyncSession,
        comment_id: int,
        current_user: UserModel
    ) -> models.MovieCommentModel:
        try:
            self.has_profile_or_is_admin_or_moderator(current_user)

            comment = await self.comment_repository.aget_by_id(
                db=db,
                id_=comment_id
            )

            self.validate_item_by_id_not_found(
                item=comment,
                id_=comment_id,
                item_type="Movie comment"
            )
            return comment
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting movie comment"
            )

    async def create_movie_comment(
        self,
        db: AsyncSession,
        data: dict,
        current_user: UserModel
    ) -> models.MovieCommentModel:
        try:
            self.has_profile(current_user)

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
    ) -> models.MovieCommentModel:
        try:
            self.has_profile_or_is_admin_or_moderator(current_user)

            comment = await self.comment_repository.aget_by_id(
                db=db,
                id_=comment_id
            )

            self.validate_item_by_id_not_found(
                item=comment,
                id_=comment_id,
                item_type="Movie comment"
            )

            self.belongs_to_profile_or_is_admin_or_moderator(
                current_user=current_user,
                child_object=comment,
                child_object_type="Movie comment"
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
                detail="An error occurred while updating movie comment"
            )

    async def delete_movie_comment(
        self,
        db: AsyncSession,
        comment_id: int,
        current_user: UserModel
    ) -> None:
        try:
            self.has_profile_or_is_admin_or_moderator(current_user)

            comment = await self.comment_repository.aget_by_id(db, comment_id)

            self.validate_item_by_id_not_found(
                item=comment,
                id_=comment_id,
                item_type="Movie comment"
            )
            self.belongs_to_profile_or_is_admin_or_moderator(
                current_user=current_user,
                child_object=comment,
                child_object_type="Movie comment"
            )

            await self.comment_repository.adelete(db, comment)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while movie comment deletion"
            )


class CommentReplyService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin,
    mixins.UserPermissionsMixin,
    mixins.FilterItemsMixin
):

    def __init__(self) -> None:
        self.model_type = models.CommentReplyModel
        self.reply_repository = repositories.CommentReplyRepository()
        self.comment_repository = repositories.MovieCommentRepository()
        self.notification_repository = NotificationRepository()

    async def get_comment_reply_list(
        self,
        filter_data: dict,
        pagination_data: dict,
        db: AsyncSession,
        current_user: UserModel
    ) -> dict:
        try:
            self.has_profile_or_is_admin_or_moderator(current_user)

            limit, offset = self.get_limit_offset(pagination_data)
            filter_expressions = self.get_filter_expressions(filter_data)

            if current_user.group.name == "user":
                filter_expressions.append(
                    self.model_type.profile_id == current_user.profile.id
                )

            total_replies = await self.reply_repository.acount(
                db=db,
                expressions=filter_expressions
            )
            total_pages = self.get_total_pages(
                total_items=total_replies,
                per_page=pagination_data["per_page"]
            )

            replies = await self.reply_repository.aget_all(
                db=db,
                expressions=filter_expressions,
                limit=limit,
                offset=offset,
                order_by_columns=[self.model_type.id]
            )

            prev_page, next_page = self.get_prev_next_urls_pages(
                "/api/rating/comment-replies/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params={
                    **pagination_data,
                    **filter_data
                }
            )
            return {
                "replies": replies,
                "total_replies": total_replies,
                "total_pages": total_pages,
                "prev": next_page,
                "next": prev_page
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with comment replies"
            )

    async def get_comment_reply_detail(
        self,
        reply_id: int,
        db: AsyncSession,
        current_user: UserModel
    ) -> models.CommentReplyModel:
        try:
            self.has_profile_or_is_admin_or_moderator(current_user)

            reply = await self.reply_repository.aget_by_id(
                db=db,
                id_=reply_id
            )

            self.validate_item_by_id_not_found(
                item=reply,
                id_=reply_id,
                item_type="Comment reply"
            )

            return reply
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting comment reply"
            )

    async def create_comment_reply(
        self,
        data: dict,
        db: AsyncSession,
        current_user: UserModel
    ) -> models.CommentReplyModel:
        try:
            self.has_profile(current_user)

            comment = await self.comment_repository.aget_by_id(
                db=db,
                id_=data["comment_id"],
                join_relationships=["profile"]
            )

            self.validate_item_by_id_not_found(
                item=comment,
                id_=data["comment_id"],
                item_type="Movie comment"
            )

            data["profile_id"] = current_user.profile.id

            reply = await self.reply_repository.acreate(db=db, data=data)

            await self.notification_repository.acreate(
                db=db,
                data={
                    "user_id": comment.profile.user_id,
                    "text": f"You got a reply to the comment \"{comment.text}\""
                }
            )

            await db.commit()
            return reply
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while comment reply creation"
            )

    async def update_comment_reply(
        self,
        reply_id: int,
        data: dict,
        db: AsyncSession,
        current_user: UserModel
    ) -> models.CommentReplyModel:
        try:
            self.has_profile_or_is_admin_or_moderator(current_user)

            data["profile_id"] = current_user.profile.id

            reply = await self.reply_repository.aget_by_id(
                db=db,
                id_=reply_id
            )

            self.validate_item_by_id_not_found(
                item=reply,
                id_=reply_id,
                item_type="Comment reply"
            )
            self.belongs_to_profile_or_is_admin_or_moderator(
                current_user=current_user,
                child_object=reply,
                child_object_type="Comment reply"
            )

            await self.reply_repository.aupdate(db, reply, data)
            await db.commit()

            return reply
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating comment reply"
            )

    async def delete_comment_reply(
        self,
        reply_id: int,
        db: AsyncSession,
        current_user: UserModel
    ) -> None:
        try:
            self.has_profile_or_is_admin_or_moderator(current_user)

            reply = await self.reply_repository.aget_by_id(
                db=db,
                id_=reply_id
            )

            self.validate_item_by_id_not_found(
                item=reply,
                id_=reply_id,
                item_type="Comment reply"
            )
            self.belongs_to_profile_or_is_admin_or_moderator(
                current_user=current_user,
                child_object=reply,
                child_object_type="Comment reply"
            )

            await self.reply_repository.adelete(db, reply)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while comment reply deletion"
            )


class CommentLikeService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin,
    mixins.FilterItemsMixin,
    mixins.UserPermissionsMixin
):

    def __init__(self) -> None:
        self.model_type = models.CommentLikeModel
        self.like_repository = repositories.CommentLikeRepository()
        self.comment_repository = repositories.MovieCommentRepository()
        self.notification_repository = NotificationRepository()

    async def get_comment_like_list(
        self,
        filter_data: dict,
        pagination_data: dict,
        db: AsyncSession,
        current_user: UserModel
    ) -> dict:
        try:
            self.has_profile(current_user)

            filter_expressions = self.get_filter_expressions(filter_data)

            if current_user.group.name == "user":
                filter_expressions.append(
                    models.CommentLikeModel.profile_id == current_user.profile.id
                )

            limit, offset = self.get_limit_offset(pagination_data)
            total_likes = await self.like_repository.acount(
                db=db,
                expressions=filter_expressions
            )
            total_pages = self.get_total_pages(
                total_items=total_likes,
                per_page=pagination_data["per_page"]
            )

            self.validate_page_not_found(
                page=pagination_data["page"],
                total_pages=total_pages,
                total_items=total_likes
            )

            likes = await self.like_repository.aget_all(
                db=db,
                expressions=filter_expressions,
                offset=offset,
                limit=limit,
                order_by_columns=[self.model_type.id]
            )

            prev_page, next_page = self.get_prev_next_urls_pages(
                url="/api/rating/comment-likes/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params={
                    **pagination_data,
                    **filter_data
                }
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
                detail="An error occurred while getting list with comment likes"
            )

    async def create_comment_like(
        self,
        data: dict,
        db: AsyncSession,
        current_user: UserModel
    ) -> models.CommentLikeModel:
        try:
            self.has_profile(current_user)

            comment = await self.comment_repository.aget_by_id(
                db=db,
                id_=data["comment_id"]
            )
            self.validate_item_by_id_not_found(comment, data["comment_id"], "Comment")

            data["profile_id"] = current_user.profile.id

            like = await self.like_repository.aget_by(
                db=db,
                expressions=[
                    self.model_type.comment_id == data["comment_id"],
                    self.model_type.profile_id == data["profile_id"]
                ]
            )

            self.validate_item_by_attrs_exists(
                item=like,
                attrs=data,
                item_type="Comment like"
            )

            like = await self.like_repository.acreate(
                db=db,
                data=data
            )
            await db.commit()

            return like
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while comment like creation"
            )

    async def delete_comment_like(
        self,
        db: AsyncSession,
        like_id: int,
        current_user: UserModel
    ) -> None:
        try:
            self.has_profile(current_user)

            like = await self.like_repository.aget_by_id(
                db=db,
                id_=like_id
            )

            self.validate_item_by_id_not_found(like, like_id, "Comment like")
            self.belongs_to_profile_or_is_admin_or_moderator(
                current_user=current_user,
                child_object=like,
                child_object_type="Comment like"
            )

            await self.like_repository.adelete(db, like)

            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while comment like deletion"
            )


class MovieRateService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin,
    mixins.FilterItemsMixin,
    mixins.UserPermissionsMixin
):

    def __init__(self) -> None:
        self.model_type = models.MovieRateModel
        self.rate_repository = repositories.MovieRateRepository()
        self.movie_repository = MovieRepository()

    async def get_movie_rate_list(
        self,
        pagination_data: dict,
        filter_data: dict,
        db: AsyncSession,
        current_user: UserModel
    ) -> dict:
        try:
            limit, offset = self.get_limit_offset(pagination_data)
            filter_expressions = self.get_filter_expressions(filter_data)

            if current_user.group.name == "user":
                filter_expressions.append(
                    self.model_type.profile_id == current_user.profile.id
                )

            total_rates = await self.rate_repository.acount(
                db=db,
                expressions=filter_expressions
            )
            total_pages = self.get_total_pages(
                total_items=total_rates,
                per_page=pagination_data["per_page"]
            )

            rates = await self.rate_repository.aget_all(
                db=db,
                expressions=filter_expressions,
                limit=limit,
                offset=offset,
                order_by_columns=[self.model_type.id]
            )

            prev_page, next_page = self.get_prev_next_urls_pages(
                "/api/rating/movie-rates/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params={
                    **pagination_data,
                    **filter_data
                }
            )

            return {
                "rates": rates,
                "total_rates": total_rates,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with movie rates"
            )

    async def get_movie_rate_detail(
        self,
        rate_id: int,
        db: AsyncSession,
        current_user: UserModel
    ) -> models.MovieRateModel:
        try:
            self.has_profile(current_user)

            rate = await self.rate_repository.aget_by_id(
                db=db,
                id_=rate_id
            )

            self.validate_item_by_id_not_found(rate, rate_id, "Movie rate")

            return rate
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting movie rate"
            )

    async def create_movie_rate(
        self,
        data: dict,
        db: AsyncSession,
        current_user: UserModel
    ) -> models.MovieRateModel:
        try:
            self.has_profile(current_user)

            rate = await self.rate_repository.aget_by(
                db=db,
                expressions=[models.MovieRateModel.movie_id == data["movie_id"]]
            )

            self.validate_item_by_attrs_exists(rate, data, "Movie rate")

            data["profile_id"] = current_user.profile.id

            rate = await self.rate_repository.acreate(db, data)

            await db.commit()
            return rate
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while movie rate creation"
            )

    async def update_movie_rate(
        self,
        rate_id: int,
        data: dict,
        db: AsyncSession,
        current_user: UserModel
    ) -> models.MovieRateModel:
        try:
            self.has_profile(current_user)

            rate = await self.rate_repository.aget_by_id(
                db=db,
                id_=rate_id
            )

            self.validate_item_by_id_not_found(rate, rate_id, "Movie rate")
            self.belongs_to_profile_or_is_admin_or_moderator(current_user, rate, "Movie rate")

            await self.rate_repository.aupdate(db, rate, data)

            await db.commit()
            return rate
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating movie rating"
            )

    async def delete_movie_rate(
        self,
        rate_id: int,
        db: AsyncSession,
        current_user: UserModel
    ) -> None:
        try:
            self.has_profile(current_user)

            rate = await self.rate_repository.aget_by_id(
                db=db,
                id_=rate_id
            )

            self.validate_item_by_id_not_found(rate, rate_id, "Movie rate")
            self.belongs_to_profile_or_is_admin_or_moderator(current_user, rate, "MovieRate")

            await self.rate_repository.adelete(db, rate)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while movie rate deletion"
            )


class FavoriteMovieService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin,
    mixins.UserPermissionsMixin,
    mixins.FilterItemsMixin,
    mixins.SearchItemsMixin,
    mixins.SortingItemsMixin
):

    def __init__(self) -> None:
       self.model_type = MovieModel
       self.favorite_movie_repository = repositories.FavoriteMovieRepository()
       self.movie_repository = MovieRepository()

    async def get_favorite_movie_list(
        self,
        filter_data: dict,
        search_data: dict,
        sort_data: dict,
        pagination_data: dict,
        db: AsyncSession,
        current_user: UserModel
    ) -> dict:
        try:
            self.has_profile(current_user)
            limit, offset = self.get_limit_offset(pagination_data)

            filter_expressions = self.get_filter_expressions(filter_data)
            sorting_expressions = self.get_sort_columns(sort_data)
            search_expressions = self.get_search_expressions(search_data)
            expressions = filter_expressions + search_expressions

            total_movies = await self.favorite_movie_repository.acount(
                db=db,
                expressions=expressions,
            )
            total_pages = self.get_total_pages(
                total_items=total_movies,
                per_page=pagination_data["per_page"]
            )

            movies = await self.movie_repository.aget_all_by_profile_favorites(
                db=db,
                profile_id=current_user.profile.id,
                expressions=expressions,
                limit=limit,
                offset=offset,
                join_relationships=[
                    "certification",
                    "genres",
                    "stars",
                    "directors"
                ],
                order_by_columns=(
                    sorting_expressions
                    if any(value is not None for value in sort_data.values())
                    else [self.model_type.id]
                )
            )

            prev_page, next_page = self.get_prev_next_urls_pages(
                url="/api/rating/movie-favorites/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params={
                    **pagination_data,
                    **filter_data,
                    **search_data,
                    **sort_data
                }
            )
            return {
                "movies": movies,
                "total_movies": total_movies,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with favorite movies"
            )

    async def add_movie_to_favorites(
        self,
        data: dict,
        db: AsyncSession,
        current_user: UserModel
    ) -> models.FavoriteMovieModel:
        try:
            self.has_profile(current_user)

            movie = await self.movie_repository.aget_by_id(
                db=db,
                id_=data["movie_id"]
            )

            self.validate_item_by_id_not_found(movie, data["movie_id"], "Movie")


            data["profile_id"] = current_user.profile.id

            favorite_movie = await self.favorite_movie_repository.aget_by(
                db=db,
                expressions=[
                    models.FavoriteMovieModel.profile_id == data["profile_id"],
                    models.FavoriteMovieModel.movie_id == data["movie_id"]
                ]
            )

            self.validate_item_by_attrs_exists(favorite_movie, data, "Movie")

            favorite_movie = await self.favorite_movie_repository.acreate(
                db=db,
                data=data
            )

            await db.commit()
            return favorite_movie
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while adding movie to favorites"
            )

    async def delete_movie_from_favorites(
        self,
        favorite_id: int,
        db: AsyncSession,
        current_user: UserModel
    ) -> None:
        try:
            self.has_profile(current_user)

            favorite_movie = await self.favorite_movie_repository.aget_by_id(
                db=db,
                id_=favorite_id
            )

            self.validate_item_by_id_not_found(
                item=favorite_movie,
                id_=favorite_id,
                item_type="Favorite movie"
            )

            await self.favorite_movie_repository.adelete(db, favorite_movie)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deletion movie from favorites"
            )
