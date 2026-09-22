from src.services import mixins
from src.repositories.rating import LikeMovieRepository
from src.database.models.rating import LikeMovieModel


class LikeMovieService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin[LikeMovieModel]
):
    def __init__(self) -> None:
        self.like_movie_repository = LikeMovieRepository()
