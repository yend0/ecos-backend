import typing

from fastapi import APIRouter, status

from ecos_backend.api.v1 import annotations
from ecos_backend.api.v1.schemas import moderation as moderation_schemas
from ecos_backend.models.moderation import ModerationDTO

router = APIRouter()


@router.get(
    "",
    summary="Get moderations",
    response_description="Moderations retrieved successfully",
    response_model=list[moderation_schemas.ModerationResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_moderations(
    user_info: annotations.verify_token,
    moderation_service: annotations.moderation_service,
) -> typing.Any:
    moderations: list[ModerationDTO] = await moderation_service.get_moderations()
    return [
        moderation_schemas.ModerationResponseSchema(**await m.to_dict())
        for m in moderations
    ]


@router.get(
    "/{moderation_id}",
    summary="Get moderation by id",
    response_description="Moderation retrieved successfully",
    response_model=moderation_schemas.ModerationResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_moderation(
    user_info: annotations.verify_token,
    moderation: annotations.moderation_by_id,
) -> typing.Any:
    return moderation
