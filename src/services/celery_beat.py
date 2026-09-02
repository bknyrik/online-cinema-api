import json
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.orm.session import Session
from sqlalchemy_celery_beat.models import PeriodicTask, ClockedSchedule

from src.database.config import SyncSessionLocal
from src.repositories.celery_beat import (
    PeriodicTaskRepository,
    ClockedScheduleRepository
)


class CeleryBeatService:

    @staticmethod
    def create_periodic_task_to_delete_activation_token(
        user_id: int,
        token_expire_time: datetime
    ) -> None:
        with SyncSessionLocal() as session:
            cs = ClockedScheduleRepository().create(
                db=session,
                data={"clocked_schedule": token_expire_time}
            )
            PeriodicTaskRepository().create(
                db=session,
                data={
                    "name": f"Delete activation token by user {user_id}",
                    "task": "src.celery_beat.tasks.delete_expired_activation_token",
                    "args": json.dumps((user_id, cs.id)),
                    "one_off": True,
                    "schedule_model": cs
                }
            )

            session.commit()


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
    def delete_periodic_task_by_schedule_id(
        db: Session,
        schedule_id: int,
    ) -> None:
        db.execute(
            delete(PeriodicTask)
            .where(PeriodicTask.schedule_id == schedule_id)
        )
