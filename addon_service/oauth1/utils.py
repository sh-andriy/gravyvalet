from base64 import b64encode
from hashlib import sha1
from hmac import HMAC
from http import (
    HTTPMethod,
    HTTPStatus,
)
from secrets import token_urlsafe
from time import time
from urllib.parse import (
    parse_qs,
    quote_plus,
)

from aiohttp import ContentTypeError

from addon_service.common.aiohttp_session import get_singleton_client_session
from addon_toolkit.credentials import OAuth1Credentials
from addon_toolkit.iri_utils import iri_with_query


async def get_temporary_token(
    temporary_token_url: str,
    oauth_consumer_key: str,
    oauth_consumer_secret: str,
) -> tuple[OAuth1Credentials, dict]:
    """
    Obtaining unauthorised request token needed to construct Authorization url
    https://oauth.net/core/1.0a/#auth_step1
    """
    signed_headers = construct_signed_headers(
        temporary_token_url, oauth_consumer_key, oauth_consumer_secret
    )
    return await _get_token(temporary_token_url, signed_headers)


async def get_access_token(
    access_token_url: str,
    oauth_consumer_key: str,
    oauth_consumer_secret: str,
    oauth_token: str,
    oauth_token_secret: str,
    oauth_verifier: str,
) -> tuple[OAuth1Credentials, dict]:
    """
    Getting final access token needed to access protected resources from Service provider

    """
    signed_headers = construct_signed_headers(
        access_token_url,
        oauth_consumer_key,
        oauth_consumer_secret,
        oauth_token=oauth_token,
        oauth_verifier=oauth_verifier,
        oauth_token_secret=oauth_token_secret,
    )
    return await _get_token(access_token_url, signed_headers)


async def _get_token(
    request_token_url, signed_headers
) -> tuple[OAuth1Credentials, dict]:
    _client = await get_singleton_client_session()
    async with _client.post(
        request_token_url, headers=signed_headers
    ) as _token_response:
        if not HTTPStatus(_token_response.status).is_success:
            raise RuntimeError(await _token_response.text())
        try:
            return OAuth1Credentials.from_dict(await _token_response.json())
        except ContentTypeError:
            raw_result = parse_qs(await _token_response.text())
            result_dict = {key: value[0] for key, value in raw_result.items() if value}
            return OAuth1Credentials.from_dict(result_dict)


def _construct_params(params_to_encode: dict) -> str:
    return ",".join(
        f'{key}="{value}"' for key, value in sorted(params_to_encode.items())
    )


def construct_signed_headers(
    url: str,
    oauth_consumer_key: str,
    oauth_consumer_secret: str,
    http_method: HTTPMethod = HTTPMethod.POST,
    oauth_token: str | None = None,
    oauth_token_secret: str | None = None,
    oauth_verifier: str | None = None,
):
    oauth_params = construct_headers(oauth_consumer_key, oauth_token, oauth_verifier)
    signature = generate_signature(
        http_method, url, oauth_params, oauth_consumer_secret, oauth_token_secret
    )
    oauth_params |= {"oauth_signature": signature}
    return {"Authorization": f"OAuth {_construct_params(oauth_params)}"}


def generate_signature(
    http_method: HTTPMethod,
    url: str,
    headers: dict,
    oauth_consumer_secret: str,
    oauth_token_secret: str | None = None,
) -> str:
    params_str = "&".join(f"{key}={value}" for key, value in sorted(headers.items()))
    signature_base = f"{http_method}&{quote_plus(url)}&{quote_plus(params_str)}"
    key = f"{oauth_consumer_secret}&{oauth_token_secret or ''}"
    hmac = HMAC(key.encode(), signature_base.encode(), sha1).digest()
    return quote_plus(b64encode(hmac))


def construct_headers(
    oauth_consumer_key: str,
    oauth_token: str | None = None,
    oauth_verifier: str | None = None,
) -> dict[str, str]:
    initial_payload = {
        "oauth_consumer_key": oauth_consumer_key,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": f"{int(time())}",
        "oauth_nonce": generate_nonce(32),
        "oauth_version": "1.0",
        "oauth_token": oauth_token,
        "oauth_verifier": oauth_verifier,
    }

    return {key: value for key, value in initial_payload.items() if value}


def build_auth_url(
    *,
    auth_uri: str,
    temporary_oauth_token: str,
) -> str:
    """build a URL that will initiate authorization when visited by a user

    see https://www.rfc-editor.org/rfc/rfc6749.html#section-4.1.1
    """
    query_params = {
        "oauth_token": temporary_oauth_token,
    }
    return iri_with_query(auth_uri, query_params)


def generate_nonce(nonce_length: int = 16):
    return token_urlsafe(nonce_length)
