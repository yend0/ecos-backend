from dataclasses import dataclass
import uuid
from ecos_backend.common.interfaces import model
from ecos_backend.common.enums import RewardType


@dataclass
class AccrualHistoryModel(model.AbstractModel):
    id: uuid.UUID
    reward: RewardType
    points: int
    user_id: uuid.UUID

    def __post_init__(self) -> None:
        if not isinstance(self.reward, RewardType):
            raise ValueError("Invalid reward type.")
