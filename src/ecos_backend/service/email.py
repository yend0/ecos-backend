from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jinja2 import Template
from pydantic import EmailStr, HttpUrl

from ecos_backend.common import config


class EmailService:
    def __init__(self, url: HttpUrl, email: list[EmailStr]) -> None:
        self._sender: str = "Ecos <ecos@ecos.com>"
        self._email: list[EmailStr] = email
        self._url: HttpUrl = url

    async def send_mail(self, subject, template) -> None:
        conf = ConnectionConfig(
            MAIL_USERNAME=config.smtp_config.EMAIL_USERNAME,
            MAIL_PASSWORD=config.smtp_config.EMAIL_PASSWORD,
            MAIL_FROM=config.smtp_config.EMAIL_FROM,
            MAIL_PORT=config.smtp_config.EMAIL_PORT,
            MAIL_SERVER=config.smtp_config.EMAIL_HOST,
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )

        template: Template = config.env_jinja2.get_template(f"{template}.html")

        html: str = template.render(url=self._url, subject=subject)

        message = MessageSchema(
            subject=subject, recipients=self._email, body=html, subtype="html"
        )

        fm = FastMail(conf)
        await fm.send_message(message)

    async def send_verification_code(self) -> None:
        await self.send_mail("Your verification code", "verification")
