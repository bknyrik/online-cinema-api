from datetime import datetime

from sqlalchemy import delete
from sqlalchemy.orm.session import Session
from sqlalchemy_celery_beat.models import PeriodicTask, ClockedSchedule


class CeleryBeatService:

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
