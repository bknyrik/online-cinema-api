from datetime import timedelta
from typing import Annotated

from fastapi import Depends

from src.settings import settings
from src.services import (
    celery_beat,
    security,
    email_sender,
    s3,
    accounts,
    cinema,
    notifications
)


ACCESS_TOKEN_LIFETIME = timedelta(minutes=30)
REFRESH_TOKEN_LIFETIME = timedelta(days=1)


def get_password_security_service() -> security.PasswordSecurityService:
    return security.PasswordSecurityService(schemes=["bcrypt"])


def get_jwt_auth_service() -> security.JWTAuthService:
    return security.JWTAuthService(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        access_token_lifetime=ACCESS_TOKEN_LIFETIME,
        refresh_token_lifetime=REFRESH_TOKEN_LIFETIME
    )


def get_email_sender_service() -> email_sender.EmailSenderService:
    return email_sender.EmailSenderService(
        host=settings.SMTP_HOST,
        port=settings.SMTP_PORT
    )


def get_s3_service() -> s3.S3Service:
    return s3.S3Service(
        access_key_id=settings.AWS_ACCESS_KEY_ID,
        secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        bucket_name=settings.AWS_BUCKET_NAME,
        region_name=settings.AWS_REGION_NAME
    )


PasswordSecurityServiceDep = Annotated[
    security.PasswordSecurityService,
    Depends(get_password_security_service)
]
EmailSenderServiceDep = Annotated[
    email_sender.EmailSenderService,
    Depends(get_email_sender_service)
]
JWTAuthServiceDep = Annotated[
    security.JWTAuthService,
    Depends(get_jwt_auth_service)
]
S3ServiceDep = Annotated[s3.S3Service, Depends(get_s3_service)]
CeleryBeatServiceDep = Annotated[celery_beat.CeleryBeatService, Depends()]
UserServiceDep = Annotated[accounts.UserService, Depends()]
UserProfileServiceDep = Annotated[accounts.UserProfileService, Depends()]
GenreServiceDep = Annotated[cinema.GenreService, Depends()]
StarServiceDep = Annotated[cinema.StarService, Depends()]
CertificationServiceDep = Annotated[cinema.CertificationService, Depends()]
DirectorServiceDep = Annotated[cinema.DirectorService, Depends()]
MovieServiceDep = Annotated[cinema.MovieService, Depends()]
NotificationServiceDep = Annotated[
    notifications.NotificationService,
    Depends()
]
