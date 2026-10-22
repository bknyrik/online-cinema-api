import os

import boto3
from fastapi import UploadFile, HTTPException, status


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

    @property
    def root_image_url(self) -> str:
        return (
            f"https://{self.bucket_name}.s3."
            f"{self.region_name}.amazonaws.com/"
        )

    def upload_image(
        self,
        identifier: int,
        image: UploadFile,
        key_prefix: str,
        image_prefix: str
    ) -> str:
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The provided file is not an image"
            )

        _, ext = os.path.splitext(image.filename)
        key = f"{key_prefix}/{image_prefix}_{identifier}{ext}"

        self.client.upload_fileobj(
            Fileobj=image.file,
            Bucket=self.bucket_name,
            Key=key
        )

        return f"{self.root_image_url}{key}"


    def delete_image(self, key: str) -> None:
        self.client.delete_object(
            Key=key,
            Bucket=self.bucket_name
        )
