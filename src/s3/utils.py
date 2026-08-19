from fastapi import UploadFile

from src.s3.client import s3_client
from src.settings import settings


async def upload_avatar(user_id: int, file: UploadFile) -> str:
    contents = await file.read()
    file_name = f"user_{user_id}.jpg"
    file_path = f"Avatars/{file_name}"

    s3_client.upload_fileobj(
        Fileobj=contents,
        Bucket=settings.AWS_BUCKET_NAME,
        Key=file_path
    )

    return f"https://s3://{settings.AWS_BUCKET_NAME}/Avatars/{file_name}"
