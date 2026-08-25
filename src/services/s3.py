import os

import boto3
from fastapi import UploadFile


class S3Service:

    def __init__(
        self,
        access_key_id: str,
        secret_access_key: str,
        region_name: str,
        bucket_name: str
    ) -> None:
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.region_name = region_name
        self.bucket_name = bucket_name
        self.client = boto3.client(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region_name
        )

    def upload_image(self, user_id: int, image: UploadFile) -> str:
        _, ext = os.path.splitext(image.filename)
        file_name = f"user_{user_id}.{ext}"

        self.client.upload_fileobj(
            Fileobj=image.file,
            Bucket=self.bucket_name,
            Key=file_name
        )

        return (
            f"https://{self.bucket_name}.s3."
            f"{self.region_name}.amazonaws.com/{file_name}"
        )
