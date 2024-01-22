from rest_framework.test import (
    APIRequestFactory,
    force_authenticate,
)


def get_test_request(user=None, method="get", path=""):
    _factory_method = getattr(APIRequestFactory(), method)
    _request = _factory_method(path)  # note that path is optional for view tests
    if user is not None:
        force_authenticate(_request, user=user)
    return _request
