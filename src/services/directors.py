from src.services import mixins
from src.repositories.movies import DirectorRepository


class DirectorService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin
):
    def __init__(self, director_repository: DirectorRepository) -> None:
        self.director_repository = director_repository
