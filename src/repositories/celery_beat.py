from sqlalchemy_celery_beat.models import PeriodicTask, ClockedSchedule

from src.repositories.base import SyncBaseRepository


class PeriodicTaskRepository(SyncBaseRepository[PeriodicTask]):

    def __init__(self) -> None:
        super().__init__(PeriodicTask)


class ClockedScheduleRepository(SyncBaseRepository[ClockedSchedule]):

    def __init__(self) -> None:
        super().__init__(ClockedSchedule)
