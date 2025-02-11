import json
import typing
import uuid

from fastapi import APIRouter, Path, Request, status

from starlette.requests import ClientDisconnect

from urllib.parse import unquote


from ecos_backend.common import exception as custom_exceptions

from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget
from streaming_form_data.validators import ValidationError


from ecos_backend.common import validation
from ecos_backend.common import constatnts as const

from ecos_backend.api.v1 import annotations
from ecos_backend.api.v1.schemas.base import BaseInforamtionResponse
from ecos_backend.api.v1.schemas.reception_point import ReceptionPointResponseSchema
from ecos_backend.domain.reception_point import ReceptionPointModel

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
    request: Request,
) -> typing.Any:
    sub = user_info["sub"]

    try:
        data, uploaded_files = await parse_request(request)

        await reception_point_service.add_reception_point(
            reception_point=ReceptionPointModel(
                name=data["name"],
                address=data["address"],
                user_id=uuid.UUID(sub),
            ),
            uploaded_files=uploaded_files,
        )

        return BaseInforamtionResponse(
            status="success",
            message="Reception point added.",
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
) -> typing.Any:
    reception_points: list[
        ReceptionPointModel
    ] = await reception_point_service.get_reception_points()
    return [
        ReceptionPointResponseSchema(**await rp.to_dict(exclude={"images_url"}))
        for rp in reception_points
    ]


@router.delete(
    "{reception_point_id}",
    summary="Get reception points",
    response_description="Reception points retrieved successfully",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_reception_points(
    user_info: annotations.verify_token,
    reception_point_id: typing.Annotated[uuid.UUID, Path],
    reception_point_service: annotations.reception_point_service,
) -> None:
    await reception_point_service.delete_reception_point(id=reception_point_id)


async def parse_request(
    request: Request,
) -> tuple[dict | None, list[tuple[str, bytes, str]] | None]:
    body_validator = validation.MaxBodySizeValidator(const.MAX_REQUEST_BODY_SIZE)
    data = ValueTarget()
    parser = StreamingFormDataParser(headers=request.headers)

    file_targets: dict = {}

    filenames_header: str | None = request.headers.get("filenames")
    filenames: list[str] = (
        [unquote(f.strip()) for f in filenames_header.split(",")]
        if filenames_header
        else []
    )

    for filename in filenames:
        file_target = validation.BytesTarget(
            validator=validation.MaxSizeValidator(const.MAX_FILE_SIZE)
        )
        parser.register(filename, file_target)
        file_targets[filename] = file_target

    parser.register("data", data)

    async for chunk in request.stream():
        body_validator(chunk)
        parser.data_received(chunk)

    try:
        raw_data: str | None = data.value.decode() if data.value else None
        if raw_data and raw_data.startswith('"') and raw_data.endswith('"'):
            raw_data = raw_data[1:-1].replace('\\"', '"')
        data_dict: dict | None = json.loads(raw_data) if raw_data else None
    except json.JSONDecodeError as e:
        raise custom_exceptions.ValidationException(
            detail=f"Invalid JSON format: {str(e)}"
        )

    uploaded_files: list = []
    for filename, file_target in file_targets.items():
        if file_target.content:
            try:
                file_extension: str = validation.FileTypeValidator.validate(
                    file_target.content
                ).lstrip(".")
                uploaded_files.append((filename, file_target.content, file_extension))
            except validation.InvalidFileTypeException as e:
                raise custom_exceptions.ValidationException(detail=str(e))

    return data_dict, uploaded_files
