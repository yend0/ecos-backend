import typing
import uuid

from fastapi import APIRouter, Depends, Path, status

from starlette.requests import ClientDisconnect

from streaming_form_data.validators import ValidationError

from ecos_backend.common import enums, validation
from ecos_backend.common import exception as custom_exceptions

from ecos_backend.db.models.reception_point import ReceptionPoint

from ecos_backend.api.v1 import annotations
from ecos_backend.api.v1.schemas.base import BaseInforamtionResponse
from ecos_backend.api.v1.schemas.reception_point import (
    PaginationParams,
    ReceptionPointFilterParams,
    ReceptionPointListResponse,
    ReceptionPointRequestCreateSchema,
    ReceptionPointResponseSchema,
)

router = APIRouter()


@router.post(
    "",
    summary="Create reception point",
    response_description="Reception point created successfully",
    response_model=BaseInforamtionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_reception_point(
    user_info: annotations.verify_token,
    reception_point_service: annotations.reception_point_service,
    data: annotations.data_request,
) -> typing.Any:
    try:
        sub = user_info["sub"]

        data_dict, uploaded_files = data

        data_schema = ReceptionPointRequestCreateSchema(**data_dict)
        model = ReceptionPoint(
            user_id=uuid.UUID(sub),
            **data_schema.model_dump(exclude={"work_schedules"}),
        )

        if not uploaded_files:
            raise custom_exceptions.ValidationException(
                detail="At least one image is required."
            )

        await reception_point_service.add_reception_point(
            reception_point=model,
            work_schedule=data_schema.work_schedules,
            uploaded_files=uploaded_files,
        )

        return BaseInforamtionResponse(
            message="Reception point created successfully",
            status=enums.Status.SUCCESS,
        )
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
    summary="Get reception points",
    response_description="Reception points retrieved successfully",
    response_model=ReceptionPointListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_reception_points(
    filter: typing.Annotated[ReceptionPointFilterParams, Depends()],
    pagination: typing.Annotated[PaginationParams, Depends()],
    reception_point_service: annotations.reception_point_service,
) -> typing.Any:
    reception_points: list[
        ReceptionPoint
    ] = await reception_point_service.get_reception_points(
        filters=filter.model_dump(exclude_none=True),
        page=pagination.page,
        per_page=pagination.per_page,
    )

    return ReceptionPointListResponse(
        items=reception_points,
        total=len(reception_points),
        page=pagination.page,
        per_page=pagination.per_page,
        total_pages=(
            (len(reception_points) + pagination.per_page - 1) // pagination.per_page
        ),
    )


@router.get(
    "/{reception_point_id}",
    summary="Get reception point by id",
    response_description="Reception point retrieved successfully",
    response_model=ReceptionPointResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_reception_point(
    reception_point: annotations.reception_point_by_id,
) -> typing.Any:
    return reception_point


@router.delete(
    "/{reception_point_id}",
    summary="Delete reception point",
    response_description="Reception point deleted successfully",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_reception_points(
    user_info: annotations.verify_token,
    reception_point_id: typing.Annotated[uuid.UUID, Path],
    reception_point_service: annotations.reception_point_service,
) -> None:
    await reception_point_service.delete_reception_point(id=reception_point_id)


@router.post(
    "/{reception_point_id}/wastes/{waste_id}",
    summary="Add waste to reception",
    response_description="Waste added to reception point successfully",
    response_model=BaseInforamtionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_waste_in_reception_point(
    user_info: annotations.verify_token,
    reception_point_id: typing.Annotated[uuid.UUID, Path],
    waste_id: typing.Annotated[uuid.UUID, Path],
    reception_point_service: annotations.reception_point_service,
) -> typing.Any:
    try:
        await reception_point_service.add_waste_in_reception_point(
            waste_id=waste_id, reception_point_id=reception_point_id
        )
        return BaseInforamtionResponse(
            message="Waste added to reception point successfully",
            status=enums.Status.SUCCESS,
        )
    except Exception as e:
        raise custom_exceptions.ValidationException(detail=f"Duplicate ID: {e}")


@router.delete(
    "/{reception_point_id}/wastes/{waste_id}",
    summary="Delete waste from reception point",
    response_description="Waste deleted from reception point successfully",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_waste_from_reception_point(
    user_info: annotations.verify_token,
    reception_point_id: typing.Annotated[uuid.UUID, Path],
    waste_id: typing.Annotated[uuid.UUID, Path],
    reception_point_service: annotations.reception_point_service,
) -> None:
    await reception_point_service.delete_waste_from_reception_point(
        reception_point_id=reception_point_id, waste_id=waste_id
    )


@router.patch(
    "/{reception_point_id}/status",
    summary="Update reception point status",
    response_description="Reception point status updated successfully",
    response_model=BaseInforamtionResponse,
    status_code=status.HTTP_200_OK,
)
async def update_reception_point_status(
    user_info: annotations.verify_token,
    data: annotations.moderation_create_schema,
    reception_point_id: typing.Annotated[uuid.UUID, Path],
    reception_point_service: annotations.reception_point_service,
) -> typing.Any:
    reception_point: (
        ReceptionPoint | None
    ) = await reception_point_service.get_reception_point_by_id(reception_point_id)

    if reception_point is None:
        raise custom_exceptions.NotFoundException(
            detail=f"Reception point with {reception_point_id} id not found."
        )

    await reception_point_service.update_status(
        reception_point=reception_point,
        comment=data.comment,
        status=data.status,
        user_id=reception_point.user_id,
    )

    return BaseInforamtionResponse(
        message="Reception point status updated successfully",
        status=enums.Status.SUCCESS,
    )
