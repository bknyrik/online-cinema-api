from datetime import datetime

from sqlalchemy import delete
from sqlalchemy_celery_beat.models import PeriodicTask, ClockedSchedule

from src.database.config import SyncSessionLocal


class CeleryBeatService:

    @staticmethod
    def create_clocked_schedule(clocked_time: datetime) -> ClockedSchedule:
        with SyncSessionLocal() as session:
            cs = ClockedSchedule(
                clocked_time=clocked_time
            )
            session.add(cs)
            session.flush()

        return cs

    @staticmethod
    def create_periodic_task(**kwargs) -> PeriodicTask:
        with SyncSessionLocal() as session:
            pt = PeriodicTask(**kwargs)

            session.add(pt)
            session.flush()

        return pt

    @staticmethod
    def delete_clocked_schedule(id_: int) -> None:
        with SyncSessionLocal() as session:
            session.execute(
                delete(ClockedSchedule)
                .where(ClockedSchedule.id == id_)
            )


    @staticmethod
    def delete_periodic_task(id_: int) -> None:
        with SyncSessionLocal() as session:
            session.execute(
                delete(PeriodicTask)
                .where(PeriodicTask.id == id_)
            )
