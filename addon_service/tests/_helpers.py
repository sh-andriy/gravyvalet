import contextlib
import dataclasses
import secrets
from collections import defaultdict
from http import HTTPStatus
from unittest.mock import patch
from urllib.parse import (
    parse_qs,
    urljoin,
    urlparse,
)

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.urls import reverse
from rest_framework import exceptions as drf_exceptions
from rest_framework.test import APIRequestFactory
from rest_framework_json_api.utils import get_resource_type_from_model

from addon_service.common.aiohttp_session import get_aiohttp_client_session


class MockOSF:
    _configured_caller_uri: str | None = None
    _permissions: dict[str, dict[str, str | bool]]

    def __init__(self, permissions=None):
        """A lightweight, configurable  mock of OSF for testing remote permissions.

        Accepts a mapping of arbitrary resource_uris to user permissiosn and `public` status
        {
            'osf.io/abcde': {'osf.io/bcdef': 'write', 'osf.io/cdefg': 'admin', 'public': True},
            'osf.io/zyxwv': {'osf.io/yxwvut': 'read', 'public': False}
        }
        Intercepts 'get' requests and uses the request url and this mapping to generate a minimal
        response required for testing GravyValet's behavior.

        Users of the mock can either explicitly tell the Mock which user to assume a call is from,
        or they can include a cookie with the 'user_uri' in their GET request, and MockOSF will honor
        that user
        """
        self._permissions = defaultdict(dict)
        if permissions:
            self._permissions.update(permissions)

    @contextlib.contextmanager
    def mocking(self):
        with patch(
            "app.authentication.make_auth_request",
            side_effect=self._mock_user_check,
        ), patch(
            "addon_service.common.permissions.authenticate_resource",
            side_effect=self._mock_resource_check,
        ):
            yield self

    def configure_assumed_caller(self, caller_uri):
        self._configured_caller_uri = caller_uri

    def configure_user_role(self, user_uri, resource_uri, role):
        self._permissions[resource_uri][user_uri] = role

    def configure_resource_visibility(self, resource_uri, *, public=True):
        self._permissions[resource_uri]["public"] = public

    def _get_assumed_caller(self, cookies=None):
        if self._configured_caller_uri:
            return self._configured_caller_uri
        if cookies is not None:
            return cookies.get(settings.USER_REFERENCE_COOKIE)
        return None

    def _get_user_permissions(self, user_uri, resource_uri):
        # Use of defaultdict means this will always have some value
        role = self._permissions[resource_uri].get(user_uri)
        if role == "read":
            return ["read"]
        if role == "write":
            return ["read", "write"]
        if role == "admin":
            return ["read", "write", "admin"]
        if self._permissions[resource_uri].get("public", False):
            return ["read"]
        return []

    def _mock_user_check(self, *args, **kwargs):
        caller_uri = self._get_assumed_caller(cookies=kwargs.get("cookies"))
        return {"data": {"links": {"iri": caller_uri}}}

    def _mock_resource_check(self, request, uri, required_permission, *args, **kwargs):
        caller = self._get_assumed_caller(cookies=request.COOKIES)
        permissions = self._get_user_permissions(user_uri=caller, resource_uri=uri)
        if required_permission.lower() not in permissions:
            raise drf_exceptions.PermissionDenied
        return uri  # mimicking behavior from the check being mocked


class MockExternalService:
    ROUTES = tuple(
        ("token_endpoint", "oauth/token"),
    )

    def __init__(self, external_service, client):
        self.auth_url = external_service.auth_uri
        api_base_url = external_service.api_base_url
        self._static_access_token = None
        self._static_refresh_token = None
        self.local_routes = {
            urlparse(urljoin(api_base_url, subpath)).path: endpoint_name
            for endpoint_name, subpath in self.ROUTES
        }

    def set_internal_client(self, client):
        """Attach a DRF APIClient for making requests internally"""
        self._internal_client = client

    def configure_static_tokens(self, access=None, refresh=None):
        self._static_access_token = access
        self._static_refresh_token = refresh

    @contextlib.contextmanager
    def mocking(self):
        client_session = get_aiohttp_client_session()
        with patch.object(
            client_session,
            "get",
            side_effect=self._route_get,
        ), patch.object(
            client_session,
            "post",
            side_effect=self._route_post,
        ):
            yield self

    def _route_get(self, url, *args, **kwargs):
        if url.startswith(self.auth_url):
            state_token = parse_qs(urlparse(url).query)["state"]
            self._initiate_oauth_exchange(state_token=state_token)

        raise RuntimeError(f"Received unrecognized endpoint {url}")

    def _initiate_oauth_exchange(self, state_token):
        self._internal_client.get(
            reverse("oauth2-callback"), {"state": state_token, "code": "authgrant"}
        )
        return _MockResponse()

    def _route_post(self, url, *args, **kwargs):
        endpoint_name = self.local_routes.get(urlparse(url).path)
        match endpoint_name:
            case "token_endpoint":
                return _MockResponse(
                    status_code=HTTPStatus.CREATED,
                    data={
                        "access_token": self._static_access_token
                        or secrets.token_hex(12),
                        "refresh_token": self._static_refresh_token
                        or secrets.token_hex(12),
                        "expires_in": 3600,
                    },
                )
            case _:
                raise RuntimeError(f"Received unrecognized endpoint {url}")


@dataclasses.dataclass
class _MockResponse:
    status_code: HTTPStatus = HTTPStatus.OK
    data: dict | None

    def json(self):
        return self.data


# TODO: use this more often in tests
def jsonapi_ref(obj) -> dict:
    """return a jsonapi resource reference (as json-serializable dict)"""
    return {
        "type": get_resource_type_from_model(obj.__class__),
        "id": obj.pk,
    }


def get_test_request(user=None, method="get", path="", cookies=None):
    _factory_method = getattr(APIRequestFactory(), method)
    _request = _factory_method(path)  # note that path is optional for view tests
    _request.session = SessionStore()  # Add cookies if provided
    if cookies:
        for name, value in cookies.items():
            _request.COOKIES[name] = value
    return _request
