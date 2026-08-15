import email_validator


def validate_email(email: str) -> str:
    try:
        return email_validator.validate_email(email).normalized
    except email_validator.EmailNotValidError as error:
        raise ValueError(str(error))
