from collections import defaultdict
from functools import (
    partial,
    wraps,
)
from http import HTTPStatus
from unittest.mock import patch

import httpx
from django.contrib.sessions.backends.db import SessionStore
from rest_framework import exceptions as drf_exceptions
from rest_framework.test import APIRequestFactory

from app import settings


def get_test_request(user=None, method="get", path="", cookies=None):
    _factory_method = getattr(APIRequestFactory(), method)
    _request = _factory_method(path)  # note that path is optional for view tests
    _request.session = SessionStore()  # Add cookies if provided
    if cookies:
        for name, value in cookies.items():
            _request.COOKIES[name] = value
    return _request


class MockOSF:
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
        self._permissions = defaultdict(lambda: defaultdict(dict))
        if permissions:
            self._permissions.update(permissions)
        self._configured_caller_uri = None
        self._mock_auth_request = patch(
            "app.authentication.make_auth_request", side_effect=self._mock_user_check
        )
        self._mock_resource_check = patch(
            "addon_service.common.permissions.authenticate_resource",
            side_effect=self._mock_resource_check,
        )
        self._mock_auth_request.start()
        self._mock_resource_check.start()

    def stop(self):
        self._mock_auth_request.stop()
        self._mock_resource_check.stop()

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
        role = self._permissions[resource_uri][user_uri]
        if role == "read":
            return ["read"]
        if role == "write":
            return ["read", "write"]
        if role == "admin":
            return ["read", "write", "admin"]
        if self._permissions[resource_uri]["public"]:
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


def with_mocked_httpx_get(response_status=HTTPStatus.OK, user_uri=None):
    def decorator(func):
        @wraps(func)
        def wrapper(testcase, *args, **kwargs):
            mock_side_effect = partial(
                _mock_httpx_response,
                response_status=response_status,
                user_uri=user_uri or testcase._user.user_uri,
            )
            patcher = patch("httpx.Client.get", side_effect=mock_side_effect)
            patcher.start()
            test_result = func(testcase, *args, **kwargs)
            patcher.stop()
            return test_result

        return wrapper

    return decorator


def _mock_httpx_response(response_status, user_uri, url, *args, **kwargs):
    """Generates mock httpx.Response based on the requested URL and response status."""
    if not response_status.is_success:
        return httpx.Response(status_code=response_status)

    if url == settings.USER_REFERENCE_LOOKUP_URL:
        payload = {"data": {"links": {"iri": user_uri}}}
    else:
        guid = url.rstrip("/").split("/")[-1]
        payload = {
            "data": {
                "attributes": {"current_user_permissions": ["read", "write", "admin"]},
                "links": {"iri": f"{settings.URI_ID}{guid}"},
            }
        }
    return httpx.Response(status_code=response_status, json=payload)
