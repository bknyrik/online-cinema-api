from src.repositories.base import AsyncBaseRepository

from src.database.models import movies


class GenreRepository(AsyncBaseRepository[movies.Genre]):

    def __init__(self) -> None:
        super().__init__(movies.Genre)


class StarRepository(AsyncBaseRepository[movies.Star]):

    def __init__(self) -> None:
        super().__init__(movies.Star)
