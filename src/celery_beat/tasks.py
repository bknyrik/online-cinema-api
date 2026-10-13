from celery import shared_task
from sqlalchemy_celery_beat.models import PeriodicTask

from src.settings import settings
from src.database.models.accounts import ActivationTokenModel
from src.database.config import SyncSessionLocal
from src.repositories.accounts import TokenRepository
from src.repositories.celery_beat import (
    PeriodicTaskRepository,
    ClockedScheduleRepository
)
from src.database.models.rating import CommentLikeModel
from src.repositories.rating import CommentLikeRepository
from src.dependencies.services import get_sync_email_sender_service


@shared_task
def delete_expired_activation_token(user_id: int, schedule_id: int) -> None:
    token_repository = TokenRepository(ActivationTokenModel)
    ptr = PeriodicTaskRepository()
    csr = ClockedScheduleRepository()

    with SyncSessionLocal() as session:
        token_repository.delete_by_user_id(
            db=session,
            user_id=user_id
        )

        ptr.delete_by_schedule_id(
            db=session,
            schedule_id=schedule_id
        )

        csr.delete_by_id(
            db=session,
            id_=schedule_id
        )

        session.commit()


@shared_task
def notify_user_got_movie_comment_likes(
    email: str,
    comment_id: int,
    schedule_id: int
) -> None:
    email_sender = get_sync_email_sender_service()
    like_repository = CommentLikeRepository()
    periodic_task_repository = PeriodicTaskRepository()
    clocked_schedule_repository = ClockedScheduleRepository()

    with SyncSessionLocal() as session:
        count_likes = like_repository.count(
            db=session,
            expressions=[
                CommentLikeModel.comment_id == comment_id,
                CommentLikeModel.has_read == False
            ]
        )

        comment_likes_link = (
            f"{settings.COMMENT_LIKES_LINK}"
            f"?filter_by_comment_id={comment_id}&filter_by_has_read=false"
        )

        email_sender.send_user_got_comment_likes_email(
            receiver_email=email,
            count_likes=count_likes,
            comment_likes_link=comment_likes_link
        )

        periodic_task_repository.delete_by(
            db=session,
            expressions=[PeriodicTask.schedule_id == schedule_id]
        )
        clocked_schedule_repository.delete_by_id(session, schedule_id)
