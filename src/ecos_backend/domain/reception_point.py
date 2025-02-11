from dataclasses import dataclass, field
import uuid
from datetime import datetime
from ecos_backend.common.interfaces import model


@dataclass
class ReceptionPointModel(model.AbstractModel):
    name: str
    address: str
    user_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    urls: list[str] = field(default_factory=list)
    images_url: str = None
    updated_at: datetime = None

    def __post_init__(self) -> None:
        if len(self.name) < 1 or len(self.address) < 1:
            raise ValueError("Reception Point name and address cannot be empty.")

    def set_images_url(self, image_url: str) -> None:
        self.images_url = image_url

    def set_image_urls(self, urls: list[str]) -> None:
        self.urls = urls
