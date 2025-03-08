import uuid

from dataclasses import dataclass, field

from ecos_backend.common.interfaces import model
from ecos_backend.common.enums import RewardType


@dataclass
class AccrualHistoryDTO(model.AbstractModel):
    points: int
    user_id: uuid.UUID
    reward: RewardType
    id: uuid.UUID = field(default_factory=uuid.uuid4)
