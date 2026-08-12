from passlib.context import CryptContext


crypt_context = CryptContext(schemes=("bcrypt",), deprecated="auto")


def hash_password(raw_password: str) -> str:
    return crypt_context.hash(raw_password)


def verify_password(password_hash: str, raw_password: str) -> bool:
    return crypt_context.verify(raw_password, password_hash)
