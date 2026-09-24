from src.repositories.base import AsyncBaseRepository

from src.database.models import rating


class LikeMovieRepository(AsyncBaseRepository):

    def __init__(self) -> None:
        super().__init__(rating.LikeMovieModel)


class CommentMovieRepository(AsyncBaseRepository):

    def __init__(self) -> None:
        super().__init__(rating.CommentMovieModel)
