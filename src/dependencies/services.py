from datetime import timedelta
from typing import Annotated

from fastapi import Depends

from src.settings import settings
from src.services.accounts import UserService, UserProfileService
from src.services.security import PasswordSecurityService, JWTAuthService
from src.services.email_sender import EmailSenderService
from src.services.s3 import S3Service


ACCESS_TOKEN_LIFETIME = timedelta(minutes=30)
REFRESH_TOKEN_LIFETIME = timedelta(days=1)


def get_password_secure_service() -> PasswordSecurityService:
    return PasswordSecurityService(schemes=["bcrypt"])


def get_jwt_auth_service() -> JWTAuthService:
    return JWTAuthService(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        access_token_lifetime=ACCESS_TOKEN_LIFETIME,
        refresh_token_lifetime=REFRESH_TOKEN_LIFETIME
    )


def get_email_sender_service() -> EmailSenderService:
    return EmailSenderService(
        host=settings.SMTP_HOST,
        port=settings.SMTP_PORT
    )


def get_s3_service() -> S3Service:
    return S3Service(
        access_key_id=settings.AWS_ACCESS_KEY_ID,
        secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        bucket_name=settings.AWS_BUCKET_NAME,
        region_name=settings.AWS_REGION_NAME
    )


PasswordSecurityService = Annotated[
    PasswordSecurityService,
    Depends(get_password_secure_service)
]
EmailSenderServiceDep = Annotated[
    EmailSenderService,
    Depends(get_email_sender_service)
]
JWTAuthServiceDep = Annotated[JWTAuthService, Depends(get_jwt_auth_service)]
S3ServiceDep = Annotated[S3Service, Depends(get_s3_service)]
UserServiceDep = Annotated[UserService, Depends()]
UserProfileServiceDep = Annotated[UserProfileService, Depends()]
