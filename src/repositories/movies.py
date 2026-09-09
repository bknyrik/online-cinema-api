from src.repositories.base import AsyncBaseRepository

from src.database.models import movies


class GenreRepository(AsyncBaseRepository[movies.GenreModel]):

    def __init__(self) -> None:
        super().__init__(movies.GenreModel)


class StarRepository(AsyncBaseRepository[movies.StarModel]):

    def __init__(self) -> None:
        super().__init__(movies.StarModel)


class DirectorRepository(AsyncBaseRepository[movies.DirectorModel]):

    def __init__(self) -> None:
        super().__init__(movies.DirectorModel)


class CertificationRepository(AsyncBaseRepository[movies.CertificationModel]):

    def __init__(self) -> None:
        super().__init__(movies.CertificationModel)


class MovieRepository(AsyncBaseRepository[movies.Movie]):

    def __init__(self) -> None:
        super().__init__(movies.Movie)
