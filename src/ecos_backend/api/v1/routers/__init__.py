from enum import Enum

from fastapi.routing import APIRouter

from ecos_backend.common import config

from ecos_backend.api.v1.routers import homepage
from ecos_backend.api.v1.routers import user
from ecos_backend.api.v1.routers import reception_point
from ecos_backend.api.v1.routers import waste
from ecos_backend.api.v1.routers import waste_translation
from ecos_backend.api.v1.routers import moderation


class Tags(Enum):
    user: str = "User"
    reception_point: str = "Reception point"
    waste: str = "Waste"
    waste_translation: str = "Waste translation"
    moderation: str = "Moderation"


root = APIRouter()
root.include_router(homepage.router)

api_router_v1 = APIRouter(prefix=f"{config.URLPathsConfig.API_PREFIX}/v1")

api_router_v1.include_router(user.router, prefix="/users", tags=[Tags.user])
api_router_v1.include_router(
    reception_point.router, prefix="/reception-points", tags=[Tags.reception_point]
)
api_router_v1.include_router(waste.router, prefix="/wastes", tags=[Tags.waste])
api_router_v1.include_router(
    waste_translation.router,
    prefix="/waste-translations",
    tags=[Tags.waste_translation],
)
api_router_v1.include_router(
    moderation.router, prefix="/moderations", tags=[Tags.moderation]
)

root.include_router(api_router_v1)
