import httpx
from urllib.parse import (
    urlencode,
    urlparse,
    urlunparse,
    urljoin
)


def build_auth_url(
    *, auth_uri, oauth_key, state_token, authorized_scopes, redirect_uri
):
    query_params = {
        "response_type": "code",
        "client_id": oauth_key,
        "state": state_token,
        "scope": authorized_scopes.join(",") if authorized_scopes else None,
        "redirect_uri": redirect_uri,
    }
    return urlunparse(urlparse(auth_uri)._replace(query=urlencode(query_params)))


def get_oauth_token_data_from_code(exernal_storage_service, code):
    query_params = {
        "redirect_uri": exernal_storage_service.auth_callback_url,
        "client_id": exernal_storage_service.oauth2_client_config.client_id,
        "client_secret": exernal_storage_service.oauth2_client_config.client_secret,
        "grant_type": "authorization_code",
        "response_type": "code",
        "code": code,
    }
    url = urljoin(exernal_storage_service.api_base_url, "oauth2/token/")

    with httpx.Client() as client:
        resp = client.post(url, data=query_params)

    resp.raise_for_status()
    return resp.json()
