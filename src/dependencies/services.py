from datetime import timedelta

from src.settings import settings
from src.services.accounts import UserService
from src.services.profiles import UserProfileService
from src.services.security import PasswordSecurityService, JWTAuthService
from src.services.email_sender import EmailSenderService
from src.services.s3 import S3Service
from src.repositories.accounts import (
    UserRepository,
    TokenRepository,
    UserGroupRepository
)
from src.repositories.profiles import UserProfileRepository
from src.database.models import accounts


ACCESS_TOKEN_LIFETIME = timedelta(minutes=30)
REFRESH_TOKEN_LIFETIME = timedelta(days=1)


def get_password_secure_service() -> PasswordSecurityService:
    return PasswordSecurityService(schemes=["bcrypt"])


def get_jwt_auth_service() -> JWTAuthService:
    return JWTAuthService(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm="HS256",
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


def get_user_service() -> UserService:
    return UserService(
        user_repository=UserRepository(),
        user_group_repository=UserGroupRepository(),
        at_repository=TokenRepository(accounts.ActivationTokenModel),
        rt_repository=TokenRepository(accounts.RefreshTokenModel),
        prt_repository=TokenRepository(accounts.PasswordResetTokenModel)
    )


def get_profile_service() -> UserProfileService:
    return UserProfileService(
        profile_repository=UserProfileRepository()
    )
