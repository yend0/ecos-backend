import typing
import uuid

from fastapi import APIRouter, status

from ecos_backend.api.v1.schemas.accrual_history import AccrualHistoryResponseSchema
from ecos_backend.api.v1 import annotations
from ecos_backend.models.accrual_history import AccrualHistoryDTO


router = APIRouter()


@router.get(
    "",
    summary="Get accrual histories",
    response_description="Accrual histories retrieved successfully",
    response_model=list[AccrualHistoryResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_accrual_histories(
    user_info: annotations.verify_token,
    accrual_history_service: annotations.accrual_history_service,
) -> typing.Any:
    accrual_histories: list[
        AccrualHistoryDTO
    ] = await accrual_history_service.get_accrual_histories()
    return [
        AccrualHistoryResponseSchema(**await accr.to_dict())
        for accr in accrual_histories
    ]


@router.get(
    "/user",
    summary="Get accrual histories for user",
    response_description="Accrual history retrieved successfully",
    response_model=list[AccrualHistoryResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_user_accrual_histories(
    user_info: annotations.verify_token,
    accrual_history_service: annotations.accrual_history_service,
) -> typing.Any:
    sub: str = user_info["sub"]
    accrual_histories: list[
        AccrualHistoryDTO
    ] = await accrual_history_service.get_user_accrual_histories(
        user_id=uuid.UUID(sub),
    )
    return [
        AccrualHistoryResponseSchema(**await accr.to_dict())
        for accr in accrual_histories
    ]


@router.get(
    "/{accrual_history_id}",
    summary="Get accrual history by id",
    response_description="Accrual history retrieved successfully",
    response_model=AccrualHistoryResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_accrual_history(
    user_info: annotations.verify_token,
    accrual_history: annotations.accrual_history_by_id,
) -> typing.Any:
    return accrual_history
