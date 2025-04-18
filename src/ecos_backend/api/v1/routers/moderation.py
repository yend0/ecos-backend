import typing

from fastapi import APIRouter, status

from ecos_backend.api.v1 import annotations
from ecos_backend.api.v1.schemas.moderation import ModerationResponseSchema
from ecos_backend.db.models.moderation import Moderation

router = APIRouter()


@router.get(
    "",
    summary="Get moderations",
    response_description="Moderations retrieved successfully",
    response_model=list[ModerationResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_moderations(
    user_info: annotations.verify_token,
    moderation_service: annotations.moderation_service,
) -> typing.Any:
    moderations: list[Moderation] = await moderation_service.get_moderations()
    return moderations
