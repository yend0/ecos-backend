from ecos_backend.common.config import keycloak_config

from keycloak import KeycloakAdmin, KeycloakOpenIDConnection

keycloak_connection = KeycloakOpenIDConnection(
    server_url=keycloak_config.KEYCLOAK_SERVER_URL,
    username=keycloak_config.KEYCLOAK_ADMIN_NAME,
    password=keycloak_config.KEYCLOAK_ADMIN_PASSWORD,
    user_realm_name=keycloak_config.KEYCLOAK_ADMIN_REALM,
)

keycloak_admin = KeycloakAdmin(connection=keycloak_connection)
keycloak_admin.change_current_realm(keycloak_config.KEYCLOAK_REALM)


def get_keycloak_admin() -> KeycloakAdmin:
    return keycloak_admin
