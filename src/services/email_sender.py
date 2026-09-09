from email.message import EmailMessage
from pathlib import Path
from string import Template

import aiosmtplib


class EmailSenderService:

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    async def send_email(
        self,
        sender: str,
        receiver: str,
        subject: str,
        body: str
    ) -> None:
        async with aiosmtplib.SMTP(
            hostname=self.host,
            port=self.port
        ) as smtp_server:
            await smtp_server.ehlo()

            message = EmailMessage()
            message["from"] = sender
            message["to"] = receiver
            message["subject"] = subject

            message.set_content(body, "html")
            await smtp_server.send_message(message)

    @staticmethod
    def parse_html_template(template_path: Path, mapping: dict) -> str:
        return Template(template_path.read_text()).substitute(mapping)

    async def send_activation_email(
        self,
        receiver_email: str,
        activation_link: str,
        activation_token: str
    ) -> None:
        template_path = Path("src/templates/emails/account_activation.html")
        body = self.parse_html_template(
            template_path=template_path,
            mapping={"link": activation_link, "token": activation_token}
        )
        await self.send_email(
            sender="online.cinema.org",
            receiver=receiver_email,
            subject="Account activation",
            body=body
        )

    async def send_reset_password_email(
        self,
        receiver_email: str,
        reset_password_link: str,
        reset_password_token: str
    ) -> None:
        template_path = Path("src/templates/emails/reset_password.html")
        body = self.parse_html_template(
            template_path=template_path,
            mapping={
                "link": reset_password_link,
                "token": reset_password_token
            }
        )
        await self.send_email(
            sender="online.cinema.orm",
            receiver=receiver_email,
            subject="Reset password",
            body=body
        )
