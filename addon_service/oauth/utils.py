from datetime import timedelta
from http import HTTPStatus
from secrets import token_urlsafe
from urllib.parse import (
    urlencode,
    urljoin,
    urlparse,
    urlunparse,
)

from django.db import transaction
from django.utils import timezone

from addon_service.common.aiohttp_session import get_aiohttp_client_session


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


async def request_access_token(token_metadata, authorization_code=None):
    client = get_aiohttp_client_session()
    async with client.post(
        _build_token_exchange_url(
            token_metadata=token_metadata,
            authorization_code=authorization_code,
        )
    ) as token_response:
        if not HTTPStatus(token_response.status_code).is_success():
            raise RuntimeError  # TODO: something smarter here
        return await token_response.json()


def _build_token_exchange_url(token_metadata, authorization_code=None):
    oauth2_client_config = token_metadata.client_config
    params = {
        "grant_type": "authorization_code" if authorization_code else "refresh_token",
        "client_id": oauth2_client_config.client_id,
        "client_secret": oauth2_client_config.client_secret,
    }
    if authorization_code:
        params["code"] = authorization_code
        params["redirect_uri"] = oauth2_client_config.auth_callback_url
    else:
        params["refresh_token"] = token_metadata.refresh_token

    api_url = token_metadata.linked_accounts[0].api_base_url
    return urlunparse(
        urlparse(urljoin(api_url, "oauth/token"))._replace(query=urlencode(params))
    )


@transaction.atomic
def update_from_token_endpoint_response(token_metadata, response_json):
    token_metadata.update(
        state_token=None,
        refresh_token=response_json.get("refresh_token"),
        access_token_expiration=timezone.now()
        + timedelta(seconds=response_json["expires_in"]),
    )
    if "scopes" in response_json:
        token_metadata.update(authorized_scopes=response_json["scopes"])

    for account in token_metadata.linked_accounts:
        account.set_credentials({"access_token": response_json["access_token"]})
