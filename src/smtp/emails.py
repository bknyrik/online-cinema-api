from pathlib import Path

from src.smtp.utils import send_email, parse_html_content


async def send_activation_email(email: str, link: str, token: str) -> None:
    html_body = parse_html_content(
        path=Path("src/smtp/templates/account_activation.html"),
        link=link,
        token=token
    )
    await send_email(
        sender="online.cinema@mail.com",
        receiver=email,
        subject="Account activation",
        html_body=html_body
    )
