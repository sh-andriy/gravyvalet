from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_json_api.utils import get_resource_type_from_serializer

from addon_service import views


def _urls_for_viewsets(*viewsets):
    """returns urlpatterns for viewsets that each correspond to a resource type

    includes patterns for jsonapi-style relationships
    """
    _router = SimpleRouter()
    _additional_urlpatterns = []
    for _viewset in viewsets:
        # NOTE: assumes each viewset corresponds to a distinct resource_name
        _resource_name = get_resource_type_from_serializer(_viewset.serializer_class)
        _router.register(
            prefix=_resource_name,
            viewset=_viewset,
            basename=_resource_name,
        )
        # add route for all relationship "related" links
        # https://django-rest-framework-json-api.readthedocs.io/en/stable/usage.html#related-urls
        _additional_urlpatterns.append(
            path(
                f"{_resource_name}/<pk>/<related_field>/",
                _viewset.as_view({"get": "retrieve_related"}),
                name=f"{_resource_name}-related",
            ),
        )
    return [
        *_router.urls,
        *_additional_urlpatterns,
    ]


urlpatterns = _urls_for_viewsets(
    views.AuthorizedStorageAccountViewSet,
    views.ConfiguredStorageAddonViewSet,
    views.ExternalStorageServiceViewSet,
    views.InternalResourceViewSet,
    views.InternalUserViewSet,
)
