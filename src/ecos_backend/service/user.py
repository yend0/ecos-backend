import hashlib
import uuid
import typing

from fastapi import Request

from ecos_backend.common.exception import (
    ConflictException,
    InternalServerException,
    NotFoundException,
)
from ecos_backend.common.unit_of_work import AbstractUnitOfWork
from ecos_backend.common.config import s3_config
from ecos_backend.service.email import EmailService
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
        request: Request,
    ) -> UserModel:
        async with self._uow:
            try:
                user: UserModel = await self._create_user_in_keycloak(
                    username, password
                )

                token: str = user.generate_verification_code()

                url: str = f"{request.url.scheme}://{request.client.host}:{request.url.port}/api/v1/user/verify-email/{token}"

                await EmailService(url=url, email=[user.email]).sendVerificationCode()

                await self._uow.user.add(user)
                await self._uow.commit()
                return user

            except Exception as e:
                await self._admin.a_delete_user(user.id)
                raise e

    async def get_account_information(
        self, id: uuid.UUID
    ) -> typing.Optional[UserModel]:
        async with self._uow:
            return await self._uow.user.get_by_id(id=id)

    async def verify_email(self, token: str) -> bool:
        async with self._uow:
            verification_code: str = self._compute_verification_code_from_token(token)
            user: typing.Optional[
                UserModel
            ] = await self._uow.user.get_by_verification_code(
                verification_code=verification_code
            )

            if not user:
                raise NotFoundException(detail="User already verified or not found")

            user.verify_email()

            await self._update_user_in_keycloak(user)
            await self._uow.user.add(user)
            await self._uow.commit()
            return True

    async def resend_verification_email(
        self, user: UserModel, request: Request
    ) -> None:
        async with self._uow:
            try:
                token: str = user.generate_verification_code()
                url: str = f"{request.url.scheme}://{request.client.host}:{request.url.port}/api/v1/user/verify-email/{token.hex()}"

                await EmailService(url=url, email=[user.email]).sendVerificationCode()

                await self._uow.user.add(user)
                await self._uow.commit()
            except ValueError as e:
                raise ConflictException(detail=str(e))

    async def update_account_information(
        self,
        user: UserModel,
        file: bytes = None,
        file_extention: str = None,
    ) -> UserModel:
        async with self._uow:
            if file_extention is not None:
                try:
                    url = self._s3_storage.upload_object(
                        bucket_name=s3_config.USER_BUCKET,
                        prefix=f"{str(user.id)}/image/{file_extention}",
                        source_file_name=str(f"{uuid.uuid4()}.{file_extention}"),
                        content=file,
                    )
                    clean_url = url.split("?")[0]
                    user.update_profile_image(clean_url)
                except Exception as e:
                    raise e

            await self._uow.user.add(user)
            await self._uow.commit()
            return user

    async def _create_user_in_keycloak(self, username: str, password: str) -> UserModel:
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
            return UserModel(
                id=uuid.UUID(new_user["id"]),
                email=new_user["email"],
            )

        except KeycloakPostError as e:
            raise ConflictException(
                detail="User exists with the same email address or the email address is incorrect"
            ) from e

    async def _update_user_in_keycloak(self, user: UserModel) -> None:
        try:
            await self._admin.a_update_user(
                user.id,
                {"emailVerified": True},
            )
        except KeycloakPutError as e:
            raise InternalServerException(detail="Failed to verify email") from e

    def _compute_verification_code_from_token(self, token) -> str:
        hashedCode: hashlib._Hash = hashlib.sha256()
        hashedCode.update(bytes.fromhex(token))
        verification_code: str = hashedCode.hexdigest()
        return verification_code
