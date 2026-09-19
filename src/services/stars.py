from src.repositories.movies import StarRepository
from src.services import mixins


class StarService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin
):

    def __init__(self, star_repository: StarRepository) -> None:
        self.star_repository = star_repository
