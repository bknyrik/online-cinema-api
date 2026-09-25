from src.repositories.base import AsyncBaseRepository

from src.database.models import rating


class LikeMovieRepository(AsyncBaseRepository[rating.LikeMovieModel]):

    def __init__(self) -> None:
        super().__init__(rating.LikeMovieModel)


class CommentMovieRepository(AsyncBaseRepository[rating.CommentMovieModel]):

    def __init__(self) -> None:
        super().__init__(rating.CommentMovieModel)
