import uuid

from dataclasses import dataclass, field

from ecos_backend.common.interfaces import model


@dataclass
class WasteModel(model.AbstractModel):
    name: str
    description: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    image_url: str | None = None

    def __post_init__(self) -> None:
        if len(self.name) < 1:
            raise ValueError("Waste name cannot be empty.")
        if not isinstance(self.id, uuid.UUID):
            raise ValueError("Invalid id.")

    def update_image_url(self, image_url: str) -> None:
        self.image_url = image_url
