from src.repositories.base import SyncBaseRepository

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy_celery_beat.models import PeriodicTask, ClockedSchedule


class PeriodicTaskRepository(SyncBaseRepository):

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

    def delete_by_schedule_id(
        self,
        db: Session,
        schedule_id
    ) -> PeriodicTask | None:
        instance = self.get_by_schedule_id(db, schedule_id)

        if not instance:
            return None

        self.delete(db, instance)

        return instance


class ClockedScheduleRepository(SyncBaseRepository):

    def __init__(self) -> None:
        super().__init__(ClockedSchedule)
