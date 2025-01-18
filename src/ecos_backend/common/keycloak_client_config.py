from ecos_backend.common.config import keycloak_config

from keycloak import KeycloakOpenID


keycloak_openid: KeycloakOpenID = KeycloakOpenID(
    server_url=keycloak_config.KEYCLOAK_SERVER_URL,
    realm_name=keycloak_config.KEYCLOAK_REALM,
    client_id=keycloak_config.KEYCLOAK_CLIENT_ID,
    client_secret_key=keycloak_config.KEYCLOAK_CLIENT_SECRET,
)


def get_keycloak_openid() -> KeycloakOpenID:
    return keycloak_openid
