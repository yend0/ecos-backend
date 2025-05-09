import typing
import uuid

from fastapi import APIRouter, Path, status

from starlette.requests import ClientDisconnect

from streaming_form_data.validators import ValidationError

from ecos_backend.common import validation
from ecos_backend.common import exception as custom_exceptions

from ecos_backend.api.v1 import annotations
from ecos_backend.api.v1.schemas.waste import (
    WasteRequestCreateSchema,
    WasteResponseSchema,
)
from ecos_backend.db.models.waste import Waste

router = APIRouter()


@router.post(
    "",
    summary="Create waste",
    response_description="Waste created successfully",
    response_model=WasteResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_waste(
    user_info: annotations.verify_token,
    waste_service: annotations.waste_service,
    data_request: annotations.data_request,
) -> typing.Any:
    try:
        data, uploaded_files = data_request

        waste_schema_request = WasteRequestCreateSchema(**data)

        waste: Waste = await waste_service.add_waste(
            waste=Waste(**waste_schema_request.model_dump()),
            file=uploaded_files[0][1],
            file_extension=uploaded_files[0][2],
        )

        return waste
    except ClientDisconnect:
        pass
    except validation.MaxBodySizeException as e:
        MAX_REQUEST_BODY_SIZE = 1024 * 1024 * 10 + 1024
        raise custom_exceptions.PayloadTooLargeException(
            detail=f"Maximum request body size limit ({MAX_REQUEST_BODY_SIZE} bytes) exceeded ({e.body_len} bytes read)."
        )
    except ValidationError as e:
        raise custom_exceptions.ValidationException(detail=f"{str(e)}")
    except validation.InvalidFileTypeException as e:
        raise custom_exceptions.ValidationException(detail=f"{str(e)}")


@router.get(
    "",
    summary="Get wastes",
    response_description="Wastes retrieved successfully",
    response_model=list[WasteResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_wastes(
    waste_service: annotations.waste_service,
    search_filter: annotations.search_filter = None,
) -> typing.Any:
    waste_list: list[Waste] = await waste_service.get_wastes(filters=search_filter)
    return waste_list


@router.get(
    "/{waste_id}",
    summary="Get waste by id",
    response_description="Waste retrieved successfully",
    response_model=WasteResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_waste(
    waste: annotations.waste_by_id,
) -> typing.Any:
    return waste


@router.delete(
    "/{waste_id}",
    summary="Delete waste",
    response_description="Waste deleted successfully",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_waste(
    user_info: annotations.verify_token,
    waste_service: annotations.waste_service,
    waste_id: typing.Annotated[uuid.UUID, Path],
) -> None:
    await waste_service.delete_waste(waste_id)
