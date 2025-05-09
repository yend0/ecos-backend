import typing
import uuid

from fastapi import APIRouter, Path, status

from ecos_backend.api.v1 import annotations
from ecos_backend.api.v1.schemas.waste_translation import WasteTranslationResponseSchema
from ecos_backend.db.models.waste_translation import WasteTranslation

router = APIRouter()


@router.get(
    "",
    summary="Get waste translations",
    response_description="Waste translations retrieved successfully",
    response_model=list[WasteTranslationResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_waste_translations(
    waste_translation_service: annotations.waste_translation_service,
) -> typing.Any:
    return await waste_translation_service.get_waste_translations()


@router.post(
    "",
    summary="Create waste translation",
    response_description="Waste translation created successfully",
    response_model=WasteTranslationResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_waste_translation(
    user_info: annotations.verify_token,
    waste_translation_service: annotations.waste_translation_service,
    waste_translation_request: annotations.waste_translation_create_schema,
) -> typing.Any:
    return await waste_translation_service.add_waste_translation(
        waste_translation=WasteTranslation(**waste_translation_request.model_dump()),
    )


@router.patch(
    "/{waste_translation_id}",
    summary="Update waste translation",
    response_description="Waste translation updated successfully",
    response_model=WasteTranslationResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
async def update_waste_translation(
    user_info: annotations.verify_token,
    waste_translation: annotations.waste_translation_by_id,
    waste_translation_service: annotations.waste_translation_service,
    waste_translation_request: annotations.waste_translation_update_schema,
) -> typing.Any:
    for field, value in waste_translation_request.model_dump(
        exclude_unset=True
    ).items():
        setattr(waste_translation, field, value)

    return await waste_translation_service.add_waste_translation(
        waste_translation=waste_translation,
    )


@router.delete(
    "/{waste_translation_id}",
    summary="Delete waste translation",
    response_description="Waste translation deleted successfully",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_waste_translation(
    user_info: annotations.verify_token,
    waste_translation_id: typing.Annotated[uuid.UUID, Path],
    waste_translation_service: annotations.waste_translation_service,
) -> None:
    await waste_translation_service.delete_waste_translation(waste_translation_id)
