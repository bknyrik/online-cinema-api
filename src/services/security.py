from typing import Literal
from datetime import timedelta, datetime, timezone

from fastapi import status, HTTPException
from jose import jwt, exceptions
from passlib.context import CryptContext


class PasswordSecurityService:

    def __init__(self, schemes: list[str]) -> None:
        self.crypt_context = CryptContext(
            schemes=schemes.copy(),
            deprecated="auto"
        )

    def hash_password(self, raw_password: str) -> str:
        return self.crypt_context.hash(raw_password)

    def verify_password(
        self,
        raw_password: str,
        hashed_password: str
    ) -> bool:
        return self.crypt_context.verify(raw_password, hashed_password)


class JWTAuthService:

    def __init__(
        self,
        secret_key: str,
        access_token_lifetime: timedelta,
        refresh_token_lifetime: timedelta,
        algorithm: str,
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_lifetime = access_token_lifetime
        self.refresh_token_lifetime = refresh_token_lifetime

    def encode_token(
        self,
        user_id: int,
        token_type: Literal["access", "refresh"]
    ) -> str:
        token_lifetime = (
            self.access_token_lifetime if token_type == "access"
            else self.refresh_token_lifetime
        )
        return jwt.encode(
            claims={
                "sub": str(user_id),
                "exp": datetime.now(timezone.utc) + token_lifetime
            },
            key=self.secret_key,
            algorithm=self.algorithm
        )

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token=token,
                key=self.secret_key,
                algorithms=(self.algorithm,)
            )
        except exceptions.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is expired"
            )
        except exceptions.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid"
            )
