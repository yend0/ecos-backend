import datetime
import uuid

from dataclasses import dataclass

from ecos_backend.common.interfaces import model


@dataclass
class UserModel(model.AbstractModel):
    id: uuid.UUID
    email: str
    full_name: str = None
    birth_date: datetime.date = None
    image_url: str = None
    verification_code: str = None
