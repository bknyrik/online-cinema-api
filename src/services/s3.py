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

    def upload_image(self, user_id: int, image: UploadFile) -> tuple[str, str]:
        _, ext = os.path.splitext(image.filename)
        key = f"Avatars/user_{user_id}{ext}"

        self.client.upload_fileobj(
            Fileobj=image.file,
            Bucket=self.bucket_name,
            Key=key
        )

        return (
            f"https://{self.bucket_name}.s3.{self.region_name}"
            f".amazonaws.com/{key}",
            key
        )


    def delete_image(self, key: str) -> None:
        self.client.delete_object(
            Key=key,
            Bucket=self.bucket_name
        )
