import uuid

from dataclasses import dataclass

from ecos_backend.common.interfaces import model


@dataclass
class WasteModel(model.AbstractModel):
    name: str
    description: str
    reception_point_id: uuid.UUID
    id: int = None
    image_url: str = None

    def __post_init__(self) -> None:
        if len(self.name) < 1:
            raise ValueError("Waste name cannot be empty.")
        if not isinstance(self.reception_point_id, uuid.UUID):
            raise ValueError("Invalid reception_point_id.")

    def update_image_url(self, image_url: str) -> None:
        self.image_url = image_url
