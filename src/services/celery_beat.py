import json
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.orm.session import Session
from sqlalchemy_celery_beat.models import PeriodicTask, ClockedSchedule

from src.database.config import SyncSessionLocal


class CeleryBeatService:

    @staticmethod
    def create_periodic_task_to_delete_activation_token(
        user_id: int,
        token_expire_time: datetime
    ) -> None:
        with SyncSessionLocal() as session:
            cs = CeleryBeatService.create_clocked_schedule(
                db=session,
                clocked_time=token_expire_time
            )
            CeleryBeatService.create_periodic_task(
                db=session,
                name=f"Delete activation token by user {user_id}",
                task="src.celery_beat.tasks.delete_expired_activation_token",
                args=json.dumps((user_id, cs.id)),
                one_off=True,
                schedule_model=cs
            )

            session.commit()

    @staticmethod
    def get_clocked_schedule_by_id(db: Session, id_: int) -> ClockedSchedule | None:
        return db.execute(
            select(ClockedSchedule)
            .where(ClockedSchedule.id == id_)
        ).scalar_one_or_none()

    @staticmethod
    def get_periodic_task_by_schedule_id(db: Session, schedule_id: int) -> PeriodicTask | None:
        return db.execute(
            select(PeriodicTask)
            .where(PeriodicTask.schedule_id == schedule_id)
        ).scalar_one_or_none()

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
    def delete_periodic_task_by_schedule_id(db: Session, id_: int) -> None:
        db.execute(
            delete(PeriodicTask)
            .where(PeriodicTask.id == id_)
        )
