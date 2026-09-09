from src.repositories.base import AsyncBaseRepository

from src.database.models import movies


class GenreRepository(AsyncBaseRepository[movies.GenreModel]):

    def __init__(self) -> None:
        super().__init__(movies.GenreModel)


class StarRepository(AsyncBaseRepository[movies.StarModel]):

    def __init__(self) -> None:
        super().__init__(movies.StarModel)


class DirectorRepository(AsyncBaseRepository[movies.Director]):

    def __init__(self) -> None:
        super().__init__(movies.Director)


class CertificationRepository(AsyncBaseRepository[movies.Certification]):

    def __init__(self) -> None:
        super().__init__(movies.Certification)


class MovieRepository(AsyncBaseRepository[movies.Movie]):

    def __init__(self) -> None:
        super().__init__(movies.Movie)
