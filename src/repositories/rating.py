from src.repositories.base import AsyncBaseRepository

from src.database.models import rating


class LikeMovieRepository(AsyncBaseRepository[rating.MovieLikeModel]):

    def __init__(self) -> None:
        super().__init__(rating.MovieLikeModel)


class CommentMovieRepository(AsyncBaseRepository[rating.CommentMovieModel]):

    def __init__(self) -> None:
        super().__init__(rating.CommentMovieModel)
