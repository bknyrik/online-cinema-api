from email.message import EmailMessage

import aiosmtplib

from src.settings import settings


async def send_email(sender: str, receiver: str, html_body: str) -> None:
    async with aiosmtplib.SMTP(
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT
    ) as smtp_server:
        await smtp_server.ehlo()

        message = EmailMessage()
        message["from"] = sender
        message["to"] = receiver

        message.set_content(html_body, "html")
        await smtp_server.send_message(message)
