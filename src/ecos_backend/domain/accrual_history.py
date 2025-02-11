from dataclasses import dataclass
import uuid
import datetime
from ecos_backend.common.interfaces import model
from ecos_backend.common.enums import Reward


@dataclass
class AccrualHistoryModel(model.AbstractModel):
    id: uuid.UUID
    reward: Reward
    points: int
    created_at: datetime.datetime
    user_id: uuid.UUID

    def __post_init__(self) -> None:
        if not isinstance(self.reward, Reward):
            raise ValueError("Invalid reward type.")
