import json
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_celery_beat.models import PeriodicTask

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
            try:
                name = f"Delete activation token by user {user_id}"
                task = "src.celery_beat.tasks.delete_expired_activation_token"
                pt_repository = PeriodicTaskRepository()
                cs_repository = ClockedScheduleRepository()

                cs = cs_repository.create(
                    db=session,
                    data={"clocked_time": token_expire_time}
                )

                periodic_task = pt_repository.get_by(
                    db=session,
                    expressions=[PeriodicTask.name == name]
                )

                if periodic_task:
                    old_schedule_id = periodic_task.schedule_id
                    pt_repository.update_by_id(
                        db=session,
                        id_=periodic_task.id,
                        data={
                            "schedule_id": cs.id,
                            "args": json.dumps((user_id, cs.id)),
                            "schedule_model": cs
                        }
                    )
                    cs_repository.delete_by_id(
                        db=session,
                        id_=old_schedule_id
                    )

                else:
                    pt_repository.create(
                        db=session,
                        data={
                            "name": name,
                            "task": task,
                            "args": json.dumps((user_id, cs.id)),
                            "one_off": True,
                            "schedule_model": cs
                        }
                    )
                session.commit()
            except SQLAlchemyError:
                session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred while creating periodic task"
                )
