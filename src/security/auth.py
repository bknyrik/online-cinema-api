from datetime import datetime, timezone, timedelta

from jose import jwt

from src.settings import settings


ALGORITHM = "HS256"


def create_access_token(user_id: int) -> str:
    return jwt.encode(
        claims={
            "user_id": user_id,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=30),
        },
        key=settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM
    )
