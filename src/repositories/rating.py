from src.repositories.base import AsyncBaseRepository

from src.database.models import rating


class MovieLikeRepository(AsyncBaseRepository[rating.MovieLikeModel]):

    def __init__(self) -> None:
        super().__init__(rating.MovieLikeModel)


class MovieCommentRepository(AsyncBaseRepository[rating.MovieCommentModel]):

    def __init__(self) -> None:
        super().__init__(rating.MovieCommentModel)


class CommentReplyRepository(AsyncBaseRepository[rating.CommentReplyModel]):

    def __init__(self) -> None:
        super().__init__(rating.CommentReplyModel)


class CommentLikeRepository(AsyncBaseRepository[rating.CommentLikeModel]):

    def __init__(self) -> None:
        super().__init__(rating.CommentLikeModel)
