from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import BaseModel, EmailStr

from ecos_backend.common import config


class EmailSchema(BaseModel):
    email: list[EmailStr]


class Email:
    def __init__(self, user: dict, url: str, email: list[EmailStr]) -> None:
        self.name = user["name"]
        self.sender: str = "Ecos <ecos@ecos.com>"
        self.email: list[str] = email
        self.url: EmailStr = url

    async def sendMail(self, subject, template) -> None:
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

        message = MessageSchema(
            subject=subject,
            recipients=self.email,
            subtype="plain",
        )

        fm = FastMail(conf)
        await fm.send_message(message)

    async def sendVerificationCode(self) -> None:
        await self.sendMail("Your verification code (Valid for 10min)", "verification")
