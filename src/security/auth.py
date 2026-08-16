from datetime import datetime

from jose import jwt

from src.settings import settings


ALGORITHM = "HS256"


def create_access_token(email: str, expires_at: datetime) -> str:
    return jwt.encode(
        claims={"sub": email, "exp": expires_at},
        key=settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM
    )
