from datetime import datetime

from fastapi import HTTPException, status
from jose import jwt, exceptions

from src.settings import settings


ALGORITHM = "HS256"


def create_access_token(email: str, expires_at: datetime) -> str:
    return jwt.encode(
        claims={"sub": email, "exp": expires_at},
        key=settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token=token,
            key=settings.JWT_SECRET_KEY,
            algorithms=(ALGORITHM,)
        )
    except exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is expired",
        )
    except exceptions.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid"
        )
