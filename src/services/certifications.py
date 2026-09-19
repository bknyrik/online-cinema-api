from src.services import mixins
from src.repositories.movies import CertificationRepository


class CertificationService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin
):

    def __init__(
        self,
        certification_repository: CertificationRepository
    ) -> None:
        self.certification_repository = certification_repository
