from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import Session
from sqlalchemy_celery_beat.models import PeriodicTask, ClockedSchedule


class CeleryBeatService:

    @staticmethod
    def get_clocked_schedule_by_id(db: Session, id_: int) -> ClockedSchedule | None:
        return db.scalar(
            select(ClockedSchedule)
            .where(ClockedSchedule.id == id_)
        ).one_or_none()

    @staticmethod
    def get_periodic_task_by_schedule_id(db: Session, schedule_id: int) -> PeriodicTask | None:
        return db.scalar(
            select(PeriodicTask)
            .options(joinedload(PeriodicTask.schedule_model))
            .where(PeriodicTask.schedule_id == schedule_id)
        ).one_or_none()

    @staticmethod
    def create_clocked_schedule(
        db: Session,
        clocked_time: datetime
    ) -> ClockedSchedule:
        cs = ClockedSchedule(clocked_time=clocked_time)

        db.add(cs)
        db.flush()

        return cs

    @staticmethod
    def create_periodic_task(db: Session, **kwargs) -> PeriodicTask:
        pt = PeriodicTask(**kwargs)

        db.add(pt)
        db.flush()

        return pt

    @staticmethod
    def delete_clocked_schedule(db: Session, id_: int) -> None:
        db.execute(
            delete(ClockedSchedule)
            .where(ClockedSchedule.id == id_)
        )


    @staticmethod
    def delete_periodic_task(db: Session, id_: int) -> None:
        db.execute(
            delete(PeriodicTask)
            .where(PeriodicTask.id == id_)
        )
