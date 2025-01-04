from enum import Enum

from fastapi.routing import APIRouter

from ecos_backend.api.v1.controllers import user


class Tags(Enum):
    user: str = "User"


api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=[Tags.user])
