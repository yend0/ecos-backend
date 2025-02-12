import typing
import uuid

from fastapi import APIRouter, Path, status

from starlette.requests import ClientDisconnect

from ecos_backend.common import exception as custom_exceptions

from streaming_form_data.validators import ValidationError


from ecos_backend.common import validation
from ecos_backend.common import constatnts as const

from ecos_backend.api.v1 import annotations
from ecos_backend.api.v1.schemas.base import BaseInforamtionResponse

router = APIRouter()


@router.post(
    "",
    summary="Create waste",
    response_description="Waste created successfully",
    response_model=BaseInforamtionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_waste(
    user_info: annotations.verify_token,
    dict_file_extension: annotations.dict_file_extension,
) -> typing.Any:
    try:
        data, file, file_extension = dict_file_extension

        return BaseInforamtionResponse(
            status="success",
            message="Waste added.",
        )
    except ClientDisconnect:
        pass
    except validation.MaxBodySizeException as e:
        raise custom_exceptions.PayloadTooLargeException(
            detail=f"Maximum request body size limit ({const.MAX_REQUEST_BODY_SIZE} bytes) exceeded ({e.body_len} bytes read)."
        )
    except ValidationError as e:
        raise custom_exceptions.ValidationException(detail=f"{str(e)}")
    except validation.InvalidFileTypeException as e:
        raise custom_exceptions.ValidationException(detail=f"{str(e)}")


@router.get(
    "",
    summary="Get wastes",
    response_description="Wastes retrieved successfully",
    status_code=status.HTTP_200_OK,
)
async def get_wastes() -> typing.Any:
    pass


@router.delete(
    "/{waste_id}",
    summary="Delete waste",
    response_description="Waste deleted successfully",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_waste(
    user_info: annotations.verify_token,
    waste_id: typing.Annotated[uuid.UUID, Path],
) -> None:
    pass
