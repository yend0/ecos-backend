from enum import Enum

from fastapi.routing import APIRouter

from ecos_backend.common import config
from ecos_backend.api.v1.controllers import homepage
from ecos_backend.api.v1.controllers import user
from ecos_backend.api.v1.controllers import auth


class Tags(Enum):
    auth: str = "Auth"
    user: str = "User"


root = APIRouter()
root.include_router(homepage.router)

api_router_v1 = APIRouter(prefix=f"{config.URLPathsConfig.API_PREFIX}/v1")

api_router_v1.include_router(auth.router, prefix="/auth", tags=[Tags.auth])
api_router_v1.include_router(user.router, prefix="/user", tags=[Tags.user])

root.include_router(api_router_v1)
