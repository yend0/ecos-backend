import typing

from fastapi import APIRouter, status

from ecos_backend.api.v1.schemas.user import UserCreateSchema

router = APIRouter()


@router.post(
    "/",
    summary="Register user",
    response_description="User created successfully",
    status_code=status.HTTP_201_CREATED,
)
async def add_user(user: UserCreateSchema) -> typing.Any:
    pass
