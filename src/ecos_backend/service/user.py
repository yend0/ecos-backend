import dataclasses
import hashlib
import random
import uuid

from sqlalchemy.orm import selectinload

from keycloak import KeycloakAdmin, KeycloakPostError, KeycloakPutError

from ecos_backend.common import config
from ecos_backend.common.unit_of_work import AbstractUnitOfWork
from ecos_backend.common.exception import (
    ConflictException,
    InternalServerException,
    NotFoundException,
    BadRequestException,
)
from ecos_backend.service.email import EmailService
from ecos_backend.db.models.user import User
from ecos_backend.db.models.user_image import UserImage
from ecos_backend.db.s3_storage import Boto3DAO


@dataclasses.dataclass(kw_only=True, frozen=True, slots=True)
class UserService:
    uow: AbstractUnitOfWork
    admin: KeycloakAdmin
    s3_storage: Boto3DAO

    VERIFY_EMAIL_PATH = "/api/v1/users/verify-email/"

    async def register_user(
        self,
        email: str,
        password: str,
    ) -> User:
        """Register new user in Keycloak and database."""
        async with self.uow:
            try:
                # Create user in Keycloak
                user: User = await self._create_user_in_keycloak(email, password)

                # Generate verification code and URL
                verification_code, token = self._generate_verification_code()
                user.verification_code = verification_code

                # Save user to database
                await self._register_user_in_database(user)

                # Send verification email
                verification_url: str = (
                    f"http://{config.uvicorn_config.HOST}"
                    f"{self.VERIFY_EMAIL_PATH}{token}"
                )
                await EmailService(
                    url=verification_url, email=[user.email]
                ).send_verification_code()

                return user
            except Exception as ex:
                await self.uow.rollback()
                raise ex

    async def get_account_information(
        self, user_id: uuid.UUID, *, with_image: bool = True
    ) -> User | None:
        """Get user account information with optional image."""
        async with self.uow:
            options: list = []
            if with_image:
                options.append(selectinload(User.user_images))

            options.append(selectinload(User.accural_histories))

            user: User | None = await self.uow.user.get_by_id(
                id=user_id, options=options
            )
            return user

    async def verify_email(self, token: str) -> bool:
        """Verify user email using verification token."""
        async with self.uow:
            verification_code: str = self._compute_verification_code_from_token(token)
            user: User = await self.uow.user.get_by_verification_code(verification_code)

            if not user:
                raise NotFoundException(detail="Invalid verification token")
            if user.email_verified:
                raise ConflictException(detail="Email already verified")

            try:
                await self._update_user_in_keycloak(user.id)
                user.email_verified = True
                await self.uow.user.add(user)
                await self.uow.commit()
                return True
            except Exception as ex:
                await self.uow.rollback()
                raise InternalServerException(detail="Failed to verify email") from ex

    async def resend_verification_email(
        self,
        email: str,
    ) -> None:
        """Resend verification email to user."""
        async with self.uow:
            user: User | None = await self.uow.user.get_by_email(email)
            if not user:
                raise NotFoundException(detail="User not found")
            if user.email_verified:
                raise ConflictException(detail="Email already verified")

            verification_code, token = self._generate_verification_code()
            user.verification_code = verification_code

            verification_url: str = (
                f"http://{config.uvicorn_config.HOST}"
                f"{self.VERIFY_EMAIL_PATH}{token}"
            )

            await EmailService(
                url=verification_url, email=[user.email]
            ).send_verification_code()

            await self.uow.user.add(user)
            await self.uow.commit()

    async def update_account_information(
        self,
        user: User,
        *,
        file: bytes | None = None,
        file_extension: str | None = None,
    ) -> User:
        """Update user account information."""
        async with self.uow:
            # Handle image upload
            if file is not None:
                try:
                    filename: str = f"{uuid.uuid4()}.{file_extension}"

                    # Upload to S3
                    self.s3_storage.upload_object(
                        bucket_name=config.s3_config.USER_BUCKET,
                        prefix=f"{user.id}/images/",
                        source_file_name=filename,
                        content=file,
                    )

                    # Create UserImage record
                    user_image = UserImage(
                        filename=filename,
                        user_id=user.id,
                    )

                    await self.uow.user_image.add(user_image)
                except Exception as ex:
                    raise InternalServerException(
                        detail="Failed to upload image"
                    ) from ex

            await self.uow.user.add(user)
            await self.uow.commit()
            return user

    async def _create_user_in_keycloak(self, email: str, password: str) -> User:
        """Create user in Keycloak."""
        try:
            user_id = await self.admin.a_create_user(
                {
                    "username": email,
                    "email": email,
                    "enabled": True,
                    "emailVerified": False,
                    "credentials": [
                        {"type": "password", "value": password, "temporary": False}
                    ],
                }
            )

            new_user = await self.admin.a_get_user(user_id)
            return User(
                id=uuid.UUID(new_user["id"]),
                email=new_user["email"],
            )
        except KeycloakPostError as ex:
            if "exists" in str(ex):
                raise ConflictException(detail="User with this email already exists")
            raise InternalServerException(
                detail="Failed to create user in identity provider"
            ) from ex

    async def _update_user_in_keycloak(self, user_id: uuid.UUID) -> None:
        """Update user in Keycloak."""
        try:
            await self.admin.a_update_user(
                str(user_id),
                {"emailVerified": True},
            )
        except KeycloakPutError as ex:
            raise InternalServerException(
                detail="Failed to update user in identity provider"
            ) from ex

    async def _register_user_in_database(self, user: User) -> User:
        """Register user in database."""
        try:
            await self.uow.user.add(user)
            await self.uow.commit()
            return user
        except Exception as ex:
            # Cleanup Keycloak if DB fails
            try:
                await self.admin.a_delete_user(str(user.id))
            except Exception:
                pass
            raise InternalServerException(
                detail="Failed to register user in database"
            ) from ex

    def _compute_verification_code_from_token(self, token: str) -> str:
        """Compute verification code from token."""
        try:
            hashed_code: hashlib.HASH = hashlib.sha256(bytes.fromhex(token))
            return hashed_code.hexdigest()
        except ValueError as ex:
            raise BadRequestException(detail="Invalid token format") from ex

    def _generate_verification_code(self) -> tuple[str, str]:
        """Generate verification code and token pair."""
        token: bytes = random.randbytes(32)
        hashed_code: hashlib.HASH = hashlib.sha256(token)
        return hashed_code.hexdigest(), token.hex()
