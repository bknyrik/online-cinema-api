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
