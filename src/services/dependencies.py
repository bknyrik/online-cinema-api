from datetime import timedelta

from src.settings import settings
from src.services.security import PasswordSecurityService, JWTAuthService


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
