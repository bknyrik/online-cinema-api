import json
from datetime import datetime

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
                data={"clocked_time": token_expire_time}
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
