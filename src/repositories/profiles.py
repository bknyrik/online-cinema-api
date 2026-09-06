from src.repositories.base import BaseRepository

from src.database.models.accounts import UserProfileModel


class UserProfileRepository(BaseRepository[UserProfileModel]):

    def __init__(self) -> None:
        super().__init__(UserProfileModel)
