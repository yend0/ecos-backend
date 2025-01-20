from ecos_backend.api.v1.exception import UnauthorizedExcetion

from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError, KeycloakPostError


class AuthService:
    def __init__(self, client: KeycloakOpenID) -> None:
        self._client: KeycloakOpenID = client

    async def auth(self, username: str, password: str) -> dict[str, str | int]:
        try:
            token = await self._client.a_token(username=username, password=password)
            return self._extract_token_data(token)
        except KeycloakAuthenticationError as e:
            raise UnauthorizedExcetion(detail="Invalid username or password") from e

    async def logout(self, token: str) -> None:
        try:
            await self._client.a_logout(refresh_token=token)
        except KeycloakAuthenticationError as e:
            raise UnauthorizedExcetion(
                detail="Could not logout because of invalid token"
            ) from e
        except KeycloakPostError as e:
            raise UnauthorizedExcetion(detail="Invalid refresh token") from e

    async def refresh_token(self, refresh_token: str) -> dict[str, str | int]:
        try:
            token = await self._client.a_refresh_token(refresh_token=refresh_token)
            return self._extract_token_data(token)
        except KeycloakAuthenticationError as e:
            raise UnauthorizedExcetion(detail="Could not refresh token") from e
        except KeycloakPostError as e:
            raise UnauthorizedExcetion(detail="Invalid refresh token") from e

    async def verify_token(self, token: str) -> str:
        try:
            user_info = await self._client.a_userinfo(token=token)
            if not user_info or "sub" not in user_info:
                raise UnauthorizedExcetion("Invalid token")
            return user_info["sub"]
        except KeycloakAuthenticationError as e:
            raise UnauthorizedExcetion(detail="Could not validate credentials") from e

    @staticmethod
    def _extract_token_data(token: dict) -> dict[str, str | int]:
        return {
            "access_token": token.get("access_token"),
            "refresh_token": token.get("refresh_token"),
            "token_type": token.get("token_type", "Bearer"),
            "expires_in": token.get("expires_in"),
            "refresh_expires_in": token.get("refresh_expires_in"),
        }
