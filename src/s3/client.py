import boto3

from src.settings import settings


s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_access_key=settings.AWS_SECRET_ACCESS_KEY_ID,
    region_name=settings.AWS_REGION_NAME
)
