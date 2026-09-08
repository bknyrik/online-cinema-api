from src.repositories.base import BaseRepository

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_celery_beat.models import PeriodicTask, ClockedSchedule


class PeriodicTaskRepository(BaseRepository):

    def __init__(self) -> None:
        super().__init__(PeriodicTask)

    def get_by_schedule_id(
        self,
        db: Session,
        schedule_id: int
    ) -> PeriodicTask | None:
        result = db.execute(
            select(self._model_type)
            .where(self._model_type.schedule_id == schedule_id)
        )
        return result.scalar_one_or_none()


class ClockedScheduleRepository(BaseRepository):

    def __init__(self) -> None:
        super().__init__(ClockedSchedule)
