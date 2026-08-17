from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status
from jose import jwt, exceptions

from src.settings import settings


ALGORITHM = "HS256"
ACCESS_TOKEN_LIFETIME_MINUTES = 30


def create_access_token(email: str) -> str:
    exp = (
        datetime.now(timezone.utc) +
        timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES)
    )
    return jwt.encode(
        claims={"sub": email, "exp": exp},
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
