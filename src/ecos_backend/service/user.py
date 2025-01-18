import uuid
import typing

from ecos_backend.api.v1.exception import ConflictException
from ecos_backend.common.unit_of_work import AbstractUnitOfWork
from ecos_backend.domain.user import UserModel

from keycloak import KeycloakAdmin, KeycloakPostError


class UserService:
    def __init__(self, uow: AbstractUnitOfWork, admin: KeycloakAdmin) -> None:
        self._uow: AbstractUnitOfWork = uow
        self._admin: KeycloakAdmin = admin

    async def register_user(self, username: str, password: str) -> UserModel:
        async with self._uow:
            try:
                user_id: str = await self._admin.a_create_user(
                    {
                        "username": username,
                        "email": username,
                        "enabled": True,
                        "credentials": [
                            {"type": "password", "value": password, "temporary": False}
                        ],
                    }
                )

            except KeycloakPostError as e:
                raise ConflictException(
                    detail="User exists with the same email address or the email address is incorrect"
                ) from e

            new_user = await self._admin.a_get_user(user_id=user_id)

            user = UserModel(id=uuid.UUID(new_user["id"]), email=new_user["email"])
            await self._uow.user.add(user)
            await self._uow.commit()
            return user

    async def get_account_information(
        self, id: uuid.UUID
    ) -> typing.Optional[UserModel]:
        async with self._uow:
            user: typing.Optional[UserModel] = await self._uow.user.get_by_id(id=id)
            return user
