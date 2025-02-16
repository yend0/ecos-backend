import uuid

from dataclasses import dataclass, field

from ecos_backend.common.interfaces import model


@dataclass
class WasteDTO(model.AbstractModel):
    name: str
    description: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    image_url: str | None = None

    def update_image_url(self, image_url: str) -> None:
        self.image_url = image_url
