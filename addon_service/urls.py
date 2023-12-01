from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_json_api.utils import get_resource_type_from_serializer

from addon_service import views


def _urls_for_viewset(viewset, *, relationship_view=None):
    """returns urlpatterns for a viewset that corresponds to a resource type

    includes patterns for jsonapi-style relationships
    """
    _resource_name = get_resource_type_from_serializer(viewset.serializer_class)
    _router = SimpleRouter()
    _router.register(
        prefix=_resource_name,
        viewset=viewset,
        basename=_resource_name,
    )
    _urlpatterns = [*_router.urls]
    # add route for all relationship "related" links
    # https://django-rest-framework-json-api.readthedocs.io/en/stable/usage.html#related-urls
    _urlpatterns.append(
        path(
            f"{_resource_name}/<pk>/<related_field>/",
            viewset.as_view({"get": "retrieve_related"}),
            name=f"{_resource_name}-related",
        ),
    )
    if relationship_view is not None:
        # add route for all relationship "self" links
        # https://django-rest-framework-json-api.readthedocs.io/en/stable/usage.html#relationshipview
        _urlpatterns.append(
            path(
                f"{_resource_name}/<pk>/relationships/<related_field>/",
                relationship_view.as_view(),
                name=f"{_resource_name}-relationships",
            ),
        )
    return _urlpatterns


# NOTE: assumes each viewset corresponds to a distinct resource_name
urlpatterns = [
    *_urls_for_viewset(
        views.AuthorizedStorageAccountViewSet,
        relationship_view=views.AuthorizedStorageAccountRelationshipView,
    ),
    *_urls_for_viewset(
        views.ConfiguredStorageAddonViewSet,
        relationship_view=views.ConfiguredStorageAddonRelationshipView,
    ),
    *_urls_for_viewset(
        views.ExternalStorageServiceViewSet,
        relationship_view=views.ExternalStorageServiceRelationshipView,
    ),
    *_urls_for_viewset(
        views.InternalResourceViewSet,
        relationship_view=views.InternalResourceRelationshipView,
    ),
    *_urls_for_viewset(
        views.InternalUserViewSet,
        relationship_view=views.InternalUserRelationshipView,
    ),
]
