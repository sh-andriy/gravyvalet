from http import HTTPStatus
from secrets import token_urlsafe
from urllib.parse import (
    urlencode,
    urljoin,
    urlparse,
    urlunparse,
)

import httpx


def build_auth_url(
    *, auth_uri, client_id, state_token, authorized_scopes, redirect_uri
):
    query_params = {
        "response_type": "code",
        "client_id": client_id,
        "state": state_token,
        "redirect_uri": redirect_uri,
    }
    if authorized_scopes:
        query_params["scope"] = ",".join(authorized_scopes)

    return urlunparse(urlparse(auth_uri)._replace(query=urlencode(query_params)))


def generate_state_token(token_length=16):
    return token_urlsafe(token_length)


def perform_oauth_token_exchange(account, authorization_code=None, refresh_token=None):
    with httpx.Client as client:
        token_response = client.post(
            _build_token_exchange_url(
                account=account,
                authorization_code=authorization_code,
                refresh_token=refresh_token,
            )
        )
    if not HTTPStatus(token_response.status_code).is_success():
        raise RuntimeError  # TODO: something smarter here

    response_json = token_response.json()
    account.oauth2_token_metadata.update_from_token_endpoint_response(response_json)
    account.set_credentials(token_response_blob=response_json)


def _build_token_exchange_url(account, authorization_code=None, refresh_token=None):
    if bool(authorization_code) == bool(refresh_token):
        raise ValueError(
            "Must specify exactly one of authorization_code or refresh_token"
        )

    oauth2_client_config = account.external_service.oauth2_client_config
    params = {
        "grant_type": "authorization_code" if authorization_code else "refresh_token",
        "client_id": oauth2_client_config.client_id,
        "client_secret": oauth2_client_config.client_secret,
    }
    if authorization_code:
        params["code"] = authorization_code
        params["redirect_uri"] = oauth2_client_config.auth_callback_url
    else:
        params["refresh_token"] = refresh_token

    return urlunparse(
        urlparse(urljoin(account.api_base_url, "oauth/token"))._replace(
            query=urlencode(params)
        )
    )
