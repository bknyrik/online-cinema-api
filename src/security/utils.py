import secrets


def generate_secure_token(length: int = 24) -> str:
    return secrets.token_urlsafe(length)
