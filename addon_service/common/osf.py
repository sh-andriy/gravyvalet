import enum
from http import HTTPStatus
from urllib.parse import urlsplit

from asgiref.sync import async_to_sync
from django import http as django_http
from django.conf import settings

from addon_service.common.aiohttp_session import get_singleton_client_session


__all__ = (
    "OSFPermission",
    "get_osf_user_uri",
    "has_osf_permission_on_resource",
)


class OSFPermission(enum.StrEnum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


@async_to_sync
async def get_osf_user_uri(request: django_http.HttpRequest) -> str | None:
    _auth_headers = _get_osf_auth_headers(request)
    if not _auth_headers:
        return None
    _client = await get_singleton_client_session()
    async with _client.get(_osfapi_me_url(), headers=_auth_headers) as _response:
        if HTTPStatus(_response.status).is_client_error:
            return None
        _response_content = await _response.json()
        return _iri_from_osfapi_resource(_response_content["data"])


@async_to_sync
async def has_osf_permission_on_resource(
    request: django_http.HttpRequest,
    resource_uri: str,
    required_permission: OSFPermission,
) -> bool:
    _auth_headers = _get_osf_auth_headers(request)
    if not _auth_headers:
        return False
    _client = await get_singleton_client_session()
    async with _client.get(
        _osfapi_guid_url(resource_uri),
        params={
            "resolve": "False",  # do not redirect to the referent
            "embed": "referent",  # instead, include the referent in the response
        },
        headers=_auth_headers,
    ) as _response:
        if not HTTPStatus(_response.status).is_success:
            return False
        _response_content = await _response.json()
        try:
            _resource_json = _response_content["data"]["embeds"]["referent"]["data"]
            _permissions = _resource_json["attributes"]["current_user_permissions"]
        except KeyError:
            return False
        return required_permission in _permissions


###
# module-private helpers

_HeaderList = list[tuple[str, str]]


def _extract_osfid(osf_resource_uri: str):
    if not any(
        osf_resource_uri.startswith(_uri_prefix)
        for _uri_prefix in settings.ALLOWED_RESOURCE_URI_PREFIXES
    ):
        raise ValueError(
            f'expected resource from a known osf {settings.ALLOWED_RESOURCE_URI_PREFIXES} (got "{osf_resource_uri}")'
        )
    try:
        (_osfid,) = urlsplit(osf_resource_uri).path.strip("/").split("/")
    except ValueError:
        raise ValueError(f'expected short osf uri (got "{osf_resource_uri}")')
    return _osfid


def _osfapi_guid_url(osf_resource_uri: str):
    _osfid = _extract_osfid(osf_resource_uri)
    return f"{settings.OSF_API_BASE_URL}/v2/guids/{_osfid}/"


def _osfapi_me_url():
    return f"{settings.OSF_API_BASE_URL}/v2/users/me/"


def _get_osf_auth_headers(request: django_http.HttpRequest) -> _HeaderList:
    return [
        *_osf_cookie_auth_headers(request),
        *_osf_token_auth_headers(request),
    ]


def _osf_cookie_auth_headers(request: django_http.HttpRequest) -> _HeaderList:
    _osf_user_cookie = request.COOKIES.get(settings.USER_REFERENCE_COOKIE)
    return (
        [("Cookie", f"{settings.USER_REFERENCE_COOKIE}={_osf_user_cookie}")]
        if _osf_user_cookie
        else []
    )


def _osf_token_auth_headers(request: django_http.HttpRequest) -> _HeaderList:
    _auth_header = request.headers.get("Authorization")
    return (
        [("Authorization", _auth_header)]
        if _auth_header and _auth_header.startswith("Bearer ")
        else []
    )


def _iri_from_osfapi_resource(osfapi_resource: dict) -> str:
    # osf api object representation has an unambiguous identifier at `links.iri`
    return osfapi_resource["links"]["iri"]
