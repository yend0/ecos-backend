from ecos_backend.common.config import keycloak_config
from keycloak import KeycloakAdmin, KeycloakOpenID, KeycloakOpenIDConnection


class KeycloakAdminAdapter:
    """Adapter for interacting with KeycloakAdmin."""

    def __init__(self) -> None:
        self._connection = KeycloakOpenIDConnection(
            server_url=keycloak_config.KEYCLOAK_SERVER_URL,
            username=keycloak_config.KEYCLOAK_ADMIN_NAME,
            password=keycloak_config.KEYCLOAK_ADMIN_PASSWORD,
            user_realm_name=keycloak_config.KEYCLOAK_ADMIN_REALM,
        )
        self._admin = KeycloakAdmin(connection=self._connection)
        self._admin.change_current_realm(keycloak_config.KEYCLOAK_REALM)

    @property
    def admin(self) -> KeycloakAdmin:
        """Provides access to the KeycloakAdmin instance."""
        return self._admin

    def __call__(self) -> KeycloakAdmin:
        """Allows the class instance to be used as a dependency."""
        return self._admin


class KeycloakClientAdapter:
    """Adapter for interacting with KeycloakOpenID."""

    def __init__(self) -> None:
        self._openid = KeycloakOpenID(
            server_url=keycloak_config.KEYCLOAK_SERVER_URL,
            realm_name=keycloak_config.KEYCLOAK_REALM,
            client_id=keycloak_config.KEYCLOAK_CLIENT_ID,
        )

    @property
    def openid(self) -> KeycloakOpenID:
        """Provides access to the KeycloakOpenID instance."""
        return self._openid

    def __call__(self) -> KeycloakOpenID:
        """Allows the class instance to be used as a dependency."""
        return self._openid
