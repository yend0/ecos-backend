import uuid

from dataclasses import dataclass, field

from ecos_backend.common.interfaces import model
from ecos_backend.common.enums import RewardType


@dataclass
class AccrualHistoryModel(model.AbstractModel):
    reward: RewardType
    points: int
    user_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.reward, RewardType):
            raise ValueError("Invalid reward type.")
        if not isinstance(self.user_id, uuid.UUID):
            raise ValueError("Invalid user_id.")
        if not isinstance(self.id, uuid.UUID):
            raise ValueError("Invalid id.")
