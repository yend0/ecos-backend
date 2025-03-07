import typing
import uuid

from fastapi import APIRouter, Path, status

from starlette.requests import ClientDisconnect


from ecos_backend.common import exception as custom_exceptions

from streaming_form_data.validators import ValidationError


from ecos_backend.common import validation
from ecos_backend.common import constatnts as const

from ecos_backend.api.v1 import annotations
from ecos_backend.api.v1.schemas.reception_point import (
    ReceptionPointRequestCreateSchema,
    ReceptionPointResponseSchema,
)
from ecos_backend.models.drop_off_point_waste import DropOffPointWasteDTO
from ecos_backend.models.reception_point import ReceptionPointDTO
from ecos_backend.models.work_schedule import WorkScheduleDTO

router = APIRouter()


@router.post(
    "",
    summary="Create reception point",
    response_description="Reception point created successfully",
    response_model=ReceptionPointResponseSchema,
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
        model = ReceptionPointDTO(
            user_id=uuid.UUID(sub),
            work_schedules=[
                WorkScheduleDTO(**value.model_dump())
                for value in data_schema.work_schedules
            ],
            **data_schema.model_dump(exclude={"work_schedules"}),
        )

        if not uploaded_files:
            raise custom_exceptions.ValidationException(
                detail="At least one image is required."
            )

        reception_point: ReceptionPointDTO = (
            await reception_point_service.add_reception_point(
                reception_point=model,
                uploaded_files=uploaded_files,
            )
        )

        return ReceptionPointResponseSchema(
            **await reception_point.to_dict(exclude={"images_url"})
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
    summary="Get reception points",
    response_description="Reception points retrieved successfully",
    response_model=list[ReceptionPointResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_reception_points(
    reception_point_service: annotations.reception_point_service,
    search_filter: annotations.search_filter = None,
) -> typing.Any:
    reception_points: list[
        ReceptionPointDTO
    ] = await reception_point_service.get_reception_points(filters=search_filter)
    return [
        ReceptionPointResponseSchema(**await rp.to_dict(exclude={"images_url"}))
        for rp in reception_points
    ]


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
    status_code=status.HTTP_201_CREATED,
)
async def add_waste_to_reception_point(
    user_info: annotations.verify_token,
    reception_point: annotations.reception_point_by_id,
    waste: annotations.waste_by_id,
    reception_point_service: annotations.reception_point_service,
) -> None:
    try:
        drop_off_point_waste = DropOffPointWasteDTO(
            reception_point_id=reception_point.id, waste_id=waste.id
        )

        await reception_point_service.add_drop_off_point_waste(drop_off_point_waste)
    except Exception:
        raise custom_exceptions.ValidationException(detail="Duplicate ID")


@router.delete(
    "/{reception_point_id}/wastes/{waste_id}",
    summary="Delete waste from reception point",
    response_description="Waste deleted from reception point successfully",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_waste_from_reception_point(
    user_info: annotations.verify_token,
    reception_point: annotations.reception_point_by_id,
    waste: annotations.waste_by_id,
    reception_point_service: annotations.reception_point_service,
) -> None:
    drop_off_point_waste = DropOffPointWasteDTO(
        reception_point_id=reception_point.id, waste_id=waste.id
    )
    await reception_point_service.delete_drop_off_point_waste(drop_off_point_waste)


@router.patch(
    "/{reception_point_id}/status",
    summary="Update reception point status",
    response_description="Reception point status updated successfully",
    response_model=ReceptionPointResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_reception_point_status(
    user_info: annotations.verify_token,
    data: annotations.moderation_create_schema,
    reception_point_id: typing.Annotated[uuid.UUID, Path],
    reception_point_service: annotations.reception_point_service,
) -> typing.Any:
    reception_point: (
        ReceptionPointDTO | None
    ) = await reception_point_service.get_reception_point_by_id(reception_point_id)

    if reception_point is None:
        raise custom_exceptions.NotFoundException(
            detail=f"Reception point with {reception_point_id} id not found."
        )

    result: ReceptionPointDTO = (
        await reception_point_service.update_status_reception_point(
            reception_point=reception_point,
            comment=data.comment,
            status=data.status,
            user_id=reception_point.user_id,
        )
    )

    return ReceptionPointResponseSchema(**await result.to_dict(exclude={"images_url"}))
