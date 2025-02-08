import datetime
import uuid

from dataclasses import dataclass

from ecos_backend.common.interfaces import model


import hashlib
import random
from dataclasses import field


@dataclass
class UserModel(model.AbstractModel):
    id: uuid.UUID
    email: str
    full_name: str = None
    birth_date: datetime.date = None
    image_url: str = None
    verification_code: str = field(default=None)
    verification_code_created_at: datetime.datetime = field(default=None)

    def __post_init__(self) -> None:
        if "@" not in self.email:
            raise ValueError("Invalid email address")

    def generate_verification_code(self) -> str:
        now: datetime.datetime = datetime.datetime.now()
        if (
            self.verification_code_created_at
            and (now - self.verification_code_created_at).seconds < 300
        ):
            raise ValueError("Verification code was recently sent. Try again later.")

        token: bytes = random.randbytes(10)
        hashed_code: hashlib._Hash = hashlib.sha256()
        hashed_code.update(token)

        self.verification_code = hashed_code.hexdigest()
        self.verification_code_created_at = now

        return token.hex()

    def verify_email(self) -> None:
        self.verification_code = None
        self.verification_code_created_at = None

    def update_profile_image(self, image_url: str) -> None:
        self.image_url = image_url
