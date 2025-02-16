import typing

from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

from ecos_backend.common import config

router = APIRouter()


@router.get(
    path=config.URLPathsConfig.HOMEPAGE,
    response_class=RedirectResponse,
    name=config.URLNamesConfig.HOMEPAGE,
    status_code=status.HTTP_303_SEE_OTHER,
    include_in_schema=False,
)
async def homepage() -> typing.Any:
    return RedirectResponse(
        status_code=status.HTTP_303_SEE_OTHER,
        url=config.URLPathsConfig.DOCS_URL,
    )
