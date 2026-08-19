from fastapi import UploadFile

from src.s3.client import s3_client
from src.settings import settings


def upload_avatar(user_id: int, avatar: UploadFile) -> str:
    file_name = f"user_{user_id}.jpg"

    s3_client.upload_fileobj(
        Fileobj=avatar.file,
        Bucket=settings.AWS_BUCKET_NAME,
        Key=f"Avatars/{file_name}"
    )

    return (
        f"https://{settings.AWS_BUCKET_NAME}.s3."
        f"{settings.AWS_REGION_NAME}.amazonaws.com/Avatars/{file_name}"
    )
