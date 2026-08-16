import re

import email_validator


def validate_email(email: str) -> str:
    try:
        return email_validator.validate_email(email).normalized
    except email_validator.EmailNotValidError as error:
        raise ValueError(str(error))


def validate_password(password: str) -> str:
    if not re.search(r"{8, 16}", password):
        raise ValueError(
            "Password length must be min 8, max 16"
        )

    elif not re.search(r"\d{3,}", password):
        raise ValueError(
            "Password must contain at least 3 digits"
        )

    elif not re.search(r"\w{6,}", password):
        raise ValueError(
            "Password must contain at least 6 characters"
        )

    elif not re.search(r"[#!-_@?.]+", password):
        raise ValueError(
            "Password must contain at "
            "least one special character: #!-_@?"
        )

    return password
