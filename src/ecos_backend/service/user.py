import uuid
import typing

from ecos_backend.common.exception import (
    ConflictException,
    InternalServerException,
    NotFoundException,
)
from ecos_backend.common.unit_of_work import AbstractUnitOfWork
from ecos_backend.common.email import Email
from ecos_backend.domain.user import UserModel
from ecos_backend.db.s3_storage import Boto3DAO

from keycloak import KeycloakAdmin, KeycloakPostError, KeycloakPutError


class UserService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        admin: KeycloakAdmin,
        s3_storage: Boto3DAO,
    ) -> None:
        self._uow: AbstractUnitOfWork = uow
        self._admin: KeycloakAdmin = admin
        self._s3_storage: Boto3DAO = s3_storage

    async def register_user(
        self,
        username: str,
        password: str,
        verification_code: str,
        url: str,
    ) -> UserModel:
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

                new_user = await self._admin.a_get_user(user_id=user_id)

                user = UserModel(id=uuid.UUID(new_user["id"]), email=new_user["email"])

                setattr(user, "verification_code", verification_code)

                await Email(url=url, email=[user.email]).sendVerificationCode()

                await self._uow.user.add(user)
                await self._uow.commit()
                return user

            except KeycloakPostError as e:
                raise ConflictException(
                    detail="User exists with the same email address or the email address is incorrect"
                ) from e
            except Exception as e:
                await self._admin.a_delete_user(user_id=user_id)
                raise e

    async def get_account_information(
        self, id: uuid.UUID
    ) -> typing.Optional[UserModel]:
        async with self._uow:
            user: typing.Optional[UserModel] = await self._uow.user.get_by_id(id=id)
            return user

    async def verify_email(self, verification_code: str) -> bool:
        async with self._uow:
            user: typing.Optional[
                UserModel
            ] = await self._uow.user.get_by_verification_code(
                verification_code=verification_code
            )

            if not user:
                raise NotFoundException(detail="User not found")

            try:
                await self._admin.a_update_user(
                    user.id,
                    {
                        "emailVerified": True,
                    },
                )
            except KeycloakPutError as e:
                raise InternalServerException(detail="Failed to verify email") from e
            return True

    async def update_account_information(
        self,
        user: UserModel,
        file: bytes,
        file_extention: str,
    ) -> UserModel:
        async with self._uow:
            if file_extention is not None:
                try:
                    url = self._s3_storage.upload_object(
                        f"{str(user.id)}/image/{file_extention}",
                        str(f"{uuid.uuid4()}.{file_extention}"),
                        file,
                    )
                    clean_url = url.split("?")[0]
                    setattr(user, "image_url", clean_url)
                except Exception as e:
                    raise e

            await self._uow.user.add(user)
            await self._uow.commit()
            return user
